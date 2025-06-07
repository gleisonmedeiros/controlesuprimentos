from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import UnidadeForm, SuprimentoForm, ProjetoForm, EntregaSuprimentoForm
from .models import Projeto, Unidade, Suprimento, EntregaSuprimento
import json
from datetime import datetime

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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EntregaSuprimento, Suprimento, Unidade, Projeto
from .forms import EntregaSuprimentoForm
from datetime import datetime
import json


@csrf_exempt
def entrega_suprimento(request):
    form_projeto = Projeto.objects.all()
    suprimentos = Suprimento.objects.all()
    unidades = Unidade.objects.all()
    erro = []

    if request.method == 'POST':
        form = EntregaSuprimentoForm(request.POST)

        # BLOCO: seleção do projeto
        if 'save_projeto' in request.POST:
            projeto_id = request.POST.get('form_projeto')
            if projeto_id:
                projeto = Projeto.objects.get(id=projeto_id)
                unidades = Unidade.objects.filter(projeto=projeto).order_by('nome')
                form.fields['unidade'].disabled = False
            else:
                erro = ['Projeto não selecionado']

            return render(request, 'entrega_suprimento.html', {
                'suprimentos': suprimentos,
                'form': form,
                'form_projeto': form_projeto,
                'errors': erro,
                'unidades': unidades,
            })

        # BLOCO: envio via AJAX
        elif request.headers.get('Content-Type') == 'application/json':
            try:
                data_json = json.loads(request.body)
                registros = data_json.get("registros", [])
                unidade_nome = data_json.get("unidade")
                data_str = data_json.get("date")

                erros = []

                # Verifica unidade
                if not unidade_nome:
                    erros.append("Unidade não preenchida.")
                    unidade = None
                else:
                    unidade = Unidade.objects.filter(nome__iexact=unidade_nome).first()
                    if not unidade:
                        erros.append(f"Unidade '{unidade_nome}' não encontrada.")
                        unidade = None

                # Verifica data
                if not data_str:
                    erros.append("Data não preenchida.")
                    data = None
                else:
                    try:
                        data = datetime.strptime(data_str, "%Y-%m-%d").date()
                    except ValueError:
                        erros.append("Formato de data inválido. Use AAAA-MM-DD.")
                        data = None

                # Processa os registros
                entregas_para_salvar = []

                if unidade and data:
                    for i, item in enumerate(registros or [], start=1):
                        toner = (item.get("toner") or "").strip()
                        quantidade = item.get("quantidade")
                        setor = (item.get("setor") or "").strip()

                        is_empty = not toner and not quantidade and not setor
                        is_partial = (toner or quantidade or setor) and not (toner and quantidade and setor)

                        if i == 1:
                            if is_partial or is_empty:
                                erros.append("Linha 1 deve estar completamente preenchida.")
                                break  # erro na primeira linha, não continua
                        else:
                            if is_partial:
                                erros.append(f"Linha {i} está parcialmente preenchida.")
                            elif is_empty:
                                continue  # ignora linha totalmente vazia

                        if not is_empty and not is_partial:
                            suprimento = Suprimento.objects.filter(nome__iexact=toner).first()
                            if not suprimento:
                                erros.append(f"Linha {i}: Suprimento '{toner}' não encontrado.")
                            else:
                                entregas_para_salvar.append(EntregaSuprimento(
                                    unidade=unidade,
                                    suprimento=suprimento,
                                    quantidade_entregue=quantidade,
                                    data=data,
                                    setor=setor
                                ))

                # Salva apenas se não houver erros
                if not erros:
                    for entrega in entregas_para_salvar:
                        entrega.save()

                contexto = {
                    'form': EntregaSuprimentoForm(),
                    'form_projeto': form_projeto,
                    'suprimentos': suprimentos,
                    'unidades': unidades,
                }

                if erros:
                    contexto['erro'] = erros
                else:
                    contexto['mensagem'] = ['Entregas salvas com sucesso!']

                return render(request, 'entrega_suprimento.html', contexto)

            except Exception as e:
                print("Dei erro")
                return JsonResponse({'erro': str(e)}, status=500)

        # BLOCO: envio tradicional do formulário Django
        elif 'save_entrega' in request.POST:
            if form.is_valid():
                form.save()
                erro = ['0']
                form = EntregaSuprimentoForm()
            else:
                erro = iterando_erro(form)

            return render(request, 'entrega_suprimento.html', {
                'suprimentos': suprimentos,
                'form': form,
                'errors': erro,
                'form_projeto': form_projeto,
                'unidades': unidades,
            })

    else:
        form = EntregaSuprimentoForm()
        form.fields['unidade'].disabled = True

    return render(request, 'entrega_suprimento.html', {
        'suprimentos': suprimentos,
        'form': form,
        'form_projeto': form_projeto,
        'unidades': unidades,
    })
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

def pesquisa_unidade(request):
    form_projeto = UnidadeForm()
    form = Unidade.objects.all()
    if request.method == 'POST':
        unidade_id = request.POST.get("unidade_id")
        if unidade_id:
            unidade = Unidade.objects.get(id=unidade_id)
            mensagem = f"Você selecionou a unidade: {unidade.nome}"
            request.session['unidade_id'] = unidade_id
            print(mensagem)
            return redirect('criar_unidade')
    else:
        return render(request, 'pesquisa_unidades.html', {'form': form,'form_projeto':form_projeto})