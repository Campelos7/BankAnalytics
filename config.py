"""
Arquivo de configuração centralizado para a aplicação Bank Analytics Platform.
"""

import os
from pathlib import Path
from typing import Optional

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Configurações do banco de dados
DB_PATH: str = os.getenv('DB_PATH', str(BASE_DIR / 'bank_data.db'))
DB_TIMEOUT: float = 20.0

# Configurações de logging
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE: Optional[str] = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))

# Configurações da aplicação
APP_TITLE: str = "Bank Analytics Platform"
APP_ICON: str = "🏦"

# Configurações de métricas
EQUITY_PERCENTAGE: float = 0.15  # 15% dos ativos como patrimônio líquido
MONTHS_FOR_ANALYSIS: int = 12  # Últimos 12 meses para análise

# Configurações de risco
RISK_THRESHOLDS = {
    'low': 30,
    'medium': 60,
    'high': 100
}

# Configurações de visualização
CHART_HEIGHT: int = 400
CHART_COLORS = {
    'primary': '#1f77b4',
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'danger': '#d62728',
    'secondary': '#9467bd'
}

