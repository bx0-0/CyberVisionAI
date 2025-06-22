from django.db import models
from django.contrib.auth.models import User
from  uuid import uuid4

class VulnerabilityGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=True, null=True)
    chart_folder = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"Group {self.id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid4()
        super().save(*args, **kwargs)

class Vulnerability(models.Model):
    group = models.ForeignKey(VulnerabilityGroup, on_delete=models.CASCADE, related_name='vulnerabilities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vulnerability_type = models.CharField(max_length=100)
    count = models.IntegerField()
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)

    def __str__(self):
        return f"{self.vulnerability_type} ({self.severity}) ({self.group})"

    class Meta:
        verbose_name_plural = 'Vulnerabilities'
        ordering = ['-count']
