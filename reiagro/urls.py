"""
URL configuration for reiagro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views  # Importa suas views da pasta core
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.frente_caixa, name='home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('consulta/', views.consulta, name='consulta'),
    path('fechamento/', views.fechamento, name='fechamento'),
]


def index(request):
    return render(request, 'paginas/index.html')


def cadastro(request):
    return render(request, 'paginas/cadastro.html')


def consulta(request):
    return render(request, 'paginas/consulta.html')


def fechamento(request):
    return render(request, 'paginas/fechamento.html')
