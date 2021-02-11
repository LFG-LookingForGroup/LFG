from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path

def index(request):
  return HttpResponse(Path("public_html/index.html").read_text())

