from .models import Kategorie

def kategorie(request):
    return {'kategorie_list': Kategorie.objects.all()}