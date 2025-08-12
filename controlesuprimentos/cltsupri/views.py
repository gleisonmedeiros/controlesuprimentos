from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import UnidadeForm, SuprimentoForm, ProjetoForm, EntregaSuprimentoForm, EquipamentoForm,UnidadeAssociacaoForm,ModeloFornecedorForm
from .models import Projeto, Unidade, Suprimento, EntregaSuprimento, Equipamento,UnidadeAssociacao, ModeloFornecedor
import json
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect

from django.shortcuts import render
from .models import Maquina, UnidadeAssociacao, ModeloFornecedor

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
        entrega_id = request.POST.get("entrega_id")
        is_pesquisa = request.POST.get("btn-pesquisar")  # só vem se o botão de filtro for clicado

        if entrega_id and not is_pesquisa:
            print(f"ID da entrega clicada: {entrega_id}")
            request.session['entrega_id'] = entrega_id
            return redirect('pesquisa_entrega')
            # Aqui você pode redirecionar, mostrar detalhes, etc.
            # Exemplo: return redirect('detalhes_entrega', pk=entrega_id)

        else:
            # Filtros via formulário
            valor_projeto = request.POST.get('projeto')
            valor_unidade = request.POST.get('unidade')
            data_inicio = request.POST.get('data_inicio')
            data_fim = request.POST.get('data_fim')

            print(f"Projeto Selecionado: {valor_projeto}")
            print(f"Unidade Selecionada: {valor_unidade}")
            print(f"Data Início: {data_inicio}")
            print(f"Data Fim: {data_fim}")

            if valor_projeto:
                entregas_ordenadas = entregas_ordenadas.filter(unidade__projeto_id=valor_projeto)
            if valor_unidade:
                entregas_ordenadas = entregas_ordenadas.filter(unidade_id=valor_unidade)
            if data_inicio:
                entregas_ordenadas = entregas_ordenadas.filter(data__gte=data_inicio)
            if data_fim:
                entregas_ordenadas = entregas_ordenadas.filter(data__lte=data_fim)

    return render(request, 'pesquisa.html', {
        'form': entregas_ordenadas,
        'form_projeto': form_projeto,
        'form_unidades': form_unidades
    })


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
    ordenado = {k: lista[k] for k in sorted(lista)}
    lista = ordenado

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
        editar = request.session.get('editar', None)
        unidade_id = request.session.get('unidade_id_novo', None)

        if editar == True and unidade_id is not None:
            unidade = get_object_or_404(Unidade, id=unidade_id)
            form = UnidadeForm(request.POST, instance=unidade)
        else:
            form = UnidadeForm(request.POST)

        if form.is_valid():
            nome = form.cleaned_data.get('nome')
            projeto = form.cleaned_data.get('projeto')

            # Apaga outra unidade com mesmo nome e projeto, exceto a atual
            Unidade.objects.filter(nome=nome, projeto=projeto).exclude(id=unidade_id).delete()

            form.save()
            form = UnidadeForm()
            erro = ['0']
            return render(request, 'cadastro_unidade.html', {'form': form, 'errors': erro})
        else:
            erro = iterando_erro(form)
            print(erro)
            return render(request, 'cadastro_unidade.html', {'form': form, 'errors': erro})

    else:
        unidade_id = request.session.get('unidade_id', None)
        request.session['unidade_id_novo'] = unidade_id
        request.session['editar'] = False

        if unidade_id is not None:
            unidade = get_object_or_404(Unidade, id=unidade_id)
            form = UnidadeForm(instance=unidade)
            request.session['editar'] = True
        else:
            form = UnidadeForm()

        print(request.session.get('editar', None))
        print(unidade_id)
        request.session.pop('unidade_id', None)

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
    form_projeto = Projeto.objects.all().order_by('nome')
    suprimentos = Suprimento.objects.all().order_by('nome')
    unidades = Unidade.objects.all().order_by('nome')
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
        if 'save_unidade' in request.POST:
            projeto_id = request.POST.get("projeto")
            form = Unidade.objects.filter(projeto_id=projeto_id)
            return render(request, 'pesquisa_unidades.html', {'form': form, 'form_projeto': form_projeto})
        unidade_id = request.POST.get("unidade_id")
        if unidade_id:
            request.session['unidade_id'] = unidade_id
            return redirect('criar_unidade')
    else:
        return render(request, 'pesquisa_unidades.html', {'form': form,'form_projeto':form_projeto})

from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404



def pesquisa_entrega(request):
    entrega_id = request.session.get('entrega_id')
    if not entrega_id:
        return redirect('pesquisa')

    entrega = get_object_or_404(EntregaSuprimento, id=entrega_id)
    unidades = Unidade.objects.all()
    suprimentos = Suprimento.objects.all()

    if request.method == 'POST':
        try:
            entrega.unidade_id = int(request.POST.get('unidade', entrega.unidade_id))
            entrega.suprimento_id = int(request.POST.get('suprimento', entrega.suprimento_id))
            entrega.quantidade_entregue = int(request.POST.get('quantidade_entregue', entrega.quantidade_entregue))
            entrega.data = datetime.strptime(request.POST.get('data', str(entrega.data)), '%Y-%m-%d').date()
            entrega.setor = request.POST.get('setor', entrega.setor)

            # Se a quantidade for zero, deleta o registro
            if entrega.quantidade_entregue == 0:
                entrega.delete()
            else:
                entrega.save()

            # Limpa a sessão após salvar ou deletar
            request.session.pop('entrega_id', None)

            return redirect('pesquisa')

        except Exception as e:
            print(f"Erro ao salvar ou deletar entrega: {e}")  # Para produção, use logging.error()

    return render(request, 'pesquisa_entrega.html', {
        'entrega': entrega,
        'unidades': unidades,
        'suprimentos': suprimentos,
    })

#############################################


import json
from datetime import datetime, timedelta
from django.shortcuts import render


import json
from django.shortcuts import render
from .models import Maquina

# Suas funções auxiliares (exemplo)
def get_safe(dct, keys, default=None):
    for key in keys:
        if isinstance(dct, dict):
            dct = dct.get(key, default)
        else:
            return default
    return dct

def esta_off_mais_de_10_dias(timestamp_ms):
    # Implemente sua lógica aqui, ex:
    # Retorna True se timestamp estiver > 10 dias atrás
    from datetime import datetime, timedelta
    if timestamp_ms is None:
        return True
    ultimo = datetime.fromtimestamp(timestamp_ms / 1000)
    return (datetime.now() - ultimo) > timedelta(days=10)

def calcular_tempo_desde_timestamp(timestamp_ms):
    from datetime import datetime
    if timestamp_ms is None:
        return {'dias': 0, 'horas': 0, 'minutos': 0}
    ultimo = datetime.fromtimestamp(timestamp_ms / 1000)
    delta = datetime.now() - ultimo
    dias = delta.days
    horas = delta.seconds // 3600
    minutos = (delta.seconds % 3600) // 60
    return {'dias': dias, 'horas': horas, 'minutos': minutos}



def inventario(request):
    ON = 0
    OFF = 0
    lista_nomes_maquinas_offline = []
    maquinas = []

    if request.method == "POST":
        if request.FILES.get("arquivo"):
            arquivo = request.FILES["arquivo"]

            if not arquivo.name.endswith(".json"):
                return render(request, "inventario.html", {"erro": "Arquivo inválido. Envie um arquivo JSON."})

            try:
                data = json.load(arquivo)
                maquinas = []

                for item in data:
                    nome_maquina = get_safe(item, ["node", "name"]) or "-"
                    tag = get_safe(item, ["node", "agent", "tag"]) or "-"
                    sistema_operacional = get_safe(item, ["node", "osdesc"]) or "-"
                    cpu_list = get_safe(item, ["sys", "hardware", "windows", "cpu"], [])
                    processador = cpu_list[0]["Name"] if cpu_list else "-"

                    memoria_banks = get_safe(item, ["sys", "hardware", "windows", "memory"], [])
                    memoria_total_bytes = 0
                    for mem in memoria_banks:
                        try:
                            memoria_total_bytes += int(mem.get("Capacity", 0))
                        except:
                            pass

                    if memoria_total_bytes > 0:
                        memoria_total_gb = memoria_total_bytes / (1024 ** 3)
                    else:
                        memoria_total_gb = None

                    placa_mae = get_safe(item, ["sys", "hardware", "identifiers", "board_name"]) or "-"
                    fabricante_placa_mae = get_safe(item, ["sys", "hardware", "identifiers", "board_vendor"]) or "-"

                    fornecedor_associado = (
                        ModeloFornecedor.objects.filter(modelo=placa_mae)
                        .values_list("fornecedor", flat=True)
                        .first()
                        or ""
                    )

                    drives = get_safe(item, ["sys", "hardware", "windows", "drives"], [])
                    if drives:
                        disco = drives[0].get("Model", "-")
                        tamanho_disco_bytes = int(drives[0].get("Size", 0))
                        tamanho_disco_gb = round(tamanho_disco_bytes / (1024 ** 3), 2) if tamanho_disco_bytes > 0 else None
                    else:
                        disco = "-"
                        tamanho_disco_gb = None

                    timestamp_ms = get_safe(item, ["lastConnect", "time"], None)
                    status = "OFF" if esta_off_mais_de_10_dias(timestamp_ms) else "ON"

                    if status == "OFF":
                        OFF += 1
                        lista_nomes_maquinas_offline.append(nome_maquina)
                    else:
                        ON += 1

                    tempo_off = calcular_tempo_desde_timestamp(timestamp_ms)

                    associacao = None
                    for i in range(len(nome_maquina), 0, -1):
                        prefixo = nome_maquina[:i]
                        associacao = UnidadeAssociacao.objects.filter(prefixo_nome=prefixo).first()
                        if associacao:
                            break

                    unidade_associada = associacao.unidade if associacao else None

                    maquinas.append({
                        "nome": nome_maquina,
                        "tag": tag,
                        "sistema_operacional": sistema_operacional,
                        "processador": processador,
                        "memoria_total": memoria_total_gb,
                        "placa_mae": placa_mae,
                        "fabricante_placa_mae": fabricante_placa_mae,
                        "disco": disco,
                        "tamanho_disco": tamanho_disco_gb,
                        "tempo_off_dias": tempo_off['dias'],
                        "tempo_off_horas": tempo_off['horas'],
                        "tempo_off_minutos": tempo_off['minutos'],
                        "status": status,
                        "unidade_associada": unidade_associada.nome if unidade_associada else "",
                        "fornecedor_associado": fornecedor_associado,
                    })

                return render(request, "inventario.html", {
                    "mensagem": "Arquivo processado com sucesso. Clique em salvar para persistir no banco.",
                    "maquinas": maquinas,
                    "on": ON,
                    "off": OFF,
                    "lista_off": lista_nomes_maquinas_offline,
                    "maquinas_json": json.dumps(maquinas),
                })

            except json.JSONDecodeError:
                return render(request, "inventario.html", {"erro": "Erro ao ler o JSON. Verifique o arquivo."})

        elif "salvar" in request.POST:
            maquinas_json = request.POST.get("maquinas_json")
            if not maquinas_json:
                return render(request, "inventario.html", {"erro": "Nenhum dado para salvar."})

            maquinas_para_salvar = json.loads(maquinas_json)

            for m in maquinas_para_salvar:
                associacao = None
                for i in range(len(m["nome"]), 0, -1):
                    prefixo = m["nome"][:i]
                    associacao = UnidadeAssociacao.objects.filter(prefixo_nome=prefixo).first()
                    if associacao:
                        break
                unidade_associada = associacao.unidade if associacao else None

                Maquina.objects.update_or_create(
                    nome=m["nome"],
                    defaults={
                        "tag": m["tag"],
                        "sistema_operacional": m["sistema_operacional"],
                        "processador": m["processador"],
                        "memoria_total": m["memoria_total"],
                        "placa_mae": m["placa_mae"],
                        "fabricante_placa_mae": m["fabricante_placa_mae"],
                        "disco": m["disco"],
                        "tamanho_disco": m["tamanho_disco"],
                        "tempo_off_dias": m["tempo_off_dias"],
                        "tempo_off_horas": m["tempo_off_horas"],
                        "tempo_off_minutos": m["tempo_off_minutos"],
                        "status": m["status"],
                        "unidade_associada": unidade_associada,
                        "fornecedor_associado": m.get("fornecedor_associado", ""),
                    }
                )

            return render(request, "inventario.html", {
                "mensagem": "Inventário salvo no banco com sucesso.",
                "maquinas": maquinas_para_salvar,
                "on": len([m for m in maquinas_para_salvar if m["status"] == "ON"]),
                "off": len([m for m in maquinas_para_salvar if m["status"] == "OFF"]),
                "lista_off": [m["nome"] for m in maquinas_para_salvar if m["status"] == "OFF"],
                "maquinas_json": maquinas_json,
            })

    # GET - mostrar dados já salvos
    maquinas_db = Maquina.objects.all()
    maquinas = []
    for m in maquinas_db:
        maquinas.append({
            "nome": m.nome,
            "tag": m.tag,
            "sistema_operacional": m.sistema_operacional,
            "processador": m.processador,
            "memoria_total": m.memoria_total,
            "placa_mae": m.placa_mae,
            "fabricante_placa_mae": m.fabricante_placa_mae,
            "disco": m.disco,
            "tamanho_disco": m.tamanho_disco,
            "tempo_off_dias": m.tempo_off_dias,
            "tempo_off_horas": m.tempo_off_horas,
            "tempo_off_minutos": m.tempo_off_minutos,
            "status": m.status,
            "unidade_associada": m.unidade_associada.nome if m.unidade_associada else "",
            "fornecedor_associado": m.fornecedor_associado or "",
        })

    return render(request, "inventario.html", {
        "maquinas": maquinas,
        "on": maquinas_db.filter(status="ON").count(),
        "off": maquinas_db.filter(status="OFF").count(),
        "lista_off": maquinas_db.filter(status="OFF").values_list("nome", flat=True),
        "maquinas_json": json.dumps(maquinas),
    })

def cadastro_equipamento(request):
    projetos = Projeto.objects.all()
    tipos = Equipamento.NOME_CHOICES  # seu campo de opções "nome"

    selected_projeto = request.POST.get('projeto', '') if request.method == 'POST' else ''
    selected_unidade = request.POST.get('unidade', '') if request.method == 'POST' else ''

    if selected_projeto:
        unidades = Unidade.objects.filter(projeto_id=selected_projeto)
    else:
        unidades = Unidade.objects.none()

    if request.method == 'POST' and 'patrimonio' in request.POST:
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cadastro_equipamento')
        else:
            print("Form inválido. Erros:", form.errors)  # <-- Aqui imprime os erros
    else:
        form = EquipamentoForm()

    equipamentos = Equipamento.objects.select_related('unidade').order_by('unidade__nome', 'patrimonio')

    return render(request, 'cadastro_equipamento.html', {
        'projetos': projetos,
        'unidades': unidades,
        'tipos': tipos,
        'form': form,
        'selected_projeto': selected_projeto,
        'selected_unidade': selected_unidade,
        'equipamentos': equipamentos,
    })

def associar_unidade(request):
    if request.method == "POST":
        form = UnidadeAssociacaoForm(request.POST)
        if form.is_valid():
            prefixo = form.cleaned_data['prefixo_nome']
            unidade = form.cleaned_data['unidade']
            # Se já existir prefixo, atualiza unidade (sobrescrever)
            associacao, created = UnidadeAssociacao.objects.update_or_create(
                prefixo_nome=prefixo,
                defaults={'unidade': unidade}
            )
            return redirect('associar_unidade')
    else:
        form = UnidadeAssociacaoForm()

    associacoes = UnidadeAssociacao.objects.select_related('unidade__projeto').all()

    # Para popular combo projeto e unidade, se quiser filtro dinâmico também
    projetos = Projeto.objects.all()

    context = {
        'form': form,
        'associacoes': associacoes,
        'projetos': projetos,
    }
    return render(request, 'associar_unidade.html', context)


def modelo_fornecedor_create(request):
    if request.method == 'POST':
        form = ModeloFornecedorForm(request.POST)
        if form.is_valid():
            modelo = form.cleaned_data['modelo']
            fornecedor = form.cleaned_data['fornecedor']
            # Usando o modelo do form.Meta para filtro
            if ModeloFornecedor.objects.filter(modelo=modelo, fornecedor=fornecedor).exists():
                form.add_error(None, "Essa associação modelo-fornecedor já existe.")
            else:
                form.save()
                return redirect('modelo-fornecedor-create')
    else:
        form = ModeloFornecedorForm()

    return render(request, 'modelo_fornecedor.html', {'form': form})

def maquinas_equipamentos_por_unidade(request):
    unidades = Unidade.objects.order_by('nome')

    # Filtros via GET
    unidade_id = request.GET.get('unidade')
    status_maquina = request.GET.get('status')
    tipo_equipamento = request.GET.get('tipo')
    tempo_off_min = request.GET.get('tempo_off_min')
    fornecedor_associado = request.GET.get('fornecedor')  # novo filtro

    maquinas = Maquina.objects.all()
    equipamentos = Equipamento.objects.all()

    if unidade_id:
        maquinas = maquinas.filter(unidade_associada_id=unidade_id)
        equipamentos = equipamentos.filter(unidade_id=unidade_id)

    if status_maquina:
        maquinas = maquinas.filter(status=status_maquina)

    if fornecedor_associado:
        maquinas = maquinas.filter(fornecedor_associado=fornecedor_associado)

    if tipo_equipamento:
        equipamentos = equipamentos.filter(nome=tipo_equipamento)

    # Filtra por tempo_off_dias >= tempo_off_min (se informado e número válido)
    if tempo_off_min:
        try:
            tempo_off_min_val = int(tempo_off_min)
            maquinas = maquinas.filter(tempo_off_dias__gte=tempo_off_min_val)
        except ValueError:
            pass  # se não for número válido, ignora

    maquinas = maquinas.order_by('unidade_associada__nome', 'nome')
    equipamentos = equipamentos.order_by('unidade__nome', 'nome')

    # Lista fornecedores distintos para popular o filtro (removendo valores vazios)
    fornecedores = (
        Maquina.objects
        .values_list('fornecedor_associado', flat=True)
        .exclude(fornecedor_associado__isnull=True)
        .exclude(fornecedor_associado__exact='')
        .distinct()
        .order_by('fornecedor_associado')
    )

    return render(request, 'maquinas_equipamentos.html', {
        'unidades': unidades,
        'fornecedores': fornecedores,
        'maquinas': maquinas,
        'equipamentos': equipamentos,
        'filtros': {
            'unidade_id': unidade_id or '',
            'status_maquina': status_maquina or '',
            'tipo_equipamento': tipo_equipamento or '',
            'tempo_off_min': tempo_off_min or '',
            'fornecedor_associado': fornecedor_associado or '',
        }
    })
