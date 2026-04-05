"""
Motor de cálculo de dimensionamento de sistemas fotovoltaicos.
Realiza todos os cálculos técnicos e financeiros para gerar a proposta.
"""

import math
import pandas as pd
from django.conf import settings


class CalculadoraSolar:
    """
    Calculadora de dimensionamento de sistemas fotovoltaicos.

    Recebe dados de consumo, irradiação solar e configurações do telhado
    para calcular o sistema ideal: potência, quantidade de painéis,
    geração estimada, investimento e tempo de retorno (payback).
    """

    def __init__(
        self,
        consumo_mensal_kwh,
        irradiacao_media,
        dados_mensais=None,
        tarifa_energia=0.85,
        eficiencia_sistema=None,
        potencia_painel_wp=None,
        custo_por_wp=None,
        inclinacao=15,
        orientacao='norte',
        tipo_telhado='ceramica',
        area_disponivel=None,
    ):
        """
        Inicializa a calculadora com os parâmetros do projeto.

        Args:
            consumo_mensal_kwh (float): Consumo médio mensal em kWh
            irradiacao_media (float): Irradiação média anual em kWh/m²/dia (HSP)
            dados_mensais (dict): Dados mensais de irradiação (opcional)
            tarifa_energia (float): Tarifa de energia em R$/kWh
            eficiencia_sistema (float): Eficiência do sistema (0 a 1)
            potencia_painel_wp (int): Potência de cada painel em Wp
            custo_por_wp (float): Custo por Watt-pico instalado (R$/Wp)
            inclinacao (float): Inclinação do telhado em graus
            orientacao (str): Orientação do telhado
            tipo_telhado (str): Tipo de telhado
            area_disponivel (float): Área disponível em m² (opcional)
        """
        self.consumo_mensal_kwh = consumo_mensal_kwh
        self.irradiacao_media = irradiacao_media
        self.dados_mensais = dados_mensais or {}
        self.tarifa_energia = tarifa_energia

        # Valores configuráveis via settings ou parâmetros
        self.eficiencia_sistema = eficiencia_sistema or getattr(
            settings, 'EFICIENCIA_SISTEMA', 0.80
        )
        self.potencia_painel_wp = potencia_painel_wp or getattr(
            settings, 'POTENCIA_PAINEL_WP', 550
        )
        self.custo_por_wp = custo_por_wp or getattr(
            settings, 'CUSTO_POR_WP', 4.50
        )

        self.inclinacao = inclinacao
        self.orientacao = orientacao
        self.tipo_telhado = tipo_telhado
        self.area_disponivel = area_disponivel

    def calcular(self):
        """
        Executa todos os cálculos e retorna o resultado completo.

        Returns:
            dict: Resultado completo do dimensionamento com dados técnicos,
                  financeiros e análise mensal detalhada.
        """
        # Fator de correção pela orientação e inclinação do telhado
        fator_orientacao = self._calcular_fator_orientacao()

        # Irradiação efetiva considerando orientação
        irradiacao_efetiva = self.irradiacao_media * fator_orientacao

        # =====================================================================
        # CÁLCULO DA POTÊNCIA NECESSÁRIA
        # =====================================================================

        # Potência necessária (kWp) = Consumo / (HSP x 30 dias x Eficiência)
        potencia_kwp = self.consumo_mensal_kwh / (
            irradiacao_efetiva * 30 * self.eficiencia_sistema
        )
        potencia_kwp = round(potencia_kwp, 2)

        # =====================================================================
        # QUANTIDADE DE PAINÉIS
        # =====================================================================

        qtd_paineis = math.ceil(
            (potencia_kwp * 1000) / self.potencia_painel_wp
        )

        # Potência real do sistema (baseada nos painéis inteiros)
        potencia_real_kwp = round(
            (qtd_paineis * self.potencia_painel_wp) / 1000, 2
        )

        # =====================================================================
        # GERAÇÃO ESTIMADA
        # =====================================================================

        # Geração mensal estimada (kWh)
        geracao_mensal = round(
            potencia_real_kwp * irradiacao_efetiva * 30 * self.eficiencia_sistema, 1
        )

        # Geração anual estimada (kWh)
        geracao_anual = round(geracao_mensal * 12, 1)

        # =====================================================================
        # ÁREA NECESSÁRIA
        # =====================================================================

        # Área por painel (considerando espaçamento) ≈ 2.2 m² por painel de 550W
        area_por_painel = 2.2  # m²
        area_necessaria = round(qtd_paineis * area_por_painel, 1)

        # Verificar se cabe na área disponível
        cabe_na_area = True
        if self.area_disponivel and self.area_disponivel > 0:
            cabe_na_area = area_necessaria <= self.area_disponivel

        # =====================================================================
        # ANÁLISE FINANCEIRA
        # =====================================================================

        # Investimento total
        investimento = round(potencia_real_kwp * 1000 * self.custo_por_wp, 2)

        # Economia mensal
        economia_mensal = round(geracao_mensal * self.tarifa_energia, 2)

        # Economia anual
        economia_anual = round(economia_mensal * 12, 2)

        # Payback simples (anos)
        payback_anos = round(investimento / economia_anual, 1) if economia_anual > 0 else 0

        # Economia em 25 anos (vida útil do sistema, com reajuste de 8% a.a.)
        economia_25_anos = self._calcular_economia_25_anos(economia_anual)

        # ROI (Retorno sobre o Investimento)
        roi = round(
            ((economia_25_anos - investimento) / investimento) * 100, 1
        ) if investimento > 0 else 0

        # =====================================================================
        # ANÁLISE MENSAL DETALHADA (com Pandas)
        # =====================================================================

        analise_mensal = self._gerar_analise_mensal(
            potencia_real_kwp, fator_orientacao
        )

        # =====================================================================
        # CO₂ EVITADO
        # =====================================================================

        # Fator de emissão médio do SIN (Sistema Interligado Nacional)
        # ~0.075 tCO₂/MWh (fonte: MCTI)
        co2_evitado_anual = round(geracao_anual * 0.075 / 1000, 2)  # toneladas
        arvores_equivalentes = round(co2_evitado_anual * 14)  # ~14 árvores por tCO₂

        return {
            # Dados técnicos
            'potencia_necessaria_kwp': potencia_kwp,
            'potencia_real_kwp': potencia_real_kwp,
            'qtd_paineis': qtd_paineis,
            'potencia_painel_wp': self.potencia_painel_wp,
            'geracao_mensal_kwh': geracao_mensal,
            'geracao_anual_kwh': geracao_anual,
            'irradiacao_efetiva': round(irradiacao_efetiva, 2),
            'eficiencia_sistema': self.eficiencia_sistema,
            'fator_orientacao': round(fator_orientacao, 2),

            # Dados do telhado
            'area_necessaria_m2': area_necessaria,
            'area_disponivel_m2': self.area_disponivel,
            'cabe_na_area': cabe_na_area,
            'tipo_telhado': self.tipo_telhado,
            'inclinacao': self.inclinacao,
            'orientacao': self.orientacao,

            # Dados financeiros
            'investimento': investimento,
            'economia_mensal': economia_mensal,
            'economia_anual': economia_anual,
            'payback_anos': payback_anos,
            'economia_25_anos': economia_25_anos,
            'roi_percentual': roi,
            'tarifa_energia': self.tarifa_energia,
            'custo_por_wp': self.custo_por_wp,

            # Sustentabilidade
            'co2_evitado_toneladas': co2_evitado_anual,
            'arvores_equivalentes': arvores_equivalentes,

            # Análise mensal
            'analise_mensal': analise_mensal,
        }

    def _calcular_fator_orientacao(self):
        """
        Calcula o fator de correção pela orientação e inclinação do telhado.
        Para o hemisfério sul, a orientação ideal é Norte.
        """
        # Fatores de correção por orientação (para hemisfério sul)
        fatores_orientacao = {
            'norte': 1.00,     # Ideal
            'nordeste': 0.95,
            'noroeste': 0.95,
            'leste': 0.88,
            'oeste': 0.88,
            'sul': 0.75,       # Pior caso
        }

        fator_dir = fatores_orientacao.get(self.orientacao, 0.90)

        # Ajuste pela inclinação (ideal é ~igual à latitude do local)
        # Inclinação de 15° é considerada boa para a maioria do Brasil
        desvio_inclinacao = abs(self.inclinacao - 15) / 90
        fator_incl = 1 - (desvio_inclinacao * 0.15)  # Penalidade máxima de 15%

        return round(fator_dir * fator_incl, 4)

    def _calcular_economia_25_anos(self, economia_anual):
        """
        Calcula a economia acumulada em 25 anos considerando:
        - Reajuste da tarifa de energia: 8% ao ano
        - Degradação dos painéis: 0.5% ao ano
        """
        economia_total = 0
        for ano in range(1, 26):
            # Tarifa reajustada
            fator_tarifa = (1.08) ** (ano - 1)
            # Degradação do painel
            fator_degradacao = 1 - (0.005 * (ano - 1))
            economia_total += economia_anual * fator_tarifa * fator_degradacao
        return round(economia_total, 2)

    def _gerar_analise_mensal(self, potencia_kwp, fator_orientacao):
        """
        Gera análise mensal detalhada usando Pandas.
        Se dados mensais do satélite estiverem disponíveis, usa-os.
        Caso contrário, usa a média anual com variação sazonal estimada.
        """
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        dados = []
        for i, mes in enumerate(meses, 1):
            mes_key = str(i)

            # Obter irradiação do mês (satélite ou estimativa)
            if mes_key in self.dados_mensais and isinstance(self.dados_mensais[mes_key], dict):
                irrad = self.dados_mensais[mes_key].get('irradiacao', self.irradiacao_media)
                temp = self.dados_mensais[mes_key].get('temperatura', 25)
            else:
                irrad = self.irradiacao_media
                temp = 25

            # Dias no mês (simplificado)
            dias_no_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][i - 1]

            # Geração estimada para o mês
            geracao = round(
                potencia_kwp * irrad * dias_no_mes * self.eficiencia_sistema * fator_orientacao,
                1
            )

            # Economia do mês
            economia = round(geracao * self.tarifa_energia, 2)

            dados.append({
                'mes': mes,
                'mes_num': i,
                'irradiacao': round(irrad, 2),
                'temperatura': round(temp, 1),
                'dias': dias_no_mes,
                'geracao_kwh': geracao,
                'economia_rs': economia,
            })

        # Usar Pandas para processar e enriquecer os dados
        df = pd.DataFrame(dados)

        # Adicionar percentual relativo ao máximo
        max_geracao = df['geracao_kwh'].max()
        if max_geracao > 0:
            df['percentual'] = (df['geracao_kwh'] / max_geracao * 100).round(0).astype(int)
        else:
            df['percentual'] = 0

        # Totalizar
        totais = {
            'geracao_anual_kwh': round(df['geracao_kwh'].sum(), 1),
            'economia_anual_rs': round(df['economia_rs'].sum(), 2),
            'irradiacao_media': round(df['irradiacao'].mean(), 2),
            'melhor_mes': df.loc[df['geracao_kwh'].idxmax(), 'mes'],
            'pior_mes': df.loc[df['geracao_kwh'].idxmin(), 'mes'],
        }

        return {
            'meses': df.to_dict('records'),
            'totais': totais,
        }
