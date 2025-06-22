from django.urls import path
from .views import SignUpView , ShowProfileView, ProfileUpdateView


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path('profile/', ShowProfileView.as_view(), name='profile'),
    path('edit-profile/', ProfileUpdateView.as_view(), name='edit-profile')
]