from typing import Any
from django.db.models.base import Model as Model
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .models import Profile
from .forms import ProfileForm, SingUpForm, UserForm
from django.views.generic import TemplateView
from django.db import transaction


class SignUpView(CreateView):
    form_class = SingUpForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    
    @transaction.atomic
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        if self.object:  # this is the User instance
           profile =  Profile.objects.create(user=self.object)
           profile.Country = form.cleaned_data.get('country')
           profile.save()
           
        return response



class ShowProfileView(TemplateView):
    template_name = "registration/profile.html"
    
    def get_context_data(self, **kwargs:Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(user = self.request.user)
        context["profile"] = profile
        return context
    

class ProfileUpdateView(UpdateView):
    template_name = "registration/edit_profile.html"
    form_class = ProfileForm
    success_url = '../profile/'
    def get_object(self, queryset=None):
        obj = Profile.objects.get(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        user_form = UserForm(self.request.POST, instance=self.request.user)
        if user_form.is_valid():
            user_form.save()
        return super().form_valid(form)