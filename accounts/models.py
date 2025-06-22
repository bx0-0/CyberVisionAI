import os
from uuid import uuid4
import uuid
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField  # type: ignore

# Create your models here.


def GetImageUploadTo(instance, ImageName):
    name, ext = os.path.splitext(ImageName)
    id = uuid4()
    return f"profile/{id}{ext}"


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile', db_index=True)
    Country = CountryField(blank_label="(select country)")
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ProfileImg = models.ImageField(upload_to=GetImageUploadTo, null=True, blank=True)
    
    def __str__(self) -> str:
        return self.user.username

    def save(self, *args, **kwargs):
        if self.pk and self.ProfileImg:
            try:
                old_img = Profile.objects.get(pk=self.pk).ProfileImg
            except Profile.DoesNotExist:
                old_img = None

            if old_img and old_img != self.ProfileImg:
                if os.path.isfile(old_img.path):
                    os.remove(old_img.path)

        return super().save(*args, **kwargs)

