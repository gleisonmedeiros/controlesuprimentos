from django.shortcuts import render, redirect
from .forms import UnidadeForm, SuprimentoForm, ProjetoForm, EntregaSuprimentoForm
from .models import Projeto, Unidade, Suprimento, EntregaSuprimento
def iterando_erro(form):
    errors = []
    for field, error_list in form.errors.items():
        for error in error_list:
            errors.append(f"{error}")
    return errors

id = 0

# Create your views here.
def index(request):
    if request.method == 'POST':
        cadastro_opcao = request.POST.get('cadastro_opcao')

        if cadastro_opcao == 'unidade':
            return redirect('criar_unidade')  # Redireciona para a view de cadastro de unidade
        elif cadastro_opcao == 'projeto':
            return redirect('criar_projeto')  # Redireciona para a view de cadastro de projeto
        elif cadastro_opcao == 'suprimento':
            return redirect('criar_suprimento')  # Redireciona para a view de cadastro de suprimento

    return render(request, 'index.html')

def criar_unidade(request):
    if request.method == 'POST':
        form = UnidadeForm(request.POST)
        if form.is_valid():
            print("funcionou")
            #if 'save_unidade' in request.POST:
            #    print("clicou")
            form.save()  # Salva a nova unidade
            form = UnidadeForm()
            erro = ['0']
            return render(request, 'cadastro_unidade.html', {'form': form,'errors': erro})
        else:
            erro = iterando_erro(form)
            print(erro)
            return render(request, 'cadastro_unidade.html', {'form': form,'errors': erro})
    else:
        form = UnidadeForm()

    return render(request, 'cadastro_unidade.html', {'form': form})

def criar_suprimento(request):
    if request.method == 'POST':
        form = SuprimentoForm(request.POST)
        if form.is_valid():
            print("funcionou")
            #if 'save_unidade' in request.POST:
            #    print("clicou")
            form.save()  # Salva a nova unidade
            form = SuprimentoForm()
            erro = ['0']
            return render(request, 'cadastro_suprimento.html', {'form': form,'errors': erro})
        else:
            erro = iterando_erro(form)
            print(erro)
            return render(request, 'cadastro_suprimento.html', {'form': form,'errors': erro})
    else:
        form = SuprimentoForm()

    return render(request, 'cadastro_suprimento.html', {'form': form})

def criar_projeto(request):
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            print("funcionou")
            #if 'save_unidade' in request.POST:
            #    print("clicou")
            form.save()  # Salva a nova unidade
            form = ProjetoForm()
            erro = ['0']
            return render(request, 'cadastro_projeto.html', {'form': form,'errors': erro})
        else:
            erro = iterando_erro(form)
            print(erro)
            return render(request, 'cadastro_projeto.html', {'form': form,'errors': erro})
    else:
        form = ProjetoForm()

    return render(request, 'cadastro_projeto.html', {'form': form})



def entrega_suprimento(request):
    form_projeto = Projeto.objects.all()  # Recupera todos os projetos disponíveis

    if request.method == 'POST':
        # Captura o projeto selecionado
        form = EntregaSuprimentoForm(request.POST)
        if 'save_projeto' in request.POST:
            if 'form_projeto' in request.POST and request.POST['form_projeto']:
                result = request.POST.get('form_projeto')
                projeto = Projeto.objects.get(id=result)  # Recupera o projeto selecionado
                print(projeto)

                # Filtra as unidades associadas ao projeto selecionado
                unidades = Unidade.objects.filter(projeto=projeto)
                form = EntregaSuprimentoForm(request.POST)
                form.fields['unidade'].queryset = unidades  # Atualiza o queryset de unidades no formulário

            else:
                # Caso o projeto não tenha sido selecionado, você pode redirecionar ou exibir um erro
                form = EntregaSuprimentoForm(request.POST)
                erro = ['Projeto não selecionado']
                return render(request, 'entrega_suprimento.html', {'form': form, 'errors': erro, 'form_projeto': form_projeto})

        # Se o formulário for válido
        if form.is_valid():
            if 'save_entrega' in request.POST:
                print("clicou")
                form.save()  # Apenas salva os dados do formulário sem associar o projeto
                erro = ['0']
                form = EntregaSuprimentoForm()  # Reseta o formulário após o envio
                return render(request, 'entrega_suprimento.html', {'form': form, 'errors': erro, 'form_projeto': form_projeto})

        else:
            erro = iterando_erro(form)
            print(erro)
            return render(request, 'entrega_suprimento.html', {'form': form, 'errors': erro, 'form_projeto': form_projeto})

    else:
        form = EntregaSuprimentoForm()  # Se o método não for POST, cria o formulário vazio

    return render(request, 'entrega_suprimento.html', {'form': form, 'form_projeto': form_projeto})


def processar_selecao(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_value = data.get('selected')
        print(selected_value)

        # Aqui você pode realizar alguma ação com o valor selecionado
        # Exemplo de resposta
        return JsonResponse({'result': selected_value})