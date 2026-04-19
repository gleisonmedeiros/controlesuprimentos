from django.db import models

# Create your models here.

from django.db import models


class Projeto(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class EquipamentoCadastro(models.Model):
    nome = models.CharField(max_length=100, unique=False)
    tipo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.nome} - ({self.tipo})"


class Unidade(models.Model):
    nome = models.CharField(max_length=100)
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
    unidade = models.ForeignKey(
        Unidade,
        on_delete=models.CASCADE,
        related_name='equipamentos'
    )
    nome = models.CharField(max_length=100)  # removeu choices
    tipo = models.CharField(max_length=100, blank=True)
    patrimonio = models.CharField(max_length=50)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    setor = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.nome} - ({self.tipo})"

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


class ConsolidadoMaquinas(models.Model):
    projeto = models.ForeignKey(
        'Projeto',
        on_delete=models.PROTECT,
        related_name='consolidados_maquinas'
    )
    unidade = models.ForeignKey(
        'Unidade',
        on_delete=models.PROTECT,
        related_name='consolidados_maquinas'
    )
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Consolidado de Máquinas'
        verbose_name_plural = 'Consolidados de Máquinas'
        unique_together = ('projeto', 'unidade')
        ordering = ['projeto', 'unidade']

    def __str__(self):
        return f"{self.projeto} - {self.unidade}: {self.quantidade}"

class ConsolidadoEquipamento(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='consolidados_equipamento')
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, related_name='consolidados_equipamento')
    equipamento = models.ForeignKey(EquipamentoCadastro, on_delete=models.CASCADE, related_name='consolidados')  # ou Equipamento, dependendo do uso
    quantidade = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('projeto', 'unidade', 'equipamento')
        verbose_name = 'Consolidado de Equipamento'
        verbose_name_plural = 'Consolidados de Equipamentos'
        ordering = ['projeto', 'unidade', 'equipamento']

    def __str__(self):
        return f"{self.projeto.nome} - {self.unidade.nome} - {self.equipamento.nome}: {self.quantidade}"

class TicketManutencao(models.Model):
    ESTADO_CHOICES = [
        ('Bom', 'Bom'),
        ('Ruim', 'Ruim'),
        ('Não contém', 'Não contém'),
    ]
    
    ESTADO_SIMPLES_CHOICES = [
        ('Bom', 'Bom'),
        ('Ruim', 'Ruim'),
    ]
    
    TIPO_RAM_CHOICES = [
        ('DDR2', 'DDR2'),
        ('DDR3', 'DDR3'),
        ('DDR4', 'DDR4'),
        ('DDR5', 'DDR5'),
    ]

    TIPO_ARMAZENAMENTO_CHOICES = [
        ('HD', 'HD'),
        ('SSD', 'SSD'),
        ('NVMe', 'NVMe'),
        ('Não contém', 'Não contém'),
    ]

    TIPO_FONTE_CHOICES = [
        ('ATX', 'ATX'),
        ('Slim', 'Slim'),
        ('Não contém', 'Não contém'),
    ]

    TIPO_EQUIPAMENTO_CHOICES = [
        ('Desktop', 'Desktop'),
        ('Monitor', 'Monitor'),
        ('Teclado', 'Teclado'),
        ('Mouse', 'Mouse'),
        ('Estabilizador', 'Estabilizador'),
        ('Nobreak', 'Nobreak'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True, verbose_name="Ticket ID")
    data_abertura = models.DateField(auto_now_add=True, verbose_name="Data de Abertura")
    tecnico = models.CharField(max_length=100, verbose_name="Técnico")
    patrimonio = models.CharField(max_length=50, blank=True, null=True, verbose_name="Patrimônio")
    ram_ausente = models.BooleanField(default=False, verbose_name="Não contém RAM")
    tipo_equipamento = models.CharField(max_length=50, choices=TIPO_EQUIPAMENTO_CHOICES, default='Desktop', verbose_name="Tipo de Equipamento")
    
    # EQUIPAMENTO
    equipamento_marca = models.CharField(max_length=100, verbose_name="Marca")
    equipamento_modelo = models.CharField(max_length=100, verbose_name="Modelo")
    gabinete_estado = models.CharField(max_length=20, choices=ESTADO_SIMPLES_CHOICES, default='Bom')
    
    # PROCESSADOR
    processador_nome = models.CharField(max_length=100, verbose_name="Nome do Processador", blank=True, null=True)
    processador_socket = models.CharField(max_length=50, verbose_name="Socket do Processador", blank=True, null=True)
    processador_estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Bom')
    
    # MEMORIA RAM
    ram_tipo = models.CharField(max_length=20, choices=TIPO_RAM_CHOICES, default='DDR4', verbose_name="Tecnologia (DDR)")
    ram_qtd_pentes = models.PositiveIntegerField(default=1, verbose_name="Quantidade de Pentes")
    ram_pentes_detalhes = models.JSONField(default=list, blank=True, help_text="Lista de dicionários [{capacidade: X, estado: 'Bom'}]")
    
    # ARMAZENAMENTO
    armazenamento_tipo = models.CharField(max_length=20, choices=TIPO_ARMAZENAMENTO_CHOICES, default='SSD')
    armazenamento_capacidade = models.CharField(max_length=50, blank=True, null=True, verbose_name="Capacidade (ex: 500GB)")
    armazenamento_estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Bom')
    
    # PLACA-MÃE
    placa_mae_estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Bom')
    
    
    # FONTE
    fonte_tipo = models.CharField(max_length=20, choices=TIPO_FONTE_CHOICES, default='ATX')
    fonte_estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Bom')
    
    # COOLER
    cooler_estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Bom')
    
    # DIAGNÓSTICO E OBS
    diagnostico = models.TextField(blank=True, null=True, verbose_name="Diagnóstico Automático")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações do Técnico")
    
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto'),
        ('AGUARDANDO PEÇAS', 'Aguardando Peças'),
        ('FINALIZADO', 'Finalizado'),
        ('CONDENADO', 'Condenado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO', verbose_name="Status")

    def __str__(self):
        return f"{self.ticket_id} - {self.equipamento_modelo}"
