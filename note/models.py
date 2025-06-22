from django.db import models
import uuid
from django.contrib.auth.models import User

class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    content = models.TextField()
    Category = models.CharField(max_length=100, default='General')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # This should automatically update

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            id = str(uuid.uuid4())
            self.slug = self.title + id
        super(Notes, self).save(*args, **kwargs)
