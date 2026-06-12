from typing import Any, Mapping

from django.contrib.auth.models import User
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from . import models


class PerfilForm(forms.ModelForm):
    data_de_nascimento = forms.DateField(
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        ),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
    )

    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)



class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label='senha'
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label='comfirmação senha'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password'
                  , 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msg = {}

        usuario_data = cleaned.get('username')
        email_data = cleaned.get('email')
        password_data = cleaned.get('password')
        password2_data = cleaned.get('password2')

        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_user_exists = "Usúario ja existe"
        error_msg_email_exists = "E-mail ja conectado a uma conta"
        error_msg_password_match = "as duas senhas não conferem"
        error_msg_password_short = "sua senha precisa de no minimo 6 carateres"
        error_msg_required_field = 'esse campo é obrigatorio'
        

        #usuario logado: atualização
        if self.usuario:
            if usuario_db:
                if usuario_data != usuario_db.username:
                    validation_error_msg['username'] = error_msg_user_exists
                        
            if email_db:
                if email_data != email_db.email:
                    validation_error_msg['email'] = error_msg_email_exists
                    
            if password_data != password2_data:
                validation_error_msg['password'] = error_msg_password_match
                validation_error_msg['password2'] = error_msg_password_match

            if password_data and len(password_data) < 6:
                validation_error_msg['password'] = error_msg_password_short

        # usuario não logado: cadastro
        else:
            if usuario_db:
                validation_error_msg['username'] = error_msg_user_exists
                        
            if email_db:
                validation_error_msg['email'] = error_msg_email_exists
                    
            if not password_data:
                validation_error_msg['password'] = error_msg_required_field

            if not password2_data:
                validation_error_msg['password2'] = error_msg_required_field

            if password_data != password2_data:
                validation_error_msg['password'] = error_msg_password_match
                validation_error_msg['password2'] = error_msg_password_match

            if password_data and len(password_data) < 6:
                    validation_error_msg['password'] = error_msg_password_short
        if validation_error_msg:
            raise forms.ValidationError(validation_error_msg)