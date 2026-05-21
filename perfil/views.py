from typing import Any

from django.shortcuts import render
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpRequest, HttpResponse

from . import models
from . import forms

# Create your views here.

class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.contexto = {
            'userform': forms.UserForm(data=self.request.POST or None),
            'perfilform': forms.PerfilForm(data=self.request.POST or None),
        }

        self.renderizar = render(self.request, self.template_name, self.contexto)

    def get(self, *args, **kwarks):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        return self.renderizar
    
class Atualizar(View):
    def get(self, *args, **kwarks):
        return HttpResponse("Atualizar")
    
class Login(View):
    def get(self, *args, **kwarks):
        return HttpResponse("Login")
    
class Logout(View):
    def get(self, *args, **kwarks):
        return HttpResponse("Logout")