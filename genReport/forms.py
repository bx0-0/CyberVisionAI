from django import forms
from .models import Report

class GenReportForm(forms.ModelForm):
    OPTION_CHOICES = [
        ('X', 'X - More accurate and comprehensive'),
        ('X-mini', 'X-mini - Faster')
    ]

    choice_model = forms.ChoiceField(
        choices=OPTION_CHOICES,
        help_text=(
            "Choose the model:\n"
            "- If you select 'X', the full model will generate and rewrite the report completely with higher accuracy, though it will be a bit slower.\n"
            "- If you select 'X-mini', it will avoid the delay, keeping the POC and Step_to_reproduce sections as you entered them, and will complete the rest of the report."
        )
    )

    class Meta:
        model = Report
        fields = ('bug_name', 'asset', 'step_to_reproduce', 'POC', 'severity', 'choice_model')


class EditReport(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('report_file',)
