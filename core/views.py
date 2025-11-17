from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    """Simple index view."""
    return HttpResponse("Welcome to AutoPhone Django Project!")
