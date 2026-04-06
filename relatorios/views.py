"""
Views do app de relatórios — Geração de PDF de propostas comerciais.
Usa WeasyPrint para converter templates HTML em documentos PDF profissionais.
"""

import io
import logging
from datetime import date
from django.http import FileResponse, Http404
from django.template.loader import render_to_string
from django.views import View
from weasyprint import HTML
from satelite.services import NASAPowerService
from dimensionamento.calculadora import CalculadoraSolar

logger = logging.getLogger(__name__)


def _parse_float(value, default=0):
    """Converte string para float, tratando vírgula como separador decimal."""
    if value is None:
        return default
    try:
        # Substituir vírgula por ponto (formato brasileiro)
        return float(str(value).replace(',', '.'))
    except (ValueError, TypeError):
        return default


class GerarPropostaPDFView(View):
    """
    Gera o PDF da proposta comercial completa.
    Recebe os dados via POST (do formulário de dimensionamento),
    calcula o dimensionamento e gera o documento PDF para download.
    """

    def post(self, request):
        """Processa os dados e gera o PDF."""
        try:
            # =================================================================
            # 1. EXTRAIR DADOS DO FORMULÁRIO (enviados via POST)
            # =================================================================
            nome_cliente = request.POST.get('nome_cliente', 'Cliente')
            email_cliente = request.POST.get('email_cliente', '')
            telefone_cliente = request.POST.get('telefone_cliente', '')
            endereco = request.POST.get('endereco', '')
            latitude = _parse_float(request.POST.get('latitude'), -23.55)
            longitude = _parse_float(request.POST.get('longitude'), -46.63)
            consumo_mensal = _parse_float(request.POST.get('consumo_mensal_kwh'), 350)
            tarifa = _parse_float(request.POST.get('tarifa_energia'), 0.85)
            tipo_telhado = request.POST.get('tipo_telhado', 'ceramica')
            inclinacao = _parse_float(request.POST.get('inclinacao_telhado'), 15)
            orientacao = request.POST.get('orientacao', 'norte')
            area_disponivel = request.POST.get('area_disponivel')
            nome_empresa = request.POST.get('nome_empresa', 'Solvian Energy')
            telefone_empresa = request.POST.get('telefone_empresa', '')
            email_empresa = request.POST.get('email_empresa', '')

            if area_disponivel:
                area_disponivel = _parse_float(area_disponivel)
            else:
                area_disponivel = None

            # =================================================================
            # 2. CONSULTAR SATÉLITE E CALCULAR
            # =================================================================
            dados_satelite = NASAPowerService.consultar_irradiacao(latitude, longitude)

            calculadora = CalculadoraSolar(
                consumo_mensal_kwh=consumo_mensal,
                irradiacao_media=dados_satelite['irradiacao_media_anual'],
                dados_mensais=dados_satelite.get('dados_mensais', {}),
                tarifa_energia=tarifa,
                inclinacao=inclinacao,
                orientacao=orientacao,
                tipo_telhado=tipo_telhado,
                area_disponivel=area_disponivel,
            )

            resultado = calculadora.calcular()

            # Mapear tipo de telhado para nome legível
            tipos_telhado = {
                'ceramica': 'Cerâmica / Barro',
                'metalica': 'Metálica / Zinco',
                'fibrocimento': 'Fibrocimento',
                'laje': 'Laje',
                'solo': 'Solo / Ground Mount',
            }

            orientacoes = {
                'norte': 'Norte',
                'nordeste': 'Nordeste',
                'noroeste': 'Noroeste',
                'leste': 'Leste',
                'oeste': 'Oeste',
                'sul': 'Sul',
            }

            # =================================================================
            # 3. RENDERIZAR TEMPLATE HTML
            # =================================================================
            contexto = {
                'data_proposta': date.today(),
                'cliente': {
                    'nome': nome_cliente,
                    'email': email_cliente,
                    'telefone': telefone_cliente,
                    'endereco': endereco,
                },
                'empresa': {
                    'nome': nome_empresa,
                    'telefone': telefone_empresa,
                    'email': email_empresa,
                },
                'localizacao': {
                    'latitude': latitude,
                    'longitude': longitude,
                },
                'telhado': {
                    'tipo': tipos_telhado.get(tipo_telhado, tipo_telhado),
                    'inclinacao': inclinacao,
                    'orientacao': orientacoes.get(orientacao, orientacao),
                    'area_disponivel': area_disponivel,
                },
                'satelite': dados_satelite,
                'resultado': resultado,
                'consumo_mensal': consumo_mensal,
            }

            html_string = render_to_string(
                'relatorios/proposta_pdf.html', contexto
            )

            # =================================================================
            # 4. GERAR PDF COM WEASYPRINT
            # =================================================================
            pdf_buffer = io.BytesIO()
            HTML(string=html_string).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)

            # Nome do arquivo
            nome_arquivo = f'Proposta_Solar_{nome_cliente.replace(" ", "_")}_{date.today().strftime("%Y%m%d")}.pdf'

            logger.info(f'PDF gerado para: {nome_cliente}')

            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=nome_arquivo,
                content_type='application/pdf',
            )

        except ValueError as e:
            logger.error(f'Erro de validação ao gerar PDF: {e}')
            raise Http404('Dados inválidos para geração do PDF.')

        except Exception as e:
            logger.error(f'Erro ao gerar PDF: {e}')
            raise Http404(f'Erro ao gerar o PDF: {str(e)}')

class GerarContratoPDFView(View):
    """
    Gera o Contrato de Prestacao de Servicos PDF.
    """
    def post(self, request):
        try:
            nome_cliente = request.POST.get('nome_cliente', 'Cliente')
            email_cliente = request.POST.get('email_cliente', '')
            telefone_cliente = request.POST.get('telefone_cliente', '')
            endereco = request.POST.get('endereco', '')
            latitude = _parse_float(request.POST.get('latitude'), -23.55)
            longitude = _parse_float(request.POST.get('longitude'), -46.63)
            consumo_mensal = _parse_float(request.POST.get('consumo_mensal_kwh'), 350)
            tarifa = _parse_float(request.POST.get('tarifa_energia'), 0.85)
            tipo_telhado = request.POST.get('tipo_telhado', 'ceramica')
            inclinacao = _parse_float(request.POST.get('inclinacao_telhado'), 15)
            orientacao = request.POST.get('orientacao', 'norte')
            area_disponivel = request.POST.get('area_disponivel')
            nome_empresa = request.POST.get('nome_empresa', 'Solvian Energy')
            telefone_empresa = request.POST.get('telefone_empresa', '')
            email_empresa = request.POST.get('email_empresa', '')

            if area_disponivel:
                area_disponivel = _parse_float(area_disponivel)
            else:
                area_disponivel = None

            dados_satelite = NASAPowerService.consultar_irradiacao(latitude, longitude)

            # Potencia do painel (Adicionado suporte novo)
            potencia_painel_wp = _parse_float(request.POST.get('potencia_painel_wp'), 550)

            calculadora = CalculadoraSolar(
                consumo_mensal_kwh=consumo_mensal,
                irradiacao_media=dados_satelite['irradiacao_media_anual'],
                dados_mensais=dados_satelite.get('dados_mensais', {}),
                tarifa_energia=tarifa,
                potencia_painel_wp=potencia_painel_wp,
                inclinacao=inclinacao,
                orientacao=orientacao,
                tipo_telhado=tipo_telhado,
                area_disponivel=area_disponivel,
            )

            resultado = calculadora.calcular()

            tipos_telhado = {
                'ceramica': 'Cerâmica / Barro',
                'metalica': 'Metálica / Zinco',
                'fibrocimento': 'Fibrocimento',
                'laje': 'Laje',
                'solo': 'Solo / Ground Mount',
            }
            orientacoes = {
                'norte': 'Norte',
                'nordeste': 'Nordeste',
                'noroeste': 'Noroeste',
                'leste': 'Leste',
                'oeste': 'Oeste',
                'sul': 'Sul',
            }

            contexto = {
                'data_proposta': date.today(),
                'cliente': {
                    'nome': nome_cliente,
                    'email': email_cliente,
                    'telefone': telefone_cliente,
                    'endereco': endereco,
                },
                'empresa': {
                    'nome': nome_empresa,
                    'telefone': telefone_empresa,
                    'email': email_empresa,
                },
                'telhado': {
                    'tipo': tipos_telhado.get(tipo_telhado, tipo_telhado),
                    'inclinacao': inclinacao,
                    'orientacao': orientacoes.get(orientacao, orientacao),
                    'area_disponivel': area_disponivel,
                },
                'resultado': resultado,
            }

            html_string = render_to_string('relatorios/contrato_pdf.html', contexto)

            pdf_buffer = io.BytesIO()
            HTML(string=html_string).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)

            nome_arquivo = f'Contrato_Solar_{nome_cliente.replace(" ", "_")}_{date.today().strftime("%Y%m%d")}.pdf'
            logger.info(f'Contrato PDF gerado para: {nome_cliente}')

            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=nome_arquivo,
                content_type='application/pdf',
            )

        except Exception as e:
            logger.error(f'Erro ao gerar Contrato PDF: {e}')
            raise Http404(f'Erro ao gerar o Contrato PDF: {str(e)}')
