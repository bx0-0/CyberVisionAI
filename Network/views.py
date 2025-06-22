from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def network_view(request):
    return render(request, 'Network/network.html')
