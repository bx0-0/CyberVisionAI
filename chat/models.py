import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils.text import slugify

class Token(models.Model):
    token = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expiration = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expiration

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set expiration if new token
            self.expiration = timezone.now() + timedelta(minutes=4)
        super().save(*args, **kwargs)

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.CharField(max_length=255)
    created_at_in_DB = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, unique=True)
    

    def __str__(self):
        return f"Conversation {self.id} with {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(uuid.uuid4().hex)
        super().save(*args, **kwargs)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=255)  
    content = models.TextField()

    
    def __str__(self):
        return f"Message {self.id} in {self.conversation.id} by {self.role}"
    

class MindMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True)
    def __str__(self):
        return f"MindMap {self.id} with {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(uuid.uuid4().hex)
        super().save(*args, **kwargs)