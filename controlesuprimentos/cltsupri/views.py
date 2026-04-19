from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.template.loader import get_template

import json
import openpyxl
from datetime import timedelta, datetime
from collections import defaultdict

from .models import (
    Projeto, Unidade, Suprimento, EntregaSuprimento, Maquina, 
    Equipamento, EquipamentoCadastro, ConsolidadoMaquinas, 
    ConsolidadoEquipamento, UnidadeAssociacao, ModeloFornecedor, 
    TicketManutencao
)
from .forms import (
    LoginForm, ProjetoForm, UnidadeForm, SuprimentoForm, 
    EntregaSuprimentoForm, EquipamentoForm, EquipamentoCadastroForm, 
    ModeloFornecedorForm, UnidadeAssociacaoForm, 
    ConsolidadoMaquinasForm, TicketManutencaoForm, ConsolidadoEquipamentoForm
)

@login_required
@require_http_methods(["GET", "POST"])
def relatorio_estoque(request):
    suprimentos = Suprimento.objects.all().order_by('nome')
    if request.method == 'POST' and request.POST.get('editar_estoque'):
        for suprimento in suprimentos:
            nova_qtd = request.POST.get(f"quantidade_{suprimento.id}")
            nova_min = request.POST.get(f"minima_{suprimento.id}")
            try:
                if nova_qtd is not None:
                    suprimento.quantidade = max(0, int(nova_qtd))
                if nova_min is not None:
                    suprimento.quantidade_minima = max(0, int(nova_min))
                suprimento.save()
            except ValueError:
                pass
        return redirect('relatorio_estoque')
    context = {'suprimentos': suprimentos}
    return render(request, 'relatorio_estoque.html', context)



def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('index')

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def iterando_erro(form):
    errors = []
    for field, error_list in form.errors.items():
        for error in error_list:
            errors.append(f"{error}")
    return errors

@login_required(login_url='login')
def cadastrar_equipamento(request, equipamento_id=None):
    if equipamento_id:
        equipamento = get_object_or_404(EquipamentoCadastro, pk=equipamento_id)
    else:
        equipamento = None

    if request.method == 'POST':
        # Exclusão
        if 'delete' in request.POST:
            equipamento_del = get_object_or_404(EquipamentoCadastro, pk=request.POST.get('delete'))
            equipamento_del.delete()
            messages.success(request, 'Equipamento excluído com sucesso!')
            return redirect('cadastrar_equipamento')

        # Cadastro ou edição
        form = EquipamentoCadastroForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipamento salvo com sucesso!')
            return redirect('cadastrar_equipamento')
    else:
        form = EquipamentoCadastroForm(instance=equipamento)

    equipamentos = EquipamentoCadastro.objects.all().order_by('nome')

    return render(request, 'cadastrar_equipamento.html', {
        'form': form,
        'equipamentos': equipamentos,
        'equipamento_id': equipamento_id,
    })

id = 0
@login_required(login_url='login')
def pesquisa(request):

    # --- CAPTURAR FILTROS (GET) ---
    projeto_id = request.GET.get('projeto')
    unidade_id = request.GET.get('unidade')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # --- LISTAS PARA OS SELECT ---
    form_projeto = Projeto.objects.all().order_by('nome')

    if projeto_id:
        form_unidades = Unidade.objects.filter(projeto_id=projeto_id).order_by('nome')
    else:
        form_unidades = Unidade.objects.none()

    # --- CONSULTA PRINCIPAL ---
    entregas = EntregaSuprimento.objects.all().select_related('unidade', 'suprimento').order_by('-data')

    if projeto_id:
        entregas = entregas.filter(unidade__projeto_id=projeto_id)

    if unidade_id:
        entregas = entregas.filter(unidade_id=unidade_id)

    if data_inicio:
        entregas = entregas.filter(data__gte=data_inicio)

    if data_fim:
        entregas = entregas.filter(data__lte=data_fim)

    # --- SE CLICAR NA LINHA, REDIRECIONA ---
    if request.method == 'POST':
        entrega_id = request.POST.get("entrega_id")
        if entrega_id:
            request.session['entrega_id'] = entrega_id
            return redirect("pesquisa_entrega")

    return render(request, "pesquisa.html", {
        "form": entregas,
        "form_projeto": form_projeto,
        "form_unidades": form_unidades,
        "projeto_id": projeto_id,
        "unidade_id": unidade_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    })


@login_required(login_url='login')
def total_unidade(request):

    projeto_id = request.GET.get('projeto')
    unidade_id = request.GET.get('unidade')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    form_projeto = Projeto.objects.all().order_by('nome')

    # Carregar somente unidades do projeto selecionado
    if projeto_id:
        form_unidades = Unidade.objects.filter(projeto_id=projeto_id).order_by('nome')
    else:
        form_unidades = Unidade.objects.none()

    entregas = EntregaSuprimento.objects.all().select_related('unidade').order_by('data')

    # Aplica filtros
    if projeto_id:
        entregas = entregas.filter(unidade__projeto_id=projeto_id)

    if unidade_id:
        entregas = entregas.filter(unidade_id=unidade_id)

    if data_inicio:
        entregas = entregas.filter(data__gte=data_inicio)

    if data_fim:
        entregas = entregas.filter(data__lte=data_fim)

    # Montar lista
    lista = {}
    total = 0
    for entrega in entregas:
        nome = entrega.unidade.nome
        lista[nome] = lista.get(nome, 0) + entrega.quantidade_entregue
        total += entrega.quantidade_entregue

    lista = dict(sorted(lista.items()))

    return render(request, 'total_unidade.html', {
        'form_projeto': form_projeto,
        'form_unidades': form_unidades,
        'lista': lista,
        'total': total,

        'projeto_id': projeto_id,
        'unidade_id': unidade_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })


# Create your views here.
@login_required(login_url='login')
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Unidade
from .forms import UnidadeForm

# sem get_object_or_404, pois você prefere evitar

@login_required(login_url='login')
def criar_unidade(request, unidade_id=None):
    # Se estiver editando
    if unidade_id:
        try:
            unidade = Unidade.objects.get(id=unidade_id)
        except Unidade.DoesNotExist:
            unidade = None
    else:
        unidade = None

    if request.method == 'POST':
        # Excluir unidade
        if 'delete' in request.POST:
            Unidade.objects.filter(id=request.POST.get('delete')).delete()
            messages.success(request, 'Unidade excluída com sucesso!')
            return redirect('criar_unidade')

        # Criar ou editar unidade
        form = UnidadeForm(request.POST, instance=unidade)
        if form.is_valid():
            nome = form.cleaned_data.get('nome')
            projeto = form.cleaned_data.get('projeto')

            # Evita duplicação (mesmo nome e projeto)
            Unidade.objects.filter(nome=nome, projeto=projeto).exclude(id=unidade_id).delete()

            form.save()
            messages.success(request, 'Unidade salva com sucesso!')
            return redirect('criar_unidade')
        else:
            erro = iterando_erro(form)
            return render(request, 'cadastro_unidade.html', {
                'form': form,
                'unidades': Unidade.objects.all(),
                'errors': erro,
                'unidade_id': unidade_id,
            })

    else:
        form = UnidadeForm(instance=unidade)

    unidades = Unidade.objects.all()
    return render(request, 'cadastro_unidade.html', {
        'form': form,
        'unidades': unidades,
        'unidade_id': unidade_id,
        'errors': [],
    })


@login_required(login_url='login')
def criar_suprimento(request, suprimento_id=None):
    # Detecta edição
    if suprimento_id:
        try:
            suprimento = Suprimento.objects.get(id=suprimento_id)
        except Suprimento.DoesNotExist:
            suprimento = None
    else:
        suprimento = None

    if request.method == 'POST':
        # Excluir suprimento
        if 'delete' in request.POST:
            Suprimento.objects.filter(id=request.POST.get('delete')).delete()
            messages.success(request, 'Suprimento excluído com sucesso!')
            return redirect('criar_suprimento')

        # Criar ou editar suprimento
        form = SuprimentoForm(request.POST, instance=suprimento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Suprimento salvo com sucesso!')
            return redirect('criar_suprimento')
        else:
            erro = iterando_erro(form)
            return render(request, 'cadastro_suprimento.html', {
                'form': form,
                'suprimentos': Suprimento.objects.all(),
                'errors': erro,
                'suprimento_id': suprimento_id,
            })

    else:
        form = SuprimentoForm(instance=suprimento)

    suprimentos = Suprimento.objects.all()
    return render(request, 'cadastro_suprimento.html', {
        'form': form,
        'suprimentos': suprimentos,
        'suprimento_id': suprimento_id,
        'errors': [],
    })

@login_required(login_url='login')
def criar_projeto(request, projeto_id=None):
    if projeto_id:
        projeto = Projeto.objects.get(id=projeto_id)
    else:
        projeto = None

    if request.method == 'POST':
        # Excluir projeto
        if 'delete' in request.POST:
            Projeto.objects.filter(id=request.POST.get('delete')).delete()
            messages.success(request, 'Projeto excluído com sucesso!')
            return redirect('criar_projeto')

        # Criar ou editar projeto
        form = ProjetoForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto salvo com sucesso!')
            return redirect('criar_projeto')
        else:
            erro = iterando_erro(form)
            return render(request, 'cadastro_projeto.html', {
                'form': form,
                'projetos': Projeto.objects.all(),
                'errors': erro,
                'projeto_id': projeto_id,
            })

    else:
        form = ProjetoForm(instance=projeto)

    projetos = Projeto.objects.all()
    return render(request, 'cadastro_projeto.html', {
        'form': form,
        'projetos': projetos,
        'projeto_id': projeto_id,
        'errors': [],
    })


@login_required(login_url='login')
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
                quantidade_por_suprimento = {}

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
                                try:
                                    quantidade_int = int(quantidade)
                                except (TypeError, ValueError):
                                    erros.append(f"Linha {i}: Quantidade inválida.")
                                    continue

                                if quantidade_int <= 0:
                                    erros.append(f"Linha {i}: Quantidade deve ser maior que zero.")
                                    continue

                                quantidade_por_suprimento[suprimento.id] = quantidade_por_suprimento.get(suprimento.id, 0) + quantidade_int

                                entregas_para_salvar.append(EntregaSuprimento(
                                    unidade=unidade,
                                    suprimento=suprimento,
                                    quantidade_entregue=quantidade_int,
                                    data=data,
                                    setor=setor
                                ))

                # Valida saldo e salva apenas se não houver erros
                if not erros:
                    with transaction.atomic():
                        suprimentos_em_uso = {
                            s.id: s
                            for s in Suprimento.objects.select_for_update().filter(id__in=quantidade_por_suprimento.keys())
                        }

                        for suprimento_id, quantidade_requisitada in quantidade_por_suprimento.items():
                            suprimento = suprimentos_em_uso.get(suprimento_id)
                            if not suprimento:
                                erros.append("Suprimento não encontrado durante a atualização de estoque.")
                                continue

                            if suprimento.quantidade < quantidade_requisitada:
                                erros.append(
                                    f"Estoque insuficiente para '{suprimento.nome}'. Disponível: {suprimento.quantidade}, solicitado: {quantidade_requisitada}."
                                )

                        if not erros:
                            for suprimento_id, quantidade_requisitada in quantidade_por_suprimento.items():
                                suprimento = suprimentos_em_uso[suprimento_id]
                                suprimento.quantidade -= quantidade_requisitada
                                suprimento.save(update_fields=['quantidade'])

                            EntregaSuprimento.objects.bulk_create(entregas_para_salvar)

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



@login_required(login_url='login')
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
                messages.success(request, 'Entrega excluída com sucesso!')
            else:
                entrega.save()
                messages.success(request, 'Entrega atualizada com sucesso!')

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

@login_required(login_url='login')
def relatorio_toners(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    projeto_id = request.GET.get('projeto')
    unidade_id = request.GET.get('unidade')

    projetos = Projeto.objects.all()
    unidades = Unidade.objects.all().order_by("nome")

    entregas = EntregaSuprimento.objects.all()

    # Filtro por data
    if data_inicio and data_fim:
        entregas = entregas.filter(data__range=[data_inicio, data_fim])

    # Filtro por projeto
    if projeto_id:
        entregas = entregas.filter(unidade__projeto_id=projeto_id)
        unidades = unidades.filter(projeto_id=projeto_id)  # restringe unidades no select

    # Filtro por unidade
    if unidade_id:
        entregas = entregas.filter(unidade_id=unidade_id)

    # Agrupa por suprimento
    entregas = (
        entregas.values('suprimento__nome')
        .annotate(total=Sum('quantidade_entregue'))
        .order_by('suprimento__nome')
    )

    # Estoque atual de cada toner
    suprimentos = Suprimento.objects.all().order_by('nome')

    # Atualização de estoque (POST)
    if request.method == 'POST' and request.POST.get('editar_estoque'):
        for suprimento in suprimentos:
            field_name = f"quantidade_{suprimento.id}"
            nova_quantidade = request.POST.get(field_name)
            if nova_quantidade is not None:
                try:
                    nova_quantidade = int(nova_quantidade)
                    if nova_quantidade >= 0:
                        suprimento.quantidade = nova_quantidade
                        suprimento.save()
                except ValueError:
                    pass  # ignora valores inválidos
        return redirect('relatorio_toners')

    context = {
        'entregas': entregas,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'projetos': projetos,
        'unidades': unidades,
        'projeto_id': projeto_id,
        'unidade_id': unidade_id,
        'suprimentos': suprimentos,
    }
    return render(request, 'relatorio_toners.html', context)

#############################################






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

    if timestamp_ms is None:
        return True
    ultimo = datetime.fromtimestamp(timestamp_ms / 1000)
    return (datetime.now() - ultimo) > timedelta(days=10)

def calcular_tempo_desde_timestamp(timestamp_ms):

    if timestamp_ms is None:
        return {'dias': 0, 'horas': 0, 'minutos': 0}
    ultimo = datetime.fromtimestamp(timestamp_ms / 1000)
    delta = datetime.now() - ultimo
    dias = delta.days
    horas = delta.seconds // 3600
    minutos = (delta.seconds % 3600) // 60
    return {'dias': dias, 'horas': horas, 'minutos': minutos}

@login_required(login_url='login')
def inventario(request):
    projetos = Projeto.objects.all()
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
                        tamanho_disco = drives[0].get("Size", 0)
                        if tamanho_disco is None:
                            tamanho_disco_bytes = 0
                        else:
                            tamanho_disco_bytes = int(tamanho_disco)
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

                    projeto_id = request.POST.get("projeto_id")
                    projeto = Projeto.objects.filter(id=projeto_id).first()


                    request.session['projeto_id'] = projeto_id

                    print(f' >>>> {projeto}')


                    unidade_associada, _ = Unidade.objects.get_or_create(
                        projeto=projeto,
                        nome="-",
                    )

                    maquinas.append({
                        "unidade_associada": unidade_associada.nome,
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
                        "fornecedor_associado": fornecedor_associado,
                    })

                return render(request, "inventario.html", {
                    "mensagem": "Arquivo processado com sucesso. Clique em salvar para persistir no banco.",
                    "maquinas": maquinas,
                    "on": ON,
                    "off": OFF,
                    "lista_off": lista_nomes_maquinas_offline,
                    "maquinas_json": json.dumps(maquinas),
                    "projetos": projetos,
                })

            except json.JSONDecodeError:
                return render(request, "inventario.html", {"erro": "Erro ao ler o JSON. Verifique o arquivo."})

        elif "salvar" in request.POST:
            maquinas_json = request.POST.get("maquinas_json")
            if not maquinas_json:
                return render(request, "inventario.html", {"erro": "Nenhum dado para salvar."})

            maquinas_para_salvar = json.loads(maquinas_json)

            for m in maquinas_para_salvar:
                '''
                associacao = None
                for i in range(len(m["nome"]), 0, -1):
                    prefixo = m["nome"][:i]
                    associacao = UnidadeAssociacao.objects.filter(prefixo_nome=prefixo).first()
                    if associacao:
                        break
                unidade_associada = associacao.unidade if associacao else None
                '''

                projeto_id = request.session.get('projeto_id')
                projeto = Projeto.objects.filter(id=projeto_id).first()

                unidade_associada = Unidade.objects.filter(
                    projeto=projeto,
                    nome="-",
                ).first()

                Maquina.objects.update_or_create(
                    nome=m["nome"],
                    defaults={
                        "unidade_associada": unidade_associada.nome,
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
                "projetos": projetos,
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
        "projetos":projetos,
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Projeto, Unidade, Equipamento, EquipamentoCadastro
from .forms import EquipamentoForm


@login_required(login_url='login')
def cadastro_equipamento_consolidado(request, equipamento_id=None):
    projetos = Projeto.objects.all()

    # Seleção de projeto/unidade
    selected_projeto = request.POST.get('projeto', '') if request.method == 'POST' else ''
    selected_unidade = request.POST.get('unidade', '') if request.method == 'POST' else ''

    # Buscar instância se estiver editando
    equipamento_instance = None
    if equipamento_id:
        equipamento_instance = get_object_or_404(Equipamento, id=equipamento_id)
        if not selected_projeto:
            selected_projeto = str(equipamento_instance.unidade.projeto.id)
        if not selected_unidade:
            selected_unidade = str(equipamento_instance.unidade.id)

    # Filtrar unidades pelo projeto
    unidades = Unidade.objects.filter(projeto_id=selected_projeto).order_by(
        "nome") if selected_projeto else Unidade.objects.none()

    # Processar POST
    if request.method == 'POST':
        # Exclusão
        if 'excluir' in request.POST and equipamento_instance:
            equipamento_instance.delete()
            messages.success(request, 'Equipamento excluído com sucesso!')
            return redirect('cadastro_equipamento_consolidado')

        # Cadastro / edição
        if 'patrimonio' in request.POST:
            form = EquipamentoForm(request.POST, instance=equipamento_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Equipamento salvo com sucesso!')
                return redirect('cadastro_equipamento_consolidado')
            else:
                errors = iterando_erro(form)
                messages.error(request, 'Verifique os campos e tente novamente.')
    else:
        form = EquipamentoForm(instance=equipamento_instance)

    # Equipamentos da tabela
    equipamentos = Equipamento.objects.select_related('unidade').order_by('unidade__nome', 'patrimonio')
    if selected_projeto:
        equipamentos = equipamentos.filter(unidade__projeto_id=selected_projeto)

    equipamentos_cadastro = EquipamentoCadastro.objects.all().order_by('nome')

    return render(request, 'cadastro_equipamento_consolidado.html', {
        'projetos': projetos,
        'unidades': unidades,
        'form': form,
        'selected_projeto': selected_projeto,
        'selected_unidade': selected_unidade,
        'equipamentos': equipamentos,
        'equipamentos_cadastro': equipamentos_cadastro,
        'equipamento_id': equipamento_id,
    })

@login_required(login_url='login')
def associar_unidade_manage(request, pk=None, action=None):
    """
    View única para criar, editar e excluir associações
    entre prefixo de nome de máquina e unidades.
    """

    # --- EXCLUSÃO ---
    if action == 'delete' and pk:
        associacao = get_object_or_404(UnidadeAssociacao, pk=pk)
        prefixo = associacao.prefixo_nome
        associacao.delete()

        # Desassocia as máquinas com o prefixo
        Maquina.objects.filter(nome__startswith=prefixo).update(unidade_associada=None)
        messages.success(request, f"Associação com prefixo '{prefixo}' foi excluída.")
        return redirect('associar-unidade-manage')

    # --- EDIÇÃO OU CRIAÇÃO ---
    if pk and action == 'edit':
        associacao = get_object_or_404(UnidadeAssociacao, pk=pk)
        form = UnidadeAssociacaoForm(request.POST or None, instance=associacao)
    else:
        associacao = None
        form = UnidadeAssociacaoForm(request.POST or None)

    # --- SALVAR ---
    if request.method == 'POST' and form.is_valid():
        prefixo = form.cleaned_data['prefixo_nome']
        unidade = form.cleaned_data['unidade']

        # Verifica duplicidade
        qs = UnidadeAssociacao.objects.filter(prefixo_nome=prefixo)
        if associacao:
            qs = qs.exclude(pk=associacao.pk)

        if qs.exists():
            form.add_error(None, "Este prefixo já está associado a uma unidade.")
        else:
            associacao = form.save()

            # Atualiza máquinas que começam com o prefixo
            Maquina.objects.filter(nome__startswith=prefixo).update(unidade_associada=unidade)

            if pk and action == 'edit':
                messages.success(request, f"Associação '{prefixo}' atualizada com sucesso.")
            else:
                messages.success(request, f"Associação '{prefixo}' criada com sucesso.")
            return redirect('associar_unidade')

    # --- LISTAGEM E DADOS DO TEMPLATE ---
    projetos = Projeto.objects.all()
    unidades = Unidade.objects.select_related("projeto").order_by("projeto__nome", "nome")
    associacoes = UnidadeAssociacao.objects.select_related('unidade__projeto').all()

    context = {
        'form': form,
        'associacoes': associacoes,
        'projetos': projetos,
        'unidades': unidades,
        'editando': bool(associacao),
        'associacao_edit': associacao,
    }

    return render(request, 'associar_unidade.html', context)

@login_required(login_url='login')
def modelo_fornecedor_manage(request, pk=None, action=None):
    # Excluir
    if action == 'delete' and pk:
        associacao = get_object_or_404(ModeloFornecedor, pk=pk)
        modelo = associacao.modelo
        associacao.delete()

        # Opcional: limpar fornecedor_associado das máquinas desse modelo
        Maquina.objects.filter(placa_mae=modelo).update(fornecedor_associado=None)

        messages.success(request, f"Associação do modelo '{modelo}' excluída com sucesso.")
        return redirect('modelo-fornecedor-manage')

    # Editar ou Criar
    if pk and action == 'edit':
        associacao = get_object_or_404(ModeloFornecedor, pk=pk)
        form = ModeloFornecedorForm(request.POST or None, instance=associacao)
    else:
        associacao = None
        form = ModeloFornecedorForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        modelo = form.cleaned_data['modelo']
        fornecedor = form.cleaned_data['fornecedor']

        # Verifica duplicidade
        qs = ModeloFornecedor.objects.filter(modelo=modelo, fornecedor=fornecedor)
        if associacao:
            qs = qs.exclude(pk=associacao.pk)

        if qs.exists():
            form.add_error(None, "Essa associação modelo-fornecedor já existe.")
        else:
            form.save()
            # Atualiza máquinas desse modelo
            Maquina.objects.filter(placa_mae=modelo).update(fornecedor_associado=fornecedor)
            if pk and action == 'edit':
                messages.success(request, f"Associação do modelo '{modelo}' atualizada com sucesso.")
            else:
                messages.success(request, f"Associação do modelo '{modelo}' criada com sucesso.")
            return redirect('modelo-fornecedor-manage')

    # Listagem
    associacoes = ModeloFornecedor.objects.all().order_by('modelo')
    return render(request, 'modelo_fornecedor.html', {
        'form': form,
        'associacoes': associacoes,
        'editando': bool(associacao),
        'associacao_edit': associacao,
    })



# Deletar Máquina
@login_required(login_url='login')
def deletar_maquina(request, pk):
    if request.method == 'POST':
        maquina = get_object_or_404(Maquina, pk=pk)
        maquina.delete()
    return redirect('maquinas_equipamentos_por_unidade')


# Deletar Equipamento
@login_required(login_url='login')
def deletar_equipamento(request, pk):
    if request.method == 'POST':
        equipamento = get_object_or_404(Equipamento, pk=pk)
        equipamento.delete()
    return redirect('maquinas_equipamentos_por_unidade')

@login_required(login_url='login')
def apagar_todas_maquinas(request):
    if request.method == 'POST':
        Maquina.objects.all().delete()
        messages.success(request, "Todas as máquinas foram apagadas com sucesso.")
    return redirect('maquinas_equipamentos_por_unidade')

@login_required(login_url='login')
def maquinas_equipamentos_por_unidade(request):
    projetos = Projeto.objects.order_by('nome')

    # Filtros
    projeto_id = request.GET.get('projeto')
    unidade_id = request.GET.get('unidade')
    status_maquina = request.GET.get('status')
    tipo_equipamento = request.GET.get('tipo')
    tempo_off_min = request.GET.get('tempo_off_min')
    fornecedor_associado = request.GET.get('fornecedor')
    processadores_filtro = request.GET.getlist('processador')
    memoria_filtro = request.GET.get('memoria')  # ✅ apenas um valor

    print(memoria_filtro)

    # Unidades
    if projeto_id:
        unidades = Unidade.objects.filter(projeto_id=projeto_id).order_by('nome')
    else:
        unidades = Unidade.objects.order_by('nome')

    # --- Base QuerySets ---
    maquinas_qs = Maquina.objects.select_related('unidade_associada').all()
    equipamentos_qs = Equipamento.objects.select_related('unidade').all()

    # --- Aplicando filtros ---
    if projeto_id:
        maquinas_qs = maquinas_qs.filter(unidade_associada__projeto_id=projeto_id)
        equipamentos_qs = equipamentos_qs.filter(unidade__projeto_id=projeto_id)
    if unidade_id:
        maquinas_qs = maquinas_qs.filter(unidade_associada_id=unidade_id)
        equipamentos_qs = equipamentos_qs.filter(unidade_id=unidade_id)
    if status_maquina:
        maquinas_qs = maquinas_qs.filter(status=status_maquina)
    if fornecedor_associado:
        maquinas_qs = maquinas_qs.filter(fornecedor_associado=fornecedor_associado)
    if tipo_equipamento:
        equipamentos_qs = equipamentos_qs.filter(nome=tipo_equipamento)
    if tempo_off_min:
        try:
            tempo_off_min_val = int(tempo_off_min)
            maquinas_qs = maquinas_qs.filter(tempo_off_dias__gte=tempo_off_min_val)
        except ValueError:
            pass
    if processadores_filtro:
        from django.db.models import Q
        query = Q()
        for proc in processadores_filtro:
            query |= Q(processador__icontains=proc)
        maquinas_qs = maquinas_qs.filter(query)
    if memoria_filtro:
        try:
            # Substitui vírgula por ponto
            memoria_val = float(memoria_filtro.replace(',', '.'))
            maquinas_qs = maquinas_qs.filter(memoria_total=memoria_val)
        except ValueError:
            pass


    # --- Atualiza unidade associada automaticamente ---
    associacoes = list(UnidadeAssociacao.objects.select_related('unidade').all())
    associacoes_dict = {a.prefixo_nome: a.unidade for a in associacoes}

    maquinas = list(maquinas_qs)
    maquinas_para_atualizar = []
    for m in maquinas:
        unidade_encontrada = None
        for i in range(len(m.nome), 0, -1):
            prefixo = m.nome[:i]
            if prefixo in associacoes_dict:
                unidade_encontrada = associacoes_dict[prefixo]
                break
        if unidade_encontrada and m.unidade_associada != unidade_encontrada:
            m.unidade_associada = unidade_encontrada
            maquinas_para_atualizar.append(m)

    if maquinas_para_atualizar:
        Maquina.objects.bulk_update(maquinas_para_atualizar, ['unidade_associada'])

    # --- Organização ---
    maquinas.sort(key=lambda x: (x.unidade_associada.nome if x.unidade_associada else '', x.nome))
    for m in maquinas:
        m.unidade_associada_display = m.unidade_associada or ''
        m.memoria_total_display = f"{int(m.memoria_total)},0" if m.memoria_total and m.memoria_total >= 1 else '-'
        m.fornecedor_associado_display = m.fornecedor_associado if m.fornecedor_associado else '-'

    equipamentos = list(equipamentos_qs.order_by('unidade__nome', 'nome'))

    cadastros = {ec.nome: ec.tipo for ec in EquipamentoCadastro.objects.all()}
    equipamentos_para_salvar = []
    for e in equipamentos:
        if not e.tipo and e.nome in cadastros:
            e.tipo = cadastros[e.nome]
            equipamentos_para_salvar.append(e)
    if equipamentos_para_salvar:
        Equipamento.objects.bulk_update(equipamentos_para_salvar, ['tipo'])

    # 🔹 Agora os combos só mostram dados das máquinas filtradas
    processadores = (
        maquinas_qs.exclude(processador__isnull=True)
        .exclude(processador__exact='')
        .values_list('processador', flat=True)
        .distinct()
        .order_by('processador')
    )

    fornecedores = (
        maquinas_qs.exclude(fornecedor_associado__isnull=True)
        .exclude(fornecedor_associado__exact='')
        .values_list('fornecedor_associado', flat=True)
        .distinct()
        .order_by('fornecedor_associado')
    )

    # 🔹 Opções únicas de memória RAM (para o select) — todas as memórias do banco
    memorias = (
        Maquina.objects.exclude(memoria_total__isnull=True)
        .values_list('memoria_total', flat=True)
        .distinct()
        .order_by('memoria_total')
    )

    return render(request, 'maquinas_equipamentos.html', {
        'projetos': projetos,
        'unidades': unidades,
        'fornecedores': fornecedores,
        'processadores': processadores,
        'memorias': memorias,
        'maquinas': maquinas,
        'equipamentos': equipamentos,
        'filtros': {
            'projeto_id': projeto_id or '',
            'unidade_id': unidade_id or '',
            'status_maquina': status_maquina or '',
            'tipo_equipamento': tipo_equipamento or '',
            'tempo_off_min': tempo_off_min or '',
            'fornecedor_associado': fornecedor_associado or '',
            'processador': processadores_filtro,
            'memoria': memoria_filtro or '',
        }
    })




@login_required(login_url='login')
def exportar_maquinas_excel(request):
    # Pega os mesmos filtros da tela
    projeto_id = request.GET.get('projeto')
    unidade_id = request.GET.get('unidade')
    status_maquina = request.GET.get('status')
    tipo_equipamento = request.GET.get('tipo')
    tempo_off_min = request.GET.get('tempo_off_min')
    fornecedor_associado = request.GET.get('fornecedor')

    maquinas = Maquina.objects.all()
    equipamentos = Equipamento.objects.all()

    if projeto_id:
        maquinas = maquinas.filter(unidade_associada__projeto_id=projeto_id)
        equipamentos = equipamentos.filter(unidade__projeto_id=projeto_id)
    if unidade_id:
        maquinas = maquinas.filter(unidade_associada_id=unidade_id)
        equipamentos = equipamentos.filter(unidade_id=unidade_id)
    if status_maquina:
        maquinas = maquinas.filter(status=status_maquina)
    if fornecedor_associado:
        maquinas = maquinas.filter(fornecedor_associado=fornecedor_associado)
    if tipo_equipamento:
        equipamentos = equipamentos.filter(nome=tipo_equipamento)
    if tempo_off_min:
        try:
            tempo_off_min_val = int(tempo_off_min)
            maquinas = maquinas.filter(tempo_off_dias__gte=tempo_off_min_val)
        except ValueError:
            pass

    # Cria workbook e worksheet
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Máquinas"

    # Cabeçalhos
    ws1.append([
        "Unidade", "Nome", "Tag", "SO", "Processador",
        "RAM (GB)", "Placa-mãe", "Fabricante", "Disco",
        "Disco (GB)", "Fornecedor", "Tempo OFF", "Status"
    ])

    # Linhas das máquinas
    for m in maquinas:
        ws1.append([
            str(m.unidade_associada),
            m.nome,
            m.tag,
            m.sistema_operacional,
            m.processador,
            m.memoria_total,
            m.placa_mae,
            m.fabricante_placa_mae,
            m.disco,
            m.tamanho_disco,
            m.fornecedor_associado,
            f"{m.tempo_off_dias}d {m.tempo_off_horas}h {m.tempo_off_minutos}m",
            m.status,
        ])

    # Nova aba para equipamentos
    ws2 = wb.create_sheet("Equipamentos")
    ws2.append(["Unidade", "Nome","Setor", "Tipo", "Patrimônio", "Marca", "Modelo"])
    for e in equipamentos:
        ws2.append([
            str(e.unidade),
            e.nome,
            e.setor,
            e.tipo,
            e.patrimonio,
            e.marca,
            e.modelo,
        ])

    # Resposta HTTP para download
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="maquinas_equipamentos.xlsx"'
    wb.save(response)
    return response

############### CONSOLIDADO ######################

from django.db.models import Q,Count
from django.shortcuts import render
from .models import Projeto, Unidade, ConsolidadoMaquinas

from django.db.models import Q

from django.db.models import Count, Q

from django.db.models import Count, OuterRef, Subquery, Q

from django.db.models import OuterRef, Subquery, Count, F, Value, CharField, Case, When, Q

@login_required(login_url='login')
def relatorio_maquinas_por_projeto(request):
    projetos = Projeto.objects.all().order_by('nome')
    projeto_id = request.GET.get('projeto')
    unidades_data = []
    total_geral_prevista = 0
    total_geral_atual = 0
    total_geral_paineis = 0

    equipamentos_totais_previstos = '-'
    equipamentos_totais_atuais = '-'

    if projeto_id:
        unidades = Unidade.objects.filter(projeto_id=projeto_id).order_by('nome')

        for unidade in unidades:
            # Quantidade atual de máquinas (sem painéis)
            qtd_atual = unidade.maquinas_associadas.filter(~Q(nome__icontains='painel')).count()
            # Quantidade de painéis
            total_paineis = unidade.maquinas_associadas.filter(nome__icontains='painel').count()
            # Quantidade prevista (consolidado)
            consolidado = ConsolidadoMaquinas.objects.filter(projeto_id=projeto_id, unidade=unidade).first()
            qtd_prevista = consolidado.quantidade if consolidado else 0

            # Equipamentos previstos (ConsolidadoEquipamento)
            consolidado_equipamentos = ConsolidadoEquipamento.objects.filter(
                projeto_id=projeto_id,
                unidade=unidade
            ).select_related('equipamento')

            equipamentos_previstos = ', '.join(
                [f"{ce.equipamento.nome} ({ce.equipamento.tipo}) {ce.quantidade}" for ce in consolidado_equipamentos]
            ) if consolidado_equipamentos.exists() else '-'

            # Agrupar equipamentos atuais (por nome e tipo)
            equipamentos_agrupados = (
                Equipamento.objects
                .filter(unidade=unidade)
                .values('nome', 'tipo')
                .annotate(quantidade=Count('id'))
                .order_by('nome', 'tipo')
            )

            # Substituir 'IMPRESSORA' por emoji e formatar
            equipamentos_atuais = ', '.join([
                f"{item['nome'].replace('IMPRESSORA', '🖨️')} ({item['tipo']}) {item['quantidade']}"
                for item in equipamentos_agrupados
            ]) if equipamentos_agrupados else '-'

            # 🔹 Ajustes de texto conforme solicitado
            equipamentos_atuais = (
                equipamentos_atuais
                .replace('(MULTIFUNCIONAL)', '(MULTI)')
                .replace('TÉRMICA (BOLETO)', '(TÉRMICA)')
            )

            # Montar dados da unidade
            unidades_data.append({
                'unidade': unidade.nome,
                'qtd_prevista': qtd_prevista,
                'equipamentos_previstos': equipamentos_previstos,
                'qtd_atual': qtd_atual,
                'equipamentos_atuais': equipamentos_atuais,
                'total_paineis': total_paineis,
            })

            # Somatórios gerais
            total_geral_prevista += qtd_prevista
            total_geral_atual += qtd_atual
            total_geral_paineis += total_paineis

        # --- Totais Gerais de Equipamentos por Projeto ---
        totais_previstos = (
            ConsolidadoEquipamento.objects
            .filter(projeto_id=projeto_id)
            .values('equipamento__nome', 'equipamento__tipo')
            .annotate(total=Sum('quantidade'))
            .order_by('equipamento__nome', 'equipamento__tipo')
        )
        equipamentos_totais_previstos = ', '.join([
            f"{item['equipamento__nome']} ({item['equipamento__tipo']}) {item['total']}"
            for item in totais_previstos
        ]) if totais_previstos else '-'

        totais_atuais = (
            Equipamento.objects
            .filter(unidade__projeto_id=projeto_id)
            .values('nome', 'tipo')
            .annotate(total=Count('id'))
            .order_by('nome', 'tipo')
        )
        equipamentos_totais_atuais = ', '.join([
            f"{item['nome'].replace('IMPRESSORA', '🖨️')} ({item['tipo']}) {item['total']}"
            for item in totais_atuais
        ]) if totais_atuais else '-'

        equipamentos_totais_atuais = (
            equipamentos_totais_atuais
            .replace('(MULTIFUNCIONAL)', '(MULTI)')
            .replace('TÉRMICA (BOLETO)', '(TÉRMICA)')
        )

    context = {
        'projetos': projetos,
        'projeto_id': projeto_id,
        'unidades_data': unidades_data,
        'total_geral_prevista': total_geral_prevista,
        'total_geral_atual': total_geral_atual,
        'total_geral_paineis': total_geral_paineis,
        'equipamentos_totais_previstos': equipamentos_totais_previstos,
        'equipamentos_totais_atuais': equipamentos_totais_atuais,
    }
    return render(request, 'quantidade_maquina_por_unidade.html', context)







from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ConsolidadoMaquinas, Projeto, Unidade
from .forms import ConsolidadoMaquinasForm

@login_required(login_url='login')
def consolidado_maquinas(request):
    # Todos os registros para listagem
    queryset = ConsolidadoMaquinas.objects.select_related('projeto', 'unidade').order_by('projeto', 'unidade')

    # ID de edição
    edit_id = request.POST.get('edit') or request.GET.get('edit')
    obj = ConsolidadoMaquinas.objects.filter(id=edit_id).first() if edit_id else None

    # Lista de projetos
    projetos = Projeto.objects.all().order_by('nome')

    # Definir projeto selecionado
    if request.method == 'POST':
        selected_projeto = request.POST.get('projeto') or ''
    elif obj:
        selected_projeto = str(obj.projeto.id)
    else:
        selected_projeto = request.GET.get('projeto') or ''

    # Definir unidades (se tiver projeto selecionado)
    if selected_projeto:
        unidades = Unidade.objects.filter(projeto_id=selected_projeto).order_by('nome')
    else:
        unidades = Unidade.objects.none()

    # Unidade selecionada
    if request.method == 'POST':
        selected_unidade = request.POST.get('unidade') or ''
    elif obj:
        selected_unidade = str(obj.unidade.id)
    else:
        selected_unidade = ''

    # Processamento POST (criar, editar ou deletar)
    if request.method == 'POST':
        # Exclusão
        if 'delete' in request.POST:
            obj_del = get_object_or_404(ConsolidadoMaquinas, pk=request.POST.get('delete'))
            obj_del.delete()
            messages.success(request, 'Registro removido com sucesso!')
            return redirect('consolidado_maquinas')

        # Criação/Edição
        form = ConsolidadoMaquinasForm(request.POST, instance=obj)
        form.fields['unidade'].queryset = unidades

        if form.is_valid():
            form.save()
            messages.success(request, f'Registro {"atualizado" if obj else "criado"} com sucesso!')
            return redirect('consolidado_maquinas')
    else:
        # GET (exibe formulário)
        form = ConsolidadoMaquinasForm(instance=obj)
        form.fields['unidade'].queryset = unidades

    return render(request, 'consolidado_maquinas.html', {
        'form': form,
        'queryset': queryset,
        'edit_obj': obj,
        'projetos': projetos,
        'unidades': unidades,
        'selected_projeto': selected_projeto,
        'selected_unidade': selected_unidade,
    })



@login_required(login_url='login')
def consolidado_equipamentos(request):
    queryset = ConsolidadoEquipamento.objects.select_related('projeto', 'unidade', 'equipamento').order_by('projeto', 'unidade', 'equipamento')

    edit_id = request.POST.get('edit') or request.GET.get('edit')
    obj = ConsolidadoEquipamento.objects.filter(id=edit_id).first() if edit_id else None

    projetos = Projeto.objects.all().order_by('nome')
    selected_projeto = request.POST.get('projeto') or request.GET.get('projeto')

    if selected_projeto:
        unidades = Unidade.objects.filter(projeto_id=selected_projeto).order_by('nome')
    else:
        unidades = Unidade.objects.none()

    selected_unidade = request.POST.get('unidade') or (str(obj.unidade.id) if obj else '')

    if request.method == 'POST':
        # Exclusão
        if 'delete' in request.POST:
            obj_del = get_object_or_404(ConsolidadoEquipamento, pk=request.POST.get('delete'))
            obj_del.delete()
            messages.success(request, 'Registro removido com sucesso!')
            return redirect('consolidado_equipamentos')

        # Criação / Edição
        form = ConsolidadoEquipamentoForm(request.POST, instance=obj)
        form.fields['unidade'].queryset = unidades

        if form.is_valid():
            form.save()
            messages.success(request, f'Registro {"atualizado" if obj else "criado"} com sucesso!')
            return redirect('consolidado_equipamentos')
    else:
        form = ConsolidadoEquipamentoForm(instance=obj)
        form.fields['unidade'].queryset = unidades

    return render(request, 'consolidado_equipamentos.html', {
        'form': form,
        'queryset': queryset,
        'edit_obj': obj,
        'projetos': projetos,
        'unidades': unidades,
        'selected_projeto': selected_projeto,
        'selected_unidade': selected_unidade,
    })

import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import TicketManutencao
from .forms import TicketManutencaoForm

@login_required(login_url='login')
def novo_ticket(request):
    if request.method == 'POST':
        form = TicketManutencaoForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            # Gerar ticket ID #AAAAMMDD-XXX
            hoje = date.today()
            prefixo = hoje.strftime("%Y%m%d")
            # Encontrar o último ticket de hoje
            ultimo_ticket = TicketManutencao.objects.filter(ticket_id__startswith=f'#{prefixo}').order_by('-ticket_id').first()
            if ultimo_ticket:
                # Extrair os últimos 3 digitos e somar 1
                seq = int(ultimo_ticket.ticket_id.split('-')[1]) + 1
            else:
                seq = 1
            
            ticket.ticket_id = f"#{prefixo}-{seq:03d}"
            
            # Capturar array json dos pentes de RAM
            pentes_json = request.POST.get('ram_pentes_detalhes_json', '[]')
            try:
                ticket.ram_pentes_detalhes = json.loads(pentes_json)
            except:
                ticket.ram_pentes_detalhes = []
                
            ticket.save()
            messages.success(request, f"Ticket {ticket.ticket_id} criado com sucesso!")
            return redirect('novo_ticket')
        else:
            messages.error(request, "Erro ao criar ticket. Verifique os campos.")
    else:
        # Tentar preencher tecnico inicialmente com o usuário da sessão
        form = TicketManutencaoForm()
        
    return render(request, 'novo_ticket.html', {'form': form})

@login_required(login_url='login')
def editar_ticket(request, pk):
    ticket = get_object_or_404(TicketManutencao, pk=pk)
    if request.method == 'POST':
        form = TicketManutencaoForm(request.POST, instance=ticket)
        if form.is_valid():
            t = form.save(commit=False)
            pentes_json = request.POST.get('ram_pentes_detalhes_json', '[]')
            try:
                t.ram_pentes_detalhes = json.loads(pentes_json)
            except:
                t.ram_pentes_detalhes = []
            t.save()
            messages.success(request, f"Ticket {t.ticket_id} atualizado com sucesso!")
            return redirect('relatorio_tickets')
        else:
            messages.error(request, "Erro ao atualizar ticket. Verifique os campos.")
    else:
        form = TicketManutencaoForm(instance=ticket)
    return render(request, 'novo_ticket.html', {'form': form, 'ticket': ticket})

from collections import defaultdict

@login_required(login_url='login')
def relatorio_tickets(request):
    from .models import TicketManutencao
    tickets = TicketManutencao.objects.all().order_by('-data_abertura', '-id')
    return render(request, 'relatorio_tickets.html', {'tickets': tickets})

@login_required(login_url='login')
def relatorio_pecas_defeituosas(request):
    from .models import TicketManutencao
    tickets = TicketManutencao.objects.filter(status__in=['ABERTO', 'AGUARDANDO PEÇAS'])

    pecas_ruins = defaultdict(lambda: {'total': 0, 'tickets': []})
    pecas_necessarias = defaultdict(lambda: {'total': 0, 'tickets': []})

    def add(d, key, ticket_id):
        d[key]['total'] += 1
        d[key]['tickets'].append(ticket_id)

    for t in tickets:
        is_desktop = t.tipo_equipamento == 'Desktop'
        tipo_display = 'Gabinete' if is_desktop else t.tipo_equipamento

        if t.gabinete_estado == 'Ruim':
            if t.tipo_equipamento == 'Impressora' and t.impressora_tipo:
                key = f"Impressora {t.impressora_tipo} ({t.equipamento_modelo})"
            elif is_desktop:
                key = f"{tipo_display} ({t.equipamento_modelo})"
            else:
                key = f"{tipo_display} ({t.equipamento_modelo})"
            add(pecas_ruins, key, t.ticket_id)

        if is_desktop:
            if t.processador_estado == 'Ruim':
                key = f"Processador {t.processador_nome or ''} ({t.processador_socket or ''})"
                add(pecas_ruins, key, t.ticket_id)

            if t.placa_mae_estado == 'Ruim':
                key = f"Placa-Mãe ({t.processador_socket or ''} / {t.ram_tipo or ''})"
                add(pecas_ruins, key, t.ticket_id)

            if t.armazenamento_estado == 'Ruim':
                key = f"{t.armazenamento_tipo or ''} {t.armazenamento_capacidade or ''}"
                add(pecas_ruins, key, t.ticket_id)
            elif t.armazenamento_estado == 'Não contém':
                key = "Unidade de Armazenamento (Necessário)"
                add(pecas_necessarias, key, t.ticket_id)

            if t.ram_ausente:
                key = f"Memória RAM {t.ram_tipo or ''} (Necessária)"
                add(pecas_necessarias, key, t.ticket_id)
            else:
                for pente in t.ram_pentes_detalhes:
                    if pente.get('estado') == 'Ruim':
                        capacidade = str(pente.get('capacidade', ''))
                        if capacidade.isdigit():
                            capacidade += "GB"
                        key = f"Memória RAM {t.ram_tipo or ''} {capacidade}"
                        add(pecas_ruins, key.strip(), t.ticket_id)

            if t.fonte_estado == 'Ruim':
                key = f"Fonte {t.fonte_tipo or ''}"
                add(pecas_ruins, key, t.ticket_id)
            elif t.fonte_estado == 'Não contém':
                key = "Fonte (Necessária)"
                add(pecas_necessarias, key, t.ticket_id)

            if t.cooler_estado == 'Ruim':
                key = f"Cooler ({t.processador_socket or ''})"
                add(pecas_ruins, key, t.ticket_id)

    lista_ruins = sorted([{'nome': k, 'total': v['total'], 'tickets': v['tickets']} for k, v in pecas_ruins.items()], key=lambda x: x['nome'])
    lista_necessarias = sorted([{'nome': k, 'total': v['total'], 'tickets': v['tickets']} for k, v in pecas_necessarias.items()], key=lambda x: x['nome'])

    condenados = TicketManutencao.objects.filter(status='CONDENADO').order_by('-data_abertura')
    impressoras = TicketManutencao.objects.filter(
        tipo_equipamento='Impressora'
    ).exclude(status='FINALIZADO').order_by('-data_abertura')

    context = {
        'lista_ruins': lista_ruins,
        'lista_necessarias': lista_necessarias,
        'total_tickets': tickets.count(),
        'condenados': condenados,
        'impressoras': impressoras,
    }
    return render(request, 'relatorio_pecas.html', context)

@csrf_exempt
@require_POST
@login_required(login_url='login')
def alterar_status_ticket(request, ticket_id):
    from .models import TicketManutencao
    import json
    try:
        data = json.loads(request.body)
        novo_status = data.get('status')
        ticket = TicketManutencao.objects.get(id=ticket_id)
        ticket.status = novo_status
        ticket.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)