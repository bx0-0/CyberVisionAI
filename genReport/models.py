from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from  uuid import uuid4
# Create your models here.

class Report(models.Model):
    """Model definition for Report."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug =  models.SlugField(null=True, blank=True) 
    bug_name = models.CharField(max_length=200)
    asset = models.CharField(max_length = 150)
    step_to_reproduce = models.TextField(
        max_length=500,
        help_text=(
            'Please enter the steps exactly as you would like them to appear in the report. '
            'The system will not modify these steps, so write them clearly.'
        )
    )
    
    POC = models.TextField(
        max_length=500,
        help_text=(
            'Please enter the Proof of Concept (POC) exactly as you would like it to appear in the report. '
            'The system will not modify this field.'
        )
    )
    report_file = models.TextField()
    create_at = models.DateField(auto_now_add=True)    
    severity_option = [
        ('Low','Low'),
        ('High', 'High'),
        ('Medium','Medium'),
        ('critical', 'critical')    
    
    ]

    severity = models.CharField(max_length = 150, choices=severity_option,default='Low')
     
    def save(self): 
       id=uuid4()
       if not self.slug :
           self.slug = slugify((self.bug_name)+'-'+str(id)) 
        
       super().save() 

    def __str__(self):
        """Unicode representation of Report."""
        return str(self.bug_name)+'/created at/'+str(self.create_at)
