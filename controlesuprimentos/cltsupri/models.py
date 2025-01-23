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
