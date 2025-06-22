from django.contrib import admin
from .models import Vulnerability,VulnerabilityGroup
# Register your models here.

admin.site.register(Vulnerability)
admin.site.register(VulnerabilityGroup)