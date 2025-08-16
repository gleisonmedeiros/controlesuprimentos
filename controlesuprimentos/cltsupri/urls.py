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
    path('total_unidade/', views.total_unidade, name='total_unidade'),
    path('pesquisa_suprimento/', views.pesquisa_suprimento, name='pesquisa_suprimento'),
    path('pesquisa_unidade/', views.pesquisa_unidade, name='pesquisa_unidade'),
    path('pesquisa_entrega/', views.pesquisa_entrega, name='pesquisa_entrega'),
    path('inventario/', views.inventario, name='inventario'),
    path('equipamentos/', views.cadastro_equipamento, name='cadastro_equipamento'),
    path('associar-unidade/', views.associar_unidade, name='associar_unidade'),
    path('modelo-fornecedor/', views.modelo_fornecedor_create, name='modelo-fornecedor-create'),
    path('maquinas-equipamentos/', views.maquinas_equipamentos_por_unidade, name='maquinas_equipamentos'),
    path('equipamentos/<int:equipamento_id>/', views.cadastro_equipamento, name='cadastro_equipamento_editar'),
    path('maquinas-equipamentos/', views.maquinas_equipamentos_por_unidade, name='maquinas_equipamentos_por_unidade'),
    path('maquina/<int:pk>/deletar/', views.deletar_maquina, name='deletar_maquina'),
    path('equipamentos/<int:pk>/', views.cadastro_equipamento, name='editar_equipamento'),
    path('equipamento/<int:pk>/deletar/', views.deletar_equipamento, name='deletar_equipamento'),
    path('apagar-todas-maquinas/', views.apagar_todas_maquinas, name='apagar_todas_maquinas'),

]