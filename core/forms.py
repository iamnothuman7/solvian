"""
Formulários do Solvian.
Formulário principal de dimensionamento solar que coleta todos os dados
necessários para calcular a proposta do sistema fotovoltaico.
"""

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator


class DimensionamentoForm(forms.Form):
    """
    Formulário completo de dimensionamento de sistema fotovoltaico.
    Coleta dados do cliente, localização e consumo para gerar a proposta.
    """

    # =========================================================================
    # DADOS DO CLIENTE
    # =========================================================================

    nome_cliente = forms.CharField(
        label='Nome do Cliente',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome completo ou razão social',
            'id': 'id_nome_cliente',
        })
    )

    email_cliente = forms.EmailField(
        label='E-mail',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'email@exemplo.com',
            'id': 'id_email_cliente',
        })
    )

    telefone_cliente = forms.CharField(
        label='Telefone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '(11) 99999-9999',
            'id': 'id_telefone_cliente',
        })
    )

    endereco = forms.CharField(
        label='Endereço da Instalação',
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Rua, número, bairro, cidade - UF',
            'id': 'id_endereco',
        })
    )

    # =========================================================================
    # LOCALIZAÇÃO (para consulta de satélite)
    # =========================================================================

    latitude = forms.FloatField(
        label='Latitude',
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: -23.5505',
            'step': '0.0001',
            'id': 'id_latitude',
        })
    )

    longitude = forms.FloatField(
        label='Longitude',
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: -46.6333',
            'step': '0.0001',
            'id': 'id_longitude',
        })
    )

    # =========================================================================
    # DADOS DO CONSUMO & CONCESSIONÁRIA
    # =========================================================================
    
    CONCESSIONARIA_CHOICES = [
        ('', '--- Selecione a Concessionária ---'),
        ('enel', 'Enel SP'),
        ('cemig', 'CEMIG'),
        ('cpfl', 'CPFL'),
        ('light', 'Light'),
        ('coelba', 'Coelba'),
        ('copel', 'COPEL'),
        ('neoenergia', 'Neoenergia'),
        ('equatorial', 'Equatorial'),
        ('outra', 'Outra / Manual'),
    ]

    concessionaria = forms.ChoiceField(
        label='Concessionária de Energia',
        choices=CONCESSIONARIA_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_concessionaria',
        }),
        help_text='A tarifa será preenchida automaticamente'
    )

    consumo_mensal_kwh = forms.FloatField(
        label='Consumo Médio Mensal (kWh)',
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: 350',
            'step': '1',
            'id': 'id_consumo_mensal',
        }),
        help_text='Valor médio da sua conta de luz em kWh'
    )

    tarifa_energia = forms.FloatField(
        label='Tarifa de Energia (R$/kWh)',
        validators=[MinValueValidator(0.01)],
        initial=0.85,
        widget=forms.NumberInput(attrs={
            'class': 'form-input bg-disabled',
            'placeholder': 'Ex: 0.85',
            'step': '0.01',
            'id': 'id_tarifa_energia',
            'readonly': 'readonly',
        }),
        help_text='Preenchido automaticamente. Selecione "Outra" para editar.'
    )

    # =========================================================================
    # DADOS TÉCNICOS DO TELHADO & PAINÉIS
    # =========================================================================

    POTENCIA_PAINEL_CHOICES = [
        (400, '400W'),
        (450, '450W'),
        (500, '500W'),
        (550, '550W (Padrão)'),
        (600, '600W'),
        (650, '650W'),
    ]

    potencia_painel_wp = forms.TypedChoiceField(
        label='Potência dos Painéis (Wp)',
        choices=POTENCIA_PAINEL_CHOICES,
        coerce=int,
        initial=550,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_potencia_painel',
        }),
        help_text='Capacidade individual de cada placa'
    )

    TIPO_TELHADO_CHOICES = [
        ('ceramica', 'Cerâmica / Barro'),
        ('metalica', 'Metálica / Zinco'),
        ('fibrocimento', 'Fibrocimento'),
        ('laje', 'Laje'),
        ('solo', 'Solo / Ground Mount'),
    ]

    tipo_telhado = forms.ChoiceField(
        label='Tipo de Telhado',
        choices=TIPO_TELHADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_tipo_telhado',
        })
    )

    inclinacao_telhado = forms.FloatField(
        label='Inclinação do Telhado (graus)',
        validators=[MinValueValidator(0), MaxValueValidator(90)],
        initial=15,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: 15',
            'step': '1',
            'id': 'id_inclinacao',
        }),
        help_text='Ângulo de inclinação do telhado (0° = plano, 90° = vertical)'
    )

    ORIENTACAO_CHOICES = [
        ('norte', 'Norte (ideal)'),
        ('nordeste', 'Nordeste'),
        ('noroeste', 'Noroeste'),
        ('leste', 'Leste'),
        ('oeste', 'Oeste'),
        ('sul', 'Sul'),
    ]

    orientacao = forms.ChoiceField(
        label='Orientação do Telhado',
        choices=ORIENTACAO_CHOICES,
        initial='norte',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_orientacao',
        }),
        help_text='Para qual direção o telhado está voltado'
    )

    area_disponivel = forms.FloatField(
        label='Área Disponível (m²)',
        validators=[MinValueValidator(1)],
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: 40 (opcional)',
            'step': '0.5',
            'id': 'id_area_disponivel',
        }),
        help_text='Área disponível para instalação dos painéis (opcional)'
    )

    # =========================================================================
    # DADOS DO INTEGRADOR (empresa que está gerando a proposta)
    # =========================================================================

    nome_empresa = forms.CharField(
        label='Nome da Empresa Integradora',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nome da sua empresa (aparece no PDF)',
            'id': 'id_nome_empresa',
        })
    )

    telefone_empresa = forms.CharField(
        label='Telefone da Empresa',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '(11) 3333-3333',
            'id': 'id_telefone_empresa',
        })
    )

    email_empresa = forms.EmailField(
        label='E-mail da Empresa',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'contato@empresa.com',
            'id': 'id_email_empresa',
        })
    )


class ManutencaoForm(forms.Form):
    """
    Formulário para análise de manutenção preditiva.
    O usuário informa dados de geração para o sistema detectar anomalias.
    """

    potencia_instalada_kwp = forms.FloatField(
        label='Potência Instalada (kWp)',
        validators=[MinValueValidator(0.1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: 5.5',
            'step': '0.1',
            'id': 'id_potencia_instalada',
        })
    )

    geracao_real_mensal = forms.CharField(
        label='Geração Real dos Últimos 12 Meses (kWh)',
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Informe 12 valores separados por vírgula.\nEx: 450, 480, 520, 510, 400, 380, 350, 390, 420, 460, 490, 470',
            'rows': 3,
            'id': 'id_geracao_real',
        }),
        help_text='12 valores de geração mensal separados por vírgula (Jan a Dez)'
    )

    latitude = forms.FloatField(
        label='Latitude',
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: -23.5505',
            'step': '0.0001',
            'id': 'id_manut_latitude',
        })
    )

    longitude = forms.FloatField(
        label='Longitude',
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: -46.6333',
            'step': '0.0001',
            'id': 'id_manut_longitude',
        })
    )

    def clean_geracao_real_mensal(self):
        """Valida e converte a string de valores em lista de floats."""
        dados = self.cleaned_data['geracao_real_mensal']
        try:
            valores = [float(v.strip()) for v in dados.split(',')]
            if len(valores) != 12:
                raise forms.ValidationError(
                    'Informe exatamente 12 valores (um para cada mês do ano).'
                )
            if any(v < 0 for v in valores):
                raise forms.ValidationError(
                    'Todos os valores de geração devem ser positivos.'
                )
            return valores
        except ValueError:
            raise forms.ValidationError(
                'Valores inválidos. Use números separados por vírgula.'
            )
