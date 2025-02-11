from django import forms
from .models import Unidade, Suprimento, EntregaSuprimento, Projeto

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
        fields = ['unidade', 'suprimento', 'quantidade_entregue', 'data', 'setor']
        widgets = {
            'unidade': forms.Select(attrs={'class': 'form-control'}),
            'suprimento': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_entregue': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'setor': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customiza as opções de unidade e suprimento, se necessário
        self.fields['unidade'].queryset = Unidade.objects.all()
        self.fields['suprimento'].queryset = Suprimento.objects.all()
