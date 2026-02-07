from rest_framework import serializers
from django.core.exceptions import ValidationError
import pandas as pd

class CSVUploadSerializer(serializers.Serializer):
    """
    Serializer for CSV file upload with validation
    """
    file = serializers.FileField(
        required=True,
        help_text="CSV file containing complaint data"
    )
    silence_threshold = serializers.FloatField(
        required=False,
        default=0.5,
        min_value=0.0,
        max_value=1.0,
        help_text="Threshold ratio for silence detection (0.0 - 1.0)"
    )

    def validate_file(self, value):
        """
        Validate that the uploaded file is a CSV with proper structure
        """
        # Check file extension
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError(
                "Invalid file type. Only CSV files are accepted."
            )
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size exceeds 10MB limit."
            )
        
        # Validate CSV structure
        try:
            # Read first few rows to validate structure
            df = pd.read_csv(value, nrows=5)
            
            # Required columns from your ingestion module
            required_cols = {"region", "district", "population", "complaints", "history_avg"}
            missing_cols = required_cols - set(df.columns)
            
            if missing_cols:
                raise serializers.ValidationError(
                    f"CSV missing required columns: {sorted(missing_cols)}. "
                    f"Required: {sorted(required_cols)}"
                )
            
            # Reset file pointer for later reading
            value.seek(0)
            
        except pd.errors.EmptyDataError:
            raise serializers.ValidationError("CSV file is empty.")
        except pd.errors.ParserError as e:
            raise serializers.ValidationError(f"CSV parsing error: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"File validation error: {str(e)}")
        
        return value
