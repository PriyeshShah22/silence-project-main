from django.contrib import admin
from .models import UploadedDataset, ComplaintRecord

@admin.register(UploadedDataset)
class UploadedDatasetAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'created_at', 'silence_threshold')

@admin.register(ComplaintRecord)
class ComplaintRecordAdmin(admin.ModelAdmin):
    list_display = ('region', 'district', 'complaints', 'is_silent')
    list_filter = ('dataset', 'region')