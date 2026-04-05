"""Registro dos modelos no Django Admin."""

from django.contrib import admin
from core.models import DadosSatelite, AlertaManutencao


@admin.register(DadosSatelite)
class DadosSateliteAdmin(admin.ModelAdmin):
    """Admin para cache de dados de satélite."""
    list_display = ('latitude', 'longitude', 'irradiacao_media_anual', 'temperatura_media', 'fonte_api', 'data_consulta')
    list_filter = ('fonte_api', 'data_consulta')
    search_fields = ('latitude', 'longitude')
    readonly_fields = ('data_consulta',)


@admin.register(AlertaManutencao)
class AlertaManutencaoAdmin(admin.ModelAdmin):
    """Admin para alertas de manutenção."""
    list_display = ('tipo_alerta', 'prioridade', 'desvio_percentual', 'resolvido', 'data_alerta')
    list_filter = ('tipo_alerta', 'prioridade', 'resolvido')
    search_fields = ('descricao', 'projeto_nome')
