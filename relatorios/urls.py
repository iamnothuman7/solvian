"""URLs do app relatorios."""

from django.urls import path
from relatorios.views import GerarPropostaPDFView, GerarContratoPDFView

app_name = 'relatorios'

urlpatterns = [
    path('proposta/pdf/', GerarPropostaPDFView.as_view(), name='gerar_proposta_pdf'),
    path('contrato/pdf/', GerarContratoPDFView.as_view(), name='gerar_contrato_pdf'),
]
