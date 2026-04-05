"""URLs do app core."""

from django.urls import path
from core.views import HomeView, DimensionamentoView, ManutencaoView, SobreView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dimensionamento/', DimensionamentoView.as_view(), name='dimensionamento'),
    path('manutencao/', ManutencaoView.as_view(), name='manutencao'),
    path('sobre/', SobreView.as_view(), name='sobre'),
]
