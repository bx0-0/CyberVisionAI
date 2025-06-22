from django import forms
from django.core.exceptions import ValidationError
import os

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in ['.pdf']:
        raise ValidationError('Unsupported file extension.')

def validate_file_size(value):
    limit = 30 * 1024 * 1024  # 10 MB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 10 MB.')

class UploadFileForm(forms.Form):
    file = forms.FileField(
        allow_empty_file=False,
        required=True,
        error_messages={'required': 'Please upload a file'},
        label='File',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        validators=[validate_file_extension, validate_file_size]
    )
    
    class Meta:
        fields = ['file']