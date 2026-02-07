from django.urls import path
from .api_views import CSVUploadAPIView, DatasetListAPIView, DatasetDetailAPIView
from . import views

urlpatterns = [
    # Existing web views
    path('', views.index_view, name='index'),
    path('about/', views.about_view, name='about'),
    path('working/', views.working_view, name='working'),
    path('upload/', views.upload_view, name='upload'),
    path('results/', views.results_view, name='results'),
    
    # API endpoints
    path('api/upload-csv/', CSVUploadAPIView.as_view(), name='api-upload-csv'),
    path('api/datasets/', DatasetListAPIView.as_view(), name='api-datasets-list'),
    path('api/datasets/<int:dataset_id>/', DatasetDetailAPIView.as_view(), name='api-dataset-detail'),
]
