from django import forms
from .models import (Unidade,
                     Suprimento,
                     EntregaSuprimento,
                     Projeto,
                     Equipamento,
                     UnidadeAssociacao,
                     ModeloFornecedor,
                     Maquina,
                     ConsolidadoMaquinas,
                     EquipamentoCadastro,
                     ConsolidadoEquipamento)

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class EquipamentoCadastroForm(forms.ModelForm):
    class Meta:
        model = EquipamentoCadastro
        fields = ['nome', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ConsolidadoEquipamentoForm(forms.ModelForm):
    class Meta:
        model = ConsolidadoEquipamento
        fields = ['projeto', 'unidade', 'equipamento', 'quantidade']
        widgets = {
            'projeto': forms.Select(attrs={'class': 'form-control'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
            'equipamento': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'projeto': 'Projeto',
            'unidade': 'Unidade',
            'equipamento': 'Equipamento',
            'quantidade': 'Quantidade',
        }

class ConsolidadoMaquinasForm(forms.ModelForm):
    class Meta:
        model = ConsolidadoMaquinas
        fields = ['projeto', 'unidade', 'quantidade']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu usuário'})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Digite sua senha'})
    )

class ModeloFornecedorForm(forms.ModelForm):
    modelo = forms.ChoiceField(label="Placa Mãe")
    fornecedor = forms.ChoiceField(
        choices=ModeloFornecedor.FORNECEDOR_CHOICES,
        label="Fornecedor"
    )

    class Meta:
        model = ModeloFornecedor
        fields = ['modelo', 'fornecedor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtemos placas e marcas únicas
        placas = Maquina.objects.values_list('placa_mae', 'fabricante_placa_mae').distinct().order_by('placa_mae')
        placas = [(p, f) for p, f in placas if p]

        # Criamos as opções com label "Marca - Placa"
        self.fields['modelo'].choices = [
            (placa, f"{marca} - {placa}") for placa, marca in placas
        ]

        # Classes Bootstrap
        self.fields['modelo'].widget.attrs.update({'class': 'form-select'})
        self.fields['fornecedor'].widget.attrs.update({'class': 'form-select'})

class UnidadeAssociacaoForm(forms.ModelForm):
    class Meta:
        model = UnidadeAssociacao
        fields = ['prefixo_nome', 'unidade']
        widgets = {
            'prefixo_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome começa com...'}),
            'unidade': forms.Select(attrs={'class': 'form-control'}),
        }

class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = ['unidade', 'setor', 'patrimonio', 'marca', 'modelo', 'nome', 'tipo']

    nome = forms.CharField(max_length=100)  # Sem choices

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome']  # Adicionando o campo projeto
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Projeto'})
        }

class UnidadeForm(forms.ModelForm):
    class Meta:
        model = Unidade
        fields = ['nome', 'projeto']  # Adicionando o campo projeto
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da Unidade'}),
            'projeto': forms.Select(attrs={'class': 'form-control'}),  # Estilo para o campo de projeto
        }

class SuprimentoForm(forms.ModelForm):
    class Meta:
        model = Suprimento
        fields = ['nome', 'quantidade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Suprimento'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Quantidade'}),
        }

class EntregaSuprimentoForm(forms.ModelForm):
    class Meta:
        model = EntregaSuprimento
        fields = ['unidade','data']
        widgets = {
            'unidade': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customiza as opções de unidade e suprimento, se necessário
        self.fields['unidade'].queryset = Unidade.objects.all()

