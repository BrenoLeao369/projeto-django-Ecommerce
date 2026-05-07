from django.shortcuts import render
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse

# Create your views here.
class Criar (View):
    def get(self, *args, **kwarks):
        return HttpResponse("Criar")
    
class Atualizar (View):
    def get(self, *args, **kwarks):
        return HttpResponse("Atualizar")
    
class Login (View):
    def get(self, *args, **kwarks):
        return HttpResponse("Login")
    
class Logout (View):
    def get(self, *args, **kwarks):
        return HttpResponse("Logout")