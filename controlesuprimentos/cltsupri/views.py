from django.shortcuts import render, redirect, get_object_or_404
from .forms import UnidadeForm, SuprimentoForm, ProjetoForm, EntregaSuprimentoForm
from .models import Projeto, Unidade, Suprimento, EntregaSuprimento
def iterando_erro(form):
    errors = []
    for field, error_list in form.errors.items():
        for error in error_list:
            errors.append(f"{error}")
    return errors

id = 0

def pesquisa(request):
    entregas_ordenadas = EntregaSuprimento.objects.all().order_by('data')
    form_projeto = Projeto.objects.all()
    form_unidades = Unidade.objects.all()
    if request.method == 'POST':
        valor_projeto = request.POST.get('projeto')  # Captura o valor do campo 'projeto'
        valor_unidade = request.POST.get('unidade')  # Captura o valor do campo 'unidade'
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')

        # Imprimir para teste
        print(f"Projeto Selecionado: {valor_projeto}")
        print(f"Unidade Selecionada: {valor_unidade}")
        print(f"Data Início: {data_inicio}")
        print(f"Data Fim: {data_fim}")

        # Filtrar entregas com base nos valores capturados
        if valor_projeto:
            entregas_ordenadas = entregas_ordenadas.filter(unidade__projeto_id=valor_projeto)
        if valor_unidade:
            entregas_ordenadas = entregas_ordenadas.filter(unidade_id=valor_unidade)
        if data_inicio:
            entregas_ordenadas = entregas_ordenadas.filter(data__gte=data_inicio)
        if data_fim:
            entregas_ordenadas = entregas_ordenadas.filter(data__lte=data_fim)
    else:
        for entrega in entregas_ordenadas:
            #print(entrega)
            pass
    return render(request,'pesquisa.html',{'form': entregas_ordenadas,'form_projeto':form_projeto,'form_unidades':form_unidades} )

def total_unidade(request):
    entregas_ordenadas = EntregaSuprimento.objects.all().order_by('data')
    form_projeto = Projeto.objects.all()
    form_unidades = Unidade.objects.all()
    if request.method == 'POST':
        valor_projeto = request.POST.get('projeto')  # Captura o valor do campo 'projeto'
        valor_unidade = request.POST.get('unidade')  # Captura o valor do campo 'unidade'
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')

        # Imprimir para teste
        print(f"Projeto Selecionado: {valor_projeto}")
        print(f"Unidade Selecionada: {valor_unidade}")
        print(f"Data Início: {data_inicio}")
        print(f"Data Fim: {data_fim}")

        # Filtrar entregas com base nos valores capturados
        if valor_projeto:
            entregas_ordenadas = entregas_ordenadas.filter(unidade__projeto_id=valor_projeto)
        if valor_unidade:
            entregas_ordenadas = entregas_ordenadas.filter(unidade_id=valor_unidade)
        if data_inicio:
            entregas_ordenadas = entregas_ordenadas.filter(data__gte=data_inicio)
        if data_fim:
            entregas_ordenadas = entregas_ordenadas.filter(data__lte=data_fim)
    else:
        for entrega in entregas_ordenadas:
            #print(entrega)
            pass

    lista = {}
    total = 0
    for entrega in entregas_ordenadas:
        if entrega.unidade.nome not in lista:
            lista[entrega.unidade.nome] = 0
        lista[entrega.unidade.nome] += entrega.quantidade_entregue
        total += entrega.quantidade_entregue

    print(lista)

    return render(request,'total_unidade.html',{'form': entregas_ordenadas,'form_projeto':form_projeto,'form_unidades':form_unidades,'lista':lista,'total':total} )


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
            editar = request.session.get('editar', None)
            suprimento_id = request.session.get('suprimento_id_novo', None)
            if (editar == True) and (suprimento_id != None):
                suprimento = get_object_or_404(Suprimento, id=suprimento_id)
                form = SuprimentoForm(request.POST, instance=suprimento)
            form.save()  # Salva a nova unidade
            form = SuprimentoForm()
            erro = ['0']
            return render(request, 'cadastro_suprimento.html', {'form': form,'errors': erro})
        else:
            erro = iterando_erro(form)
            print(erro)
            return render(request, 'cadastro_suprimento.html', {'form': form,'errors': erro})
    else:
        suprimento_id = request.session.get('suprimento_id', None)
        request.session['suprimento_id_novo'] = suprimento_id
        request.session['editar'] = False
        if suprimento_id != None:
            suprimento = get_object_or_404(Suprimento, id=suprimento_id)
            form = SuprimentoForm(instance=suprimento)
            request.session['editar'] = True
        else:
            request.session['editar'] = False
            form = SuprimentoForm()
        print(request.session.get('editar', None))
        print(suprimento_id)
        request.session.pop('suprimento_id', None)

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
                unidades = Unidade.objects.filter(projeto=projeto).order_by('nome')
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
        #del form.fields['unidade']
        form.fields['unidade'].disabled = True

    return render(request, 'entrega_suprimento.html', {'form': form, 'form_projeto': form_projeto})


def processar_selecao(request):
    pass
'''
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_value = data.get('selected')
        print(selected_value)

        # Aqui você pode realizar alguma ação com o valor selecionado
        # Exemplo de resposta
        return JsonResponse({'result': selected_value})
'''

def pesquisa_suprimento(request):
    form = Suprimento.objects.all()
    if request.method == 'POST':
        suprimento_id = request.POST.get("suprimento_id")
        if suprimento_id:
            suprimento = Suprimento.objects.get(id=suprimento_id)
            mensagem = f"Você selecionou o suprimento: {suprimento.nome}"
            request.session['suprimento_id'] = suprimento_id
            print(mensagem)
            #return render(request, 'pesquisa_suprimentos.html', {'form': form})
            return redirect('criar_suprimento')
    else:
        return render(request, 'pesquisa_suprimentos.html',{'form':form})