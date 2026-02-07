from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    population = models.IntegerField()
    current_complaints = models.IntegerField()
    historical_avg = models.IntegerField(help_text="Historical trend for early warning")
    
    # Computed fields logic handled in analytics pipeline
    
    def __str__(self):
        return self.name
class UploadedDataset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)

    # Optional: store threshold used for analysis
    silence_threshold = models.FloatField(default=0.5)

    def __str__(self):
        return f"{self.original_filename} ({self.created_at:%Y-%m-%d %H:%M})"


class ComplaintRecord(models.Model):
    dataset = models.ForeignKey(UploadedDataset, on_delete=models.CASCADE, related_name="records")

    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    population = models.IntegerField()
    complaints = models.IntegerField()
    history_avg = models.IntegerField()

    # Optional computed fields (helps auditing / later dashboards)
    density = models.FloatField(null=True, blank=True)
    density_z = models.FloatField(null=True, blank=True)
    is_silent = models.BooleanField(default=False)
    trend_gap = models.FloatField(null=True, blank=True)
    fear_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.region} - {self.district}"