from django import forms
from .models import Vulnerability
from django.core.exceptions import ValidationError

class VulnerabilityForm(forms.ModelForm):
    class Meta:
        model = Vulnerability
        fields = ['vulnerability_type', 'count', 'severity']

#create form for excel upload

class UploadFileForm(forms.Form):
    file = forms.FileField()

    ALLOWED_EXTENSIONS = ['.xlsx', '.xls']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Get the file name
            file_name = file.name
            
            # Find the first occurrence of '.'
            dot_index = file_name.find('.')
            
            # If there is no '.' or '.' is at the beginning, raise an error
            if dot_index == -1 or dot_index == 0:
                raise ValidationError('Invalid file name. File must have an extension.')

            # Extract the extension after the first '.'
            extension = file_name[dot_index:].lower()

            # Check if the file extension is allowed
            if extension not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(f'Unsupported file extension. Allowed extensions are: {", ".join(self.ALLOWED_EXTENSIONS)}.')

        return file
