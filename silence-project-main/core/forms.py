from django import forms

class AnalysisForm(forms.Form):
    # The file input
    dataset = forms.FileField(
        label="Upload Complaint Dataset (CSV)",
        required=True
    )
    
    # The threshold input (Optional)
    silence_threshold = forms.FloatField(
        required=False,
        initial=0.5,
        widget=forms.HiddenInput()
    )

class CSVUploadForm(forms.Form):
    dataset = forms.FileField(
        label="Select CSV",
        widget=forms.ClearableFileInput(attrs={'id': 'id_dataset', 'accept': '.csv'})
    )