from django import template
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template import loader

# Create your views here.

def dashboard_view(request):
    template = loader.get_template('dashboard/index.html')
    return HttpResponse(template.render({}, request))
