from django.contrib import admin
from .models import Projeto, Unidade, Suprimento, EntregaSuprimento

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')  # Mostra ID e nome no admin
    search_fields = ('nome',)  # Permite buscar pelo nome

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'projeto')  # Mostra ID, nome e projeto
    list_filter = ('projeto',)  # Adiciona filtro por projeto
    search_fields = ('nome', 'projeto__nome')  # Permite buscar pelo nome da unidade ou do projeto

@admin.register(Suprimento)
class SuprimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'quantidade')  # Mostra ID, nome e quantidade
    search_fields = ('nome',)  # Permite buscar pelo nome

@admin.register(EntregaSuprimento)
class EntregaSuprimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'unidade', 'suprimento', 'quantidade_entregue', 'data', 'setor')
    list_filter = ('unidade__projeto', 'unidade', 'data', 'setor')  # Filtra por projeto, unidade, data, setor
    search_fields = ('unidade__nome', 'suprimento__nome', 'setor')  # Busca por nome da unidade, suprimento ou setor
    date_hierarchy = 'data'  # Adiciona navegação hierárquica por data