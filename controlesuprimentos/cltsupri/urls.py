from django.urls import path
from . import views

urlpatterns = [
    path('index/',views.index, name='index'),
    path('unidade/', views.criar_unidade, name='criar_unidade'),
    path('suprimento/', views.criar_suprimento, name='criar_suprimento'),
    path('projeto/', views.criar_projeto, name='criar_projeto'),
    path('', views.index, name='index'),
    path('entrega_suprimento/', views.entrega_suprimento, name='entrega_suprimento'),
    path('processar-selecao/', views.processar_selecao, name='processar_selecao'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),

]