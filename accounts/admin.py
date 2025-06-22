from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  
            return ('api_key',)  
        return ()

admin.site.register(Profile, ProfileAdmin)
