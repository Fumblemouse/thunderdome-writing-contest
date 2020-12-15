"""views for baseapp"""
from django.shortcuts import render

# Create your views here.
def home(request):
    """Homepage"""
    return render(request, 'baseapp/home.html', {})
