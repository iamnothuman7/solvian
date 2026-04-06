"""
Views do app core — Páginas principais do Solvian.
Como não há login, todas as views são públicas.
"""

import logging
from django.views.generic import TemplateView, FormView
from django.shortcuts import render
from core.forms import DimensionamentoForm, ManutencaoForm
from satelite.services import NASAPowerService
from dimensionamento.calculadora import CalculadoraSolar
from dimensionamento.ia_manutencao import PreditorManutencao

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """Página inicial do Solvian com apresentação do sistema."""
    template_name = 'home.html'


class DimensionamentoView(FormView):
    """
    View principal de dimensionamento solar.
    Recebe os dados do formulário, consulta o satélite,
    executa o cálculo e exibe o resultado.
    """
    template_name = 'core/projeto_form.html'
    form_class = DimensionamentoForm

    def form_valid(self, form):
        """Processa o formulário válido e gera o dimensionamento."""
        dados = form.cleaned_data

        # =====================================================================
        # 1. CONSULTAR DADOS DE SATÉLITE (NASA POWER)
        # =====================================================================
        dados_satelite = NASAPowerService.consultar_irradiacao(
            latitude=dados['latitude'],
            longitude=dados['longitude'],
        )

        logger.info(f'Irradiação média anual: {dados_satelite.get("irradiacao_media_anual")}')
        logger.info(f'Dados mensais keys: {list(dados_satelite.get("dados_mensais", {}).keys())}')

        # =====================================================================
        # 2. CALCULAR DIMENSIONAMENTO
        # =====================================================================
        calculadora = CalculadoraSolar(
            consumo_mensal_kwh=dados['consumo_mensal_kwh'],
            irradiacao_media=dados_satelite['irradiacao_media_anual'],
            dados_mensais=dados_satelite.get('dados_mensais', {}),
            tarifa_energia=dados['tarifa_energia'],
            potencia_painel_wp=dados.get('potencia_painel_wp', 550),
            inclinacao=dados['inclinacao_telhado'],
            orientacao=dados['orientacao'],
            tipo_telhado=dados['tipo_telhado'],
            area_disponivel=dados.get('area_disponivel'),
        )

        resultado = calculadora.calcular()

        # =====================================================================
        # 3. RENDERIZAR RESULTADO
        # =====================================================================
        contexto = {
            'form': form,
            'consumo_mensal_kwh': dados['consumo_mensal_kwh'],
            'dados_cliente': {
                'nome': dados['nome_cliente'],
                'email': dados.get('email_cliente', ''),
                'telefone': dados.get('telefone_cliente', ''),
                'endereco': dados['endereco'],
                'latitude': dados['latitude'],
                'longitude': dados['longitude'],
            },
            'dados_empresa': {
                'nome': dados.get('nome_empresa', 'Solvian Energy'),
                'telefone': dados.get('telefone_empresa', ''),
                'email': dados.get('email_empresa', ''),
            },
            'dados_satelite': dados_satelite,
            'resultado': resultado,
        }

        return render(self.request, 'dimensionamento/resultado.html', contexto)


class ManutencaoView(FormView):
    """
    View de análise de manutenção preditiva.
    Recebe dados de geração real e compara com o esperado via IA.
    """
    template_name = 'core/manutencao_form.html'
    form_class = ManutencaoForm

    def form_valid(self, form):
        """Processa a análise preditiva."""
        dados = form.cleaned_data

        # =====================================================================
        # 1. OBTER GERAÇÃO ESPERADA VIA SATÉLITE
        # =====================================================================
        dados_satelite = NASAPowerService.consultar_irradiacao(
            latitude=dados['latitude'],
            longitude=dados['longitude'],
        )

        potencia_kwp = dados['potencia_instalada_kwp']
        eficiencia = 0.80

        # Calcular geração esperada para cada mês
        geracao_esperada = []
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        dias_no_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        dados_mensais = dados_satelite.get('dados_mensais', {})
        for i in range(12):
            mes_key = str(i + 1)
            if mes_key in dados_mensais and isinstance(dados_mensais[mes_key], dict):
                irrad = dados_mensais[mes_key].get('irradiacao', dados_satelite['irradiacao_media_anual'])
            else:
                irrad = dados_satelite['irradiacao_media_anual']

            esperado = potencia_kwp * irrad * dias_no_mes[i] * eficiencia
            geracao_esperada.append(round(esperado, 1))

        # =====================================================================
        # 2. EXECUTAR ANÁLISE DE IA
        # =====================================================================
        preditor = PreditorManutencao()
        resultado_ia = preditor.analisar(
            geracao_real=dados['geracao_real_mensal'],
            geracao_esperada=geracao_esperada,
            meses=meses,
        )

        # =====================================================================
        # 3. RENDERIZAR RESULTADO
        # =====================================================================
        contexto = {
            'form': form,
            'resultado': resultado_ia,
            'dados_satelite': dados_satelite,
            'potencia_kwp': potencia_kwp,
            'geracao_real': dados['geracao_real_mensal'],
            'geracao_esperada': geracao_esperada,
        }

        return render(self.request, 'dimensionamento/manutencao_resultado.html', contexto)


class SobreView(TemplateView):
    """Página sobre o Solvian."""
    template_name = 'core/sobre.html'
