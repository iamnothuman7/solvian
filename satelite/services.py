"""
Serviço de integração com a API NASA POWER.
Consulta dados de irradiação solar via satélite para qualquer
localização geográfica (latitude/longitude).
"""

import requests
import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from core.models import DadosSatelite

logger = logging.getLogger(__name__)

# Mapeamento dos meses para nomes em português
MESES_PT = {
    '1': 'Janeiro', '2': 'Fevereiro', '3': 'Março',
    '4': 'Abril', '5': 'Maio', '6': 'Junho',
    '7': 'Julho', '8': 'Agosto', '9': 'Setembro',
    '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro',
}


class NASAPowerService:
    """
    Classe responsável por consultar a API NASA POWER e retornar
    dados de irradiação solar e temperatura para uma localização.

    A API NASA POWER fornece dados climáticos gratuitos baseados em satélite,
    incluindo irradiação solar (GHI - Global Horizontal Irradiance).

    Documentação: https://power.larc.nasa.gov/docs/services/api/
    """

    # Endpoint da API para dados climatológicos (médias de 30 anos)
    API_URL = getattr(
        settings, 'NASA_POWER_API_URL',
        'https://power.larc.nasa.gov/api/temporal/climatology/point'
    )

    # Timeout padrão para a requisição HTTP
    TIMEOUT = getattr(settings, 'NASA_POWER_TIMEOUT', 30)

    # Parâmetros de interesse:
    # ALLSKY_SFC_SW_DWN = Irradiação solar total na superfície (kWh/m²/dia)
    # CLRSKY_SFC_SW_DWN = Irradiação em céu limpo
    # T2M = Temperatura a 2 metros (°C)
    PARAMETROS = 'ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN,T2M'

    @classmethod
    def consultar_irradiacao(cls, latitude, longitude, usar_cache=True):
        """
        Consulta a irradiação solar para uma determinada localização.

        Args:
            latitude (float): Latitude do local (-90 a 90)
            longitude (float): Longitude do local (-180 a 180)
            usar_cache (bool): Se True, verifica o cache antes de consultar

        Returns:
            dict: Dicionário com os dados de irradiação, temperatura e metadados
                {
                    'sucesso': bool,
                    'latitude': float,
                    'longitude': float,
                    'irradiacao_media_anual': float,  # kWh/m²/dia
                    'temperatura_media': float,  # °C
                    'dados_mensais': {
                        '1': {'irradiacao': float, 'temperatura': float, 'nome_mes': str},
                        ...
                    },
                    'fonte': str,
                    'erro': str (apenas se sucesso=False)
                }

        Raises:
            Não levanta exceções - retorna dict com 'sucesso': False em caso de erro.
        """

        # Arredondar coordenadas para 2 casas (precisão de ~1km, suficiente para solar)
        lat = round(float(latitude), 2)
        lon = round(float(longitude), 2)

        # =====================================================================
        # VERIFICAR CACHE (consultas recentes para mesma localização)
        # =====================================================================
        if usar_cache:
            cache = cls._buscar_cache(lat, lon)
            if cache:
                logger.info(f'Cache encontrado para ({lat}, {lon})')
                return cache

        # =====================================================================
        # CONSULTAR API NASA POWER
        # =====================================================================
        try:
            logger.info(f'Consultando NASA POWER para ({lat}, {lon})...')

            params = {
                'parameters': cls.PARAMETROS,
                'community': 'RE',  # Renewable Energy
                'longitude': lon,
                'latitude': lat,
                'format': 'JSON',
            }

            response = requests.get(
                cls.API_URL,
                params=params,
                timeout=cls.TIMEOUT,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()

            dados_api = response.json()
            resultado = cls._processar_resposta(dados_api, lat, lon)

            # Salvar no cache
            if resultado['sucesso']:
                cls._salvar_cache(resultado)

            return resultado

        except requests.exceptions.Timeout:
            logger.error(f'Timeout ao consultar NASA POWER para ({lat}, {lon})')
            return cls._resposta_fallback(lat, lon, 'Timeout na conexão com a API NASA POWER')

        except requests.exceptions.ConnectionError:
            logger.error(f'Erro de conexão com NASA POWER para ({lat}, {lon})')
            return cls._resposta_fallback(lat, lon, 'Sem conexão com a API NASA POWER')

        except requests.exceptions.HTTPError as e:
            logger.error(f'Erro HTTP da NASA POWER: {e}')
            return cls._resposta_fallback(lat, lon, f'Erro na API: {e.response.status_code}')

        except Exception as e:
            logger.error(f'Erro inesperado ao consultar NASA POWER: {e}')
            return cls._resposta_fallback(lat, lon, str(e))

    # Mapeamento das chaves de mês da API NASA POWER para número do mês
    # A API retorna JAN, FEB, MAR... em vez de 1, 2, 3...
    MESES_API = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
        'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
        'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12,
    }

    @classmethod
    def _processar_resposta(cls, dados_api, lat, lon):
        """
        Processa a resposta JSON da API NASA POWER e extrai os dados relevantes.
        A API retorna chaves de mês como JAN, FEB, MAR...
        """
        try:
            properties = dados_api.get('properties', {})
            parametros = properties.get('parameter', {})

            # Dados de irradiação solar (kWh/m²/dia)
            irradiacao = parametros.get('ALLSKY_SFC_SW_DWN', {})
            # Dados de temperatura (°C)
            temperatura = parametros.get('T2M', {})

            # Processar dados mensais usando as chaves corretas da API
            dados_mensais = {}
            irradiacao_valores = []

            for mes_abrev, mes_num in cls.MESES_API.items():
                mes_key = str(mes_num)
                irrad = irradiacao.get(mes_abrev, 0)
                temp = temperatura.get(mes_abrev, 0)

                # A API retorna -999 para dados não disponíveis
                if irrad == -999:
                    irrad = 0
                if temp == -999:
                    temp = 0

                dados_mensais[mes_key] = {
                    'irradiacao': round(irrad, 2),
                    'temperatura': round(temp, 1),
                    'nome_mes': MESES_PT.get(mes_key, mes_key),
                }
                if irrad > 0:
                    irradiacao_valores.append(irrad)

            # Calcular médias anuais
            media_irrad = (
                round(sum(irradiacao_valores) / len(irradiacao_valores), 2)
                if irradiacao_valores else 0
            )

            # Média anual da API (campo 'ANN')
            media_anual_api = irradiacao.get('ANN', media_irrad)
            if media_anual_api == -999:
                media_anual_api = media_irrad

            temp_valores = [d['temperatura'] for d in dados_mensais.values() if d['temperatura'] > 0]
            media_temp = (
                round(sum(temp_valores) / len(temp_valores), 1)
                if temp_valores else 25.0
            )

            return {
                'sucesso': True,
                'latitude': lat,
                'longitude': lon,
                'irradiacao_media_anual': round(media_anual_api, 2),
                'temperatura_media': media_temp,
                'dados_mensais': dados_mensais,
                'fonte': 'NASA POWER (Climatologia 30 anos)',
                'erro': None,
            }

        except (KeyError, TypeError) as e:
            logger.error(f'Erro ao processar resposta da NASA POWER: {e}')
            return cls._resposta_fallback(lat, lon, 'Erro ao processar dados da API')

    @classmethod
    def _buscar_cache(cls, lat, lon):
        """
        Busca dados em cache para a mesma localização (tolerância de 0.01°).
        Cache válido por 30 dias.
        """
        try:
            limite_cache = timezone.now() - timedelta(days=30)
            cache = DadosSatelite.objects.filter(
                latitude__range=(lat - 0.01, lat + 0.01),
                longitude__range=(lon - 0.01, lon + 0.01),
                data_consulta__gte=limite_cache,
            ).first()

            if cache:
                dados_mensais = cache.dados_mensais
                return {
                    'sucesso': True,
                    'latitude': cache.latitude,
                    'longitude': cache.longitude,
                    'irradiacao_media_anual': cache.irradiacao_media_anual,
                    'temperatura_media': cache.temperatura_media,
                    'dados_mensais': dados_mensais,
                    'fonte': f'{cache.fonte_api} (cache)',
                    'erro': None,
                }
        except Exception as e:
            logger.warning(f'Erro ao buscar cache: {e}')

        return None

    @classmethod
    def _salvar_cache(cls, resultado):
        """Salva o resultado da consulta no banco como cache."""
        try:
            # Preparar dados mensais para serialização
            dados_para_json = {}
            for mes, dados in resultado['dados_mensais'].items():
                dados_para_json[mes] = {
                    'irradiacao': dados['irradiacao'],
                    'temperatura': dados['temperatura'],
                    'nome_mes': dados['nome_mes'],
                }

            cache = DadosSatelite(
                latitude=resultado['latitude'],
                longitude=resultado['longitude'],
                irradiacao_media_anual=resultado['irradiacao_media_anual'],
                temperatura_media=resultado['temperatura_media'],
                fonte_api='NASA POWER',
            )
            cache.dados_mensais = dados_para_json
            cache.save()
            logger.info(f'Cache salvo para ({resultado["latitude"]}, {resultado["longitude"]})')

        except Exception as e:
            logger.warning(f'Erro ao salvar cache: {e}')

    @classmethod
    def _resposta_fallback(cls, lat, lon, mensagem_erro):
        """
        Retorna dados estimados quando a API não está disponível.
        Usa valores médios para o Brasil como fallback.
        """
        logger.warning(f'Usando fallback para ({lat}, {lon}): {mensagem_erro}')

        # Estimativa baseada na latitude para o Brasil
        # Regiões mais próximas do equador têm maior irradiação
        lat_abs = abs(lat)
        if lat_abs < 10:
            irrad_estimada = 5.5  # Norte/Nordeste
        elif lat_abs < 20:
            irrad_estimada = 5.2  # Centro-Oeste/Sudeste
        elif lat_abs < 30:
            irrad_estimada = 4.8  # Sul
        else:
            irrad_estimada = 4.5  # Extremo Sul

        dados_mensais = {}
        for mes_num in range(1, 13):
            # Variação sazonal simplificada
            fator_sazonal = 1.0
            if lat < 0:  # Hemisfério Sul
                if mes_num in [12, 1, 2]:
                    fator_sazonal = 1.15  # Verão
                elif mes_num in [6, 7, 8]:
                    fator_sazonal = 0.85  # Inverno
            else:
                if mes_num in [6, 7, 8]:
                    fator_sazonal = 1.15
                elif mes_num in [12, 1, 2]:
                    fator_sazonal = 0.85

            dados_mensais[str(mes_num)] = {
                'irradiacao': round(irrad_estimada * fator_sazonal, 2),
                'temperatura': round(25 + (10 - lat_abs) * 0.3, 1),
                'nome_mes': MESES_PT.get(str(mes_num), str(mes_num)),
            }

        return {
            'sucesso': False,
            'latitude': lat,
            'longitude': lon,
            'irradiacao_media_anual': irrad_estimada,
            'temperatura_media': 25.0,
            'dados_mensais': dados_mensais,
            'fonte': 'Estimativa (API indisponível)',
            'erro': mensagem_erro,
        }
