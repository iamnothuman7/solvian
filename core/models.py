"""
Modelos de dados do Solvian.
Como o sistema não armazena dados permanentemente (sem login),
os modelos servem para estruturar os dados em memória e,
opcionalmente, cachear consultas de satélite para performance.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class DadosSatelite(models.Model):
    """
    Cache de dados de irradiação solar obtidos via API NASA POWER.
    Armazena para evitar consultas repetidas para a mesma localização.
    """

    latitude = models.FloatField(
        'Latitude',
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text='Latitude do local (-90 a 90)'
    )
    longitude = models.FloatField(
        'Longitude',
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text='Longitude do local (-180 a 180)'
    )

    # Irradiação solar média anual em kWh/m²/dia
    irradiacao_media_anual = models.FloatField(
        'Irradiação Média Anual (kWh/m²/dia)',
        null=True, blank=True
    )

    # Dados mensais de irradiação como JSON
    # Formato: {"1": 5.2, "2": 5.5, ..., "12": 4.8}
    dados_mensais_json = models.TextField(
        'Dados Mensais (JSON)',
        blank=True, default='{}'
    )

    # Temperatura média anual em °C
    temperatura_media = models.FloatField(
        'Temperatura Média (°C)',
        null=True, blank=True
    )

    fonte_api = models.CharField(
        'Fonte da API',
        max_length=100,
        default='NASA POWER'
    )

    data_consulta = models.DateTimeField(
        'Data da Consulta',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Dado de Satélite'
        verbose_name_plural = 'Dados de Satélite'
        ordering = ['-data_consulta']
        # Índice para buscas por coordenadas (cache)
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f'Irradiação em ({self.latitude}, {self.longitude}) - {self.irradiacao_media_anual} kWh/m²/dia'

    @property
    def dados_mensais(self):
        """Retorna os dados mensais como dicionário Python."""
        try:
            return json.loads(self.dados_mensais_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    @dados_mensais.setter
    def dados_mensais(self, valor):
        """Define os dados mensais a partir de um dicionário."""
        self.dados_mensais_json = json.dumps(valor)


class AlertaManutencao(models.Model):
    """
    Registro de alertas de manutenção preditiva gerados pela IA.
    Usado para demonstração do sistema de detecção de anomalias.
    """

    class TipoAlerta(models.TextChoices):
        QUEDA_GERACAO = 'QUEDA', 'Queda na Geração'
        SUJEIRA = 'SUJEIRA', 'Sujeira nos Painéis'
        DEFEITO = 'DEFEITO', 'Possível Defeito'
        SOMBREAMENTO = 'SOMBRA', 'Sombreamento Detectado'
        DEGRADACAO = 'DEGRAD', 'Degradação Natural'

    class Prioridade(models.TextChoices):
        BAIXA = 'BAIXA', 'Baixa'
        MEDIA = 'MEDIA', 'Média'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Crítica'

    tipo_alerta = models.CharField(
        'Tipo de Alerta',
        max_length=10,
        choices=TipoAlerta.choices,
        default=TipoAlerta.QUEDA_GERACAO
    )

    descricao = models.TextField('Descrição do Alerta')

    geracao_real_kwh = models.FloatField(
        'Geração Real (kWh)',
        validators=[MinValueValidator(0)]
    )

    geracao_esperada_kwh = models.FloatField(
        'Geração Esperada (kWh)',
        validators=[MinValueValidator(0)]
    )

    desvio_percentual = models.FloatField(
        'Desvio Percentual (%)',
        help_text='Diferença percentual entre real e esperado'
    )

    prioridade = models.CharField(
        'Prioridade',
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA
    )

    resolvido = models.BooleanField('Resolvido', default=False)
    data_alerta = models.DateTimeField('Data do Alerta', auto_now_add=True)
    data_resolucao = models.DateTimeField('Data de Resolução', null=True, blank=True)

    # Dados do projeto (armazenados inline, sem FK, pois não há persistência)
    projeto_nome = models.CharField('Nome do Projeto', max_length=200, blank=True)
    projeto_potencia_kwp = models.FloatField('Potência do Projeto (kWp)', null=True, blank=True)

    class Meta:
        verbose_name = 'Alerta de Manutenção'
        verbose_name_plural = 'Alertas de Manutenção'
        ordering = ['-data_alerta']

    def __str__(self):
        return f'[{self.get_prioridade_display()}] {self.get_tipo_alerta_display()} - Desvio: {self.desvio_percentual:.1f}%'

    def save(self, *args, **kwargs):
        """Calcula o desvio percentual automaticamente antes de salvar."""
        if self.geracao_esperada_kwh and self.geracao_esperada_kwh > 0:
            self.desvio_percentual = (
                (self.geracao_esperada_kwh - self.geracao_real_kwh)
                / self.geracao_esperada_kwh * 100
            )
        super().save(*args, **kwargs)
