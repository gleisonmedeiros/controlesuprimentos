from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Login / Logout
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('unidade/', views.criar_unidade, name='criar_unidade'),
    path('unidade/<int:unidade_id>/', views.criar_unidade, name='criar_unidade_editar'),
    path('suprimento/', views.criar_suprimento, name='criar_suprimento'),
    path('suprimento/<int:suprimento_id>/', views.criar_suprimento, name='criar_suprimento_editar'),
    path('projeto/', views.criar_projeto, name='criar_projeto'),
    path('projeto/<int:projeto_id>/', views.criar_projeto, name='criar_projeto_editar'),
    path('', views.index, name='index'),
    path('entrega_suprimento/', views.entrega_suprimento, name='entrega_suprimento'),
    #path('processar-selecao/', views.processar_selecao, name='processar_selecao'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('total_unidade/', views.total_unidade, name='total_unidade'),
    path('pesquisa_entrega/', views.pesquisa_entrega, name='pesquisa_entrega'),
    path('relatorio-toners/', views.relatorio_toners, name='relatorio_toners'),
    #path('relatorio-toners/pdf/', views.relatorio_toners_pdf, name='relatorio_toners_pdf'),
    path('inventario/', views.inventario, name='inventario'),
    path('equipamentos/', views.cadastro_equipamento, name='cadastro_equipamento'),
    path('associar_unidade/', views.associar_unidade_manage, name='associar_unidade'),
    path('associar_unidade/<int:pk>/<str:action>/', views.associar_unidade_manage, name='associar-unidade-action'),
    path('modelo-fornecedor/', views.modelo_fornecedor_manage, name='modelo-fornecedor-create'),
    path('maquinas-equipamentos/', views.maquinas_equipamentos_por_unidade, name='maquinas_equipamentos'),
    path('equipamentos/<int:equipamento_id>/', views.cadastro_equipamento, name='cadastro_equipamento_editar'),
    path('maquinas-equipamentos/', views.maquinas_equipamentos_por_unidade, name='maquinas_equipamentos_por_unidade'),
    path('maquina/<int:pk>/deletar/', views.deletar_maquina, name='deletar_maquina'),
    path('equipamentos/<int:pk>/', views.cadastro_equipamento, name='editar_equipamento'),
    path('equipamento/<int:pk>/deletar/', views.deletar_equipamento, name='deletar_equipamento'),
    path('apagar-todas-maquinas/', views.apagar_todas_maquinas, name='apagar_todas_maquinas'),
    path('modelo-fornecedor/', views.modelo_fornecedor_manage, name='modelo-fornecedor-manage'),
    path('modelo-fornecedor/edit/<int:pk>/', views.modelo_fornecedor_manage, {'action': 'edit'},
         name='modelo-fornecedor-edit'),
    path('modelo-fornecedor/delete/<int:pk>/', views.modelo_fornecedor_manage, {'action': 'delete'},
         name='modelo-fornecedor-delete'),
    path("maquinas/exportar/", views.exportar_maquinas_excel, name="exportar_maquinas_excel"),
    path('quantidade-maquina-por-unidade/', views.relatorio_maquinas_por_projeto, name='quantidade_maquina_por_unidade'),
    path('consolidado_maquinas/', views.consolidado_maquinas, name='consolidado_maquinas'),
    path('equipamento/', views.cadastrar_equipamento, name='cadastrar_equipamento'),
    path('equipamento/<int:equipamento_id>/', views.cadastrar_equipamento, name='cadastrar_equipamento_editar'),
    path('consolidado-equipamentos/', views.consolidado_equipamentos, name='consolidado_equipamentos'),
]