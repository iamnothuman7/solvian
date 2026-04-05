"""
Módulo de Inteligência Artificial para Manutenção Preditiva.
Utiliza Scikit-learn (IsolationForest) para detectar anomalias
na geração de energia de sistemas fotovoltaicos.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class PreditorManutencao:
    """
    Sistema de detecção de anomalias para manutenção preditiva
    de sistemas fotovoltaicos.

    Utiliza o algoritmo IsolationForest do Scikit-learn para identificar
    meses em que a geração real está significativamente abaixo do esperado,
    indicando possíveis problemas como:
    - Sujeira nos painéis
    - Defeito no inversor
    - Sombreamento inesperado
    - Degradação acelerada
    """

    def __init__(self, contamination=0.15):
        """
        Inicializa o preditor de manutenção.

        Args:
            contamination (float): Proporção esperada de anomalias (0.0 a 0.5).
                                   Valores menores = mais conservador.
        """
        self.contamination = contamination
        self.modelo = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        self.scaler = StandardScaler()
        self._treinado = False

    def analisar(self, geracao_real, geracao_esperada, meses=None):
        """
        Analisa a geração real vs esperada e detecta anomalias.

        Args:
            geracao_real (list): Lista de 12 valores de geração real (kWh).
            geracao_esperada (list): Lista de 12 valores de geração esperada (kWh).
            meses (list): Nomes dos meses (opcional).

        Returns:
            dict: Resultado da análise com anomalias detectadas.
                {
                    'sucesso': bool,
                    'alertas': list,        # Lista de alertas gerados
                    'resumo': dict,         # Estatísticas gerais
                    'analise_mensal': list,  # Análise mês a mês
                    'recomendacoes': list,   # Recomendações de manutenção
                }
        """
        if meses is None:
            meses = [
                'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
            ]

        try:
            # Validar dados de entrada
            if len(geracao_real) != 12 or len(geracao_esperada) != 12:
                return {
                    'sucesso': False,
                    'erro': 'São necessários exatamente 12 valores de geração (um por mês).',
                    'alertas': [],
                    'resumo': {},
                    'analise_mensal': [],
                    'recomendacoes': [],
                }

            # =================================================================
            # PREPARAR DADOS
            # =================================================================

            df = pd.DataFrame({
                'mes': meses,
                'geracao_real': geracao_real,
                'geracao_esperada': geracao_esperada,
            })

            # Calcular desvio percentual
            df['desvio'] = np.where(
                df['geracao_esperada'] > 0,
                ((df['geracao_esperada'] - df['geracao_real']) / df['geracao_esperada'] * 100),
                0
            )

            # Calcular razão de performance (PR - Performance Ratio)
            df['performance_ratio'] = np.where(
                df['geracao_esperada'] > 0,
                df['geracao_real'] / df['geracao_esperada'],
                1.0
            )

            # =================================================================
            # TREINAR E APLICAR MODELO DE ANOMALIA
            # =================================================================

            # Features para o modelo: desvio e performance ratio
            features = df[['desvio', 'performance_ratio']].values

            # Normalizar features
            features_scaled = self.scaler.fit_transform(features)

            # Treinar e prever anomalias
            self.modelo.fit(features_scaled)
            predicoes = self.modelo.predict(features_scaled)

            # -1 = anomalia, 1 = normal
            df['anomalia'] = predicoes == -1

            # Score de anomalia (quanto menor, mais anômalo)
            scores = self.modelo.score_samples(features_scaled)
            df['score_anomalia'] = scores

            self._treinado = True

            # =================================================================
            # GERAR ALERTAS
            # =================================================================

            alertas = []
            analise_mensal = []

            for _, row in df.iterrows():
                status = 'normal'
                tipo_alerta = None
                prioridade = 'BAIXA'
                descricao = ''

                desvio = row['desvio']
                pr = row['performance_ratio']

                if row['anomalia'] or desvio > 15:
                    status = 'alerta'

                    # Classificar o tipo de problema
                    if desvio > 40:
                        tipo_alerta = 'DEFEITO'
                        prioridade = 'CRITICA'
                        descricao = (
                            f'Geração {desvio:.0f}% abaixo do esperado em {row["mes"]}. '
                            f'Possível defeito no equipamento. Verificação urgente necessária.'
                        )
                    elif desvio > 25:
                        tipo_alerta = 'SUJEIRA'
                        prioridade = 'ALTA'
                        descricao = (
                            f'Queda significativa de {desvio:.0f}% em {row["mes"]}. '
                            f'Provável acúmulo de sujeira ou sombreamento parcial.'
                        )
                    elif desvio > 15:
                        tipo_alerta = 'QUEDA'
                        prioridade = 'MEDIA'
                        descricao = (
                            f'Geração {desvio:.0f}% abaixo do esperado em {row["mes"]}. '
                            f'Monitorar nos próximos meses.'
                        )
                    else:
                        tipo_alerta = 'SOMBRA'
                        prioridade = 'BAIXA'
                        descricao = (
                            f'Leve redução detectada em {row["mes"]} '
                            f'(desvio de {desvio:.0f}%). Possível sombreamento sazonal.'
                        )

                    alertas.append({
                        'mes': row['mes'],
                        'tipo': tipo_alerta,
                        'prioridade': prioridade,
                        'descricao': descricao,
                        'desvio_percentual': round(desvio, 1),
                        'geracao_real': row['geracao_real'],
                        'geracao_esperada': row['geracao_esperada'],
                        'performance_ratio': round(pr, 3),
                    })

                analise_mensal.append({
                    'mes': row['mes'],
                    'geracao_real': row['geracao_real'],
                    'geracao_esperada': round(row['geracao_esperada'], 1),
                    'desvio_percentual': round(desvio, 1),
                    'performance_ratio': round(pr, 3),
                    'status': status,
                    'score': round(row['score_anomalia'], 3),
                })

            # =================================================================
            # GERAR RESUMO E RECOMENDAÇÕES
            # =================================================================

            total_real = df['geracao_real'].sum()
            total_esperado = df['geracao_esperada'].sum()
            desvio_global = (
                (total_esperado - total_real) / total_esperado * 100
                if total_esperado > 0 else 0
            )
            pr_media = df['performance_ratio'].mean()

            resumo = {
                'geracao_total_real': round(total_real, 1),
                'geracao_total_esperada': round(total_esperado, 1),
                'desvio_global_percentual': round(desvio_global, 1),
                'performance_ratio_media': round(pr_media, 3),
                'meses_com_anomalia': int(df['anomalia'].sum()),
                'total_alertas': len(alertas),
                'alertas_criticos': sum(1 for a in alertas if a['prioridade'] == 'CRITICA'),
                'alertas_altos': sum(1 for a in alertas if a['prioridade'] == 'ALTA'),
                'saude_sistema': self._classificar_saude(pr_media, len(alertas)),
            }

            recomendacoes = self._gerar_recomendacoes(alertas, pr_media, desvio_global)

            return {
                'sucesso': True,
                'alertas': alertas,
                'resumo': resumo,
                'analise_mensal': analise_mensal,
                'recomendacoes': recomendacoes,
            }

        except Exception as e:
            logger.error(f'Erro na análise preditiva: {e}')
            return {
                'sucesso': False,
                'erro': str(e),
                'alertas': [],
                'resumo': {},
                'analise_mensal': [],
                'recomendacoes': [],
            }

    def _classificar_saude(self, pr_media, num_alertas):
        """Classifica a saúde geral do sistema fotovoltaico."""
        if pr_media >= 0.90 and num_alertas == 0:
            return {'nivel': 'Excelente', 'cor': '#10B981', 'icone': '✅'}
        elif pr_media >= 0.80 and num_alertas <= 2:
            return {'nivel': 'Bom', 'cor': '#3B82F6', 'icone': '👍'}
        elif pr_media >= 0.70 and num_alertas <= 4:
            return {'nivel': 'Atenção', 'cor': '#F59E0B', 'icone': '⚠️'}
        elif pr_media >= 0.60:
            return {'nivel': 'Crítico', 'cor': '#EF4444', 'icone': '🔴'}
        else:
            return {'nivel': 'Urgente', 'cor': '#DC2626', 'icone': '🚨'}

    def _gerar_recomendacoes(self, alertas, pr_media, desvio_global):
        """Gera recomendações de manutenção baseadas na análise."""
        recomendacoes = []

        if any(a['prioridade'] == 'CRITICA' for a in alertas):
            recomendacoes.append({
                'prioridade': 'CRITICA',
                'titulo': 'Inspeção Técnica Urgente',
                'descricao': (
                    'Foram detectadas quedas críticas na geração. '
                    'Recomendamos uma inspeção técnica imediata no sistema, '
                    'verificando inversor, conexões e estado dos módulos.'
                ),
                'icone': '🔧',
            })

        if any(a['tipo'] == 'SUJEIRA' for a in alertas):
            recomendacoes.append({
                'prioridade': 'ALTA',
                'titulo': 'Limpeza dos Painéis Solares',
                'descricao': (
                    'Padrão de queda sugere acúmulo de sujeira nos módulos. '
                    'Realize a limpeza dos painéis com água e detergente neutro. '
                    'Frequência recomendada: a cada 6 meses.'
                ),
                'icone': '🧹',
            })

        if any(a['tipo'] == 'SOMBRA' for a in alertas):
            recomendacoes.append({
                'prioridade': 'MEDIA',
                'titulo': 'Verificar Sombreamento',
                'descricao': (
                    'Possível sombreamento sazonal detectado. '
                    'Verifique se há árvores, construções ou outros obstáculos '
                    'que possam estar causando sombra nos painéis em horários específicos.'
                ),
                'icone': '🌳',
            })

        if pr_media < 0.85 and desvio_global > 10:
            recomendacoes.append({
                'prioridade': 'MEDIA',
                'titulo': 'Monitoramento Contínuo',
                'descricao': (
                    f'Performance ratio média de {pr_media:.1%} está abaixo do ideal (>85%). '
                    'Recomendamos instalar um sistema de monitoramento em tempo real '
                    'para acompanhar a geração diária.'
                ),
                'icone': '📊',
            })

        if not recomendacoes:
            recomendacoes.append({
                'prioridade': 'BAIXA',
                'titulo': 'Sistema Operando Normalmente',
                'descricao': (
                    'Nenhuma anomalia significativa detectada. '
                    'Continue com a manutenção preventiva padrão: '
                    'limpeza semestral e inspeção visual trimestral.'
                ),
                'icone': '✅',
            })

        return recomendacoes
