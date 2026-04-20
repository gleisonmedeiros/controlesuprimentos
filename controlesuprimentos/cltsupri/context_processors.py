from django.db.models import F
from .models import Suprimento

def toners_baixos(request):
    if request.user.is_authenticated:
        toners_baixo = Suprimento.objects.filter(quantidade_minima__gt=0, quantidade__lte=F('quantidade_minima'))
        return {'toners_baixo': toners_baixo}
    return {'toners_baixo': None}
