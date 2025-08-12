from django.db import models

# Create your models here.

from django.db import models


class Projeto(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Unidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='unidades')

    def __str__(self):
        return self.nome

class Suprimento(models.Model):
    nome = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nome} ({self.quantidade})"

class EntregaSuprimento(models.Model):
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='entregas')
    suprimento = models.ForeignKey(Suprimento, on_delete=models.CASCADE, related_name='entregas')
    quantidade_entregue = models.PositiveIntegerField()
    data = models.DateField()
    setor = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.unidade.nome} - {self.suprimento.nome} - {self.quantidade_entregue} - {self.data}"

class Equipamento(models.Model):
    NOME_CHOICES = [
        ('impressora', 'Impressora'),
        ('tv', 'TV'),
        ('outro', 'Outro'),
    ]

    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.CASCADE,
        related_name='equipamentos'
    )
    nome = models.CharField(max_length=50, choices=NOME_CHOICES, default='impressora')
    tipo = models.CharField(max_length=100, blank=True)  # campo editável, opcional
    patrimonio = models.CharField(max_length=50, unique=True)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)

    def __str__(self):
        tipo_exibido = self.tipo if self.tipo else self.get_nome_display()
        return f"{self.patrimonio} - {self.marca} {self.modelo} ({tipo_exibido})"

class Maquina(models.Model):
    unidade_associada = models.ForeignKey('Unidade',on_delete=models.SET_NULL,blank=True,null=True,related_name='maquinas_associadas')
    nome = models.CharField(max_length=200)
    tag = models.CharField(max_length=100, blank=True, null=True)
    sistema_operacional = models.CharField(max_length=200, blank=True, null=True)
    processador = models.CharField(max_length=200, blank=True, null=True)
    memoria_total = models.FloatField(blank=True, null=True)  # GB
    placa_mae = models.CharField(max_length=200, blank=True, null=True)
    fabricante_placa_mae = models.CharField(max_length=200, blank=True, null=True)
    disco = models.CharField(max_length=200, blank=True, null=True)
    tamanho_disco = models.FloatField(blank=True, null=True)  # GB
    fornecedor_associado = models.CharField(max_length=50,blank=True,null=True)
    tempo_off_dias = models.IntegerField(default=0)
    tempo_off_horas = models.IntegerField(default=0)
    tempo_off_minutos = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=[('ON', 'ON'), ('OFF', 'OFF')])

    def __str__(self):
        return f"{self.nome} ({self.status})"

class UnidadeAssociacao(models.Model):
    prefixo_nome = models.CharField(max_length=200, unique=True, help_text="Prefixo do nome da máquina para associar")
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='associacoes')

    def __str__(self):
        return f"{self.prefixo_nome} -> {self.unidade.nome}"

class ModeloFornecedor(models.Model):

    FORNECEDOR_CHOICES = [
        ('ECO', 'ECO'),
        ('DISTRICOMP', 'DISTRICOMP'),
    ]
    modelo = models.CharField(max_length=100)  # nome do modelo 
    fornecedor = models.CharField(max_length=50, choices=FORNECEDOR_CHOICES)

    class Meta:
        unique_together = ('modelo', 'fornecedor')  # modelo+fornecedor únicos
