from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt  # Add this
from django.utils.decorators import method_decorator  # Add this
from django.db import transaction
from .serializers import CSVUploadSerializer
from .ingestion import ingest_csv_to_db
from .models import UploadedDataset, ComplaintRecord
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')  # Add this decorator
class CSVUploadAPIView(APIView):
    """
    API endpoint for CSV data ingestion
    
    POST /api/upload-csv
    - Accepts CSV file via multipart/form-data
    - Validates file structure
    - Persists data to database
    - Returns dataset summary
    """
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        # ... rest of your code remains the same
        serializer = CSVUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = serializer.validated_data['file']
        threshold = serializer.validated_data.get('silence_threshold', 0.5)
        
        try:
            with transaction.atomic():
                dataset = ingest_csv_to_db(csv_file, threshold)
                record_count = ComplaintRecord.objects.filter(dataset=dataset).count()
                
                logger.info(
                    f"Successfully ingested CSV: {dataset.original_filename} "
                    f"with {record_count} records"
                )
                
                response_data = {
                    "success": True,
                    "message": "CSV data successfully ingested",
                    "dataset": {
                        "id": dataset.id,
                        "filename": dataset.original_filename,
                        "created_at": dataset.created_at.isoformat(),
                        "silence_threshold": dataset.silence_threshold,
                        "record_count": record_count
                    },
                    "statistics": self._calculate_statistics(dataset)
                }
                
                return Response(
                    response_data,
                    status=status.HTTP_201_CREATED
                )
        
        except ValueError as ve:
            logger.error(f"Validation error during CSV ingestion: {str(ve)}")
            return Response(
                {
                    "success": False,
                    "error": "Data validation failed",
                    "details": str(ve)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.exception(f"Unexpected error during CSV ingestion: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": "Internal server error",
                    "details": str(e)  # Changed to show actual error
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_statistics(self, dataset):
        """Calculate basic statistics for the uploaded dataset"""
        records = ComplaintRecord.objects.filter(dataset=dataset)
        
        if not records.exists():
            return {}
        
        import pandas as pd
        
        data = list(records.values(
            'region', 'district', 'population', 'complaints', 'history_avg'
        ))
        df = pd.DataFrame(data)
        
        return {
            "total_records": len(df),
            "unique_regions": df['region'].nunique(),
            "unique_districts": df['district'].nunique(),
            "total_population": int(df['population'].sum()),
            "total_complaints": int(df['complaints'].sum()),
            "avg_complaints_per_region": round(df['complaints'].mean(), 2),
            "complaint_density_per_1000": round(
                (df['complaints'].sum() / df['population'].sum()) * 1000, 2
            )
        }


@method_decorator(csrf_exempt, name='dispatch')  # Add this too
class DatasetListAPIView(APIView):
    """GET /api/datasets - Returns list of all uploaded datasets"""
    def get(self, request):
        datasets = UploadedDataset.objects.all().order_by('-created_at')
        
        data = [{
            "id": ds.id,
            "filename": ds.original_filename,
            "created_at": ds.created_at.isoformat(),
            "silence_threshold": ds.silence_threshold,
            "record_count": ds.records.count()
        } for ds in datasets]
        
        return Response({
            "success": True,
            "count": len(data),
            "datasets": data
        })


@method_decorator(csrf_exempt, name='dispatch')  # Add this too
class DatasetDetailAPIView(APIView):
    """GET /api/datasets/{id} - Returns details of a specific dataset"""
    def get(self, request, dataset_id):
        try:
            dataset = UploadedDataset.objects.get(id=dataset_id)
            records = ComplaintRecord.objects.filter(dataset=dataset)
            
            return Response({
                "success": True,
                "dataset": {
                    "id": dataset.id,
                    "filename": dataset.original_filename,
                    "created_at": dataset.created_at.isoformat(),
                    "silence_threshold": dataset.silence_threshold,
                },
                "records": [{
                    "region": r.region,
                    "district": r.district,
                    "population": r.population,
                    "complaints": r.complaints,
                    "history_avg": r.history_avg,
                    "density": r.density,
                    "is_silent": r.is_silent,
                    "fear_score": r.fear_score
                } for r in records]
            })
        
        except UploadedDataset.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": "Dataset not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
