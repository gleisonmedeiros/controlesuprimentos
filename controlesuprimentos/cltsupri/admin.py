from django.contrib import admin
from .models import Projeto, Unidade, Suprimento, EntregaSuprimento, Equipamento, Maquina,ModeloFornecedor

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)

@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'projeto')
    list_filter = ('projeto',)
    search_fields = ('nome', 'projeto__nome')

@admin.register(Suprimento)
class SuprimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'quantidade')
    search_fields = ('nome',)

@admin.register(EntregaSuprimento)
class EntregaSuprimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'unidade', 'suprimento', 'quantidade_entregue', 'data', 'setor')
    list_filter = ('unidade__projeto', 'unidade', 'data', 'setor')
    search_fields = ('unidade__nome', 'suprimento__nome', 'setor')
    date_hierarchy = 'data'

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'patrimonio', 'nome', 'marca', 'modelo', 'tipo', 'unidade')
    list_filter = ('nome', 'tipo', 'unidade__projeto', 'unidade')
    search_fields = ('patrimonio', 'marca', 'modelo', 'unidade__nome', 'unidade__projeto__nome')
    ordering = ('unidade__projeto__nome', 'unidade__nome', 'patrimonio')

@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nome', 'tag', 'sistema_operacional', 'processador', 'memoria_total',
        'placa_mae', 'fabricante_placa_mae', 'disco', 'tamanho_disco',
        'tempo_off_dias', 'tempo_off_horas', 'tempo_off_minutos', 'status'
    )
    list_filter = ('status', 'sistema_operacional', 'fabricante_placa_mae')
    search_fields = ('nome', 'tag', 'processador', 'placa_mae', 'disco')
    ordering = ('status', 'nome')

@admin.register(ModeloFornecedor)
class ModeloFornecedorAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'fornecedor')
    search_fields = ('modelo',)
    list_filter = ('fornecedor',)
    ordering = ('modelo',)