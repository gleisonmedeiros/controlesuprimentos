from .models import Suprimento

def toners_baixos(request):
    """
    Injeta no contexto global de todas as views os suprimentos
    que possuem quantidade 15 ou menor.
    """
    if request.user.is_authenticated:
        toners_baixo = Suprimento.objects.filter(quantidade__lte=15)
        return {'toners_baixo': toners_baixo}
    return {'toners_baixo': None}
