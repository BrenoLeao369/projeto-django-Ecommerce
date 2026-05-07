from django.shortcuts import render
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponse
# Create your views here.

class Pagar (View):
    def get(self, *args, **kwarks):
        return HttpResponse('Pagar')

class FecharPedido (View):
    def get(self, *args, **kwarks):
        return HttpResponse("FecharPedido")

class Detalhes (View):
    def get(self, *args, **kwarks):
        return HttpResponse("Detalhes")