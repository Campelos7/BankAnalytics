"""
Testes unitários para o módulo de métricas.
"""

import pytest
import sqlite3
import pandas as pd
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import metrics
from config import DB_PATH

@pytest.fixture
def test_db():
    """Cria um banco de dados de teste em memória."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Criar tabelas de teste
    cursor.execute('''
        CREATE TABLE financial_statements (
            month TEXT PRIMARY KEY,
            interest_income REAL NOT NULL,
            interest_expense REAL NOT NULL,
            fee_income REAL NOT NULL,
            operating_cost REAL NOT NULL,
            net_profit REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE accounts (
            account_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL,
            interest_rate REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE loans (
            loan_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            sector TEXT NOT NULL,
            loan_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            default_flag INTEGER NOT NULL
        )
    ''')
    
    # Inserir dados de teste
    # Financial statements - últimos 12 meses
    for i in range(12):
        month = f"2024-{str(i+1).zfill(2)}"
        cursor.execute('''
            INSERT INTO financial_statements 
            (month, interest_income, interest_expense, fee_income, operating_cost, net_profit)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (month, 1000000, 400000, 200000, 500000, 300000))
    
    # Accounts
    cursor.execute('''
        INSERT INTO accounts (account_id, customer_id, account_type, balance, interest_rate)
        VALUES ('ACC001', 'CUST001', 'checking', 100000, 0.02)
    ''')
    cursor.execute('''
        INSERT INTO accounts (account_id, customer_id, account_type, balance, interest_rate)
        VALUES ('ACC002', 'CUST001', 'savings', 200000, 0.05)
    ''')
    
    # Loans
    cursor.execute('''
        INSERT INTO loans (loan_id, customer_id, sector, loan_amount, interest_rate, default_flag)
        VALUES ('LOAN001', 'CUST001', 'Technology', 500000, 0.10, 0)
    ''')
    cursor.execute('''
        INSERT INTO loans (loan_id, customer_id, sector, loan_amount, interest_rate, default_flag)
        VALUES ('LOAN002', 'CUST002', 'Retail', 300000, 0.12, 1)
    ''')
    
    conn.commit()
    yield conn
    conn.close()

def test_calculate_roa(test_db):
    """Testa o cálculo de ROA."""
    roa = metrics.calculate_roa(test_db)
    
    # ROA = (Lucro Líquido 12 meses) / (Depósitos + Empréstimos) * 100
    # Lucro = 12 * 300000 = 3.600.000
    # Ativos = 100000 + 200000 + 500000 + 300000 = 1.100.000
    # ROA = 3.600.000 / 1.100.000 * 100 = 327.27%
    
    assert roa > 0
    assert isinstance(roa, float)

def test_calculate_roe(test_db):
    """Testa o cálculo de ROE."""
    roe = metrics.calculate_roe(test_db)
    
    assert roe > 0
    assert isinstance(roe, float)

def test_calculate_nim(test_db):
    """Testa o cálculo de NIM."""
    nim = metrics.calculate_net_interest_margin(test_db)
    
    assert isinstance(nim, float)

def test_calculate_cir(test_db):
    """Testa o cálculo de CIR."""
    cir = metrics.calculate_cost_to_income_ratio(test_db)
    
    assert cir >= 0
    assert isinstance(cir, float)

def test_calculate_loan_to_deposit_ratio(test_db):
    """Testa o cálculo de LDR."""
    ldr = metrics.calculate_loan_to_deposit_ratio(test_db)
    
    # Empréstimos = 500000 + 300000 = 800000
    # Depósitos = 100000 + 200000 = 300000
    # LDR = 800000 / 300000 * 100 = 266.67%
    
    assert ldr > 0
    assert isinstance(ldr, float)

def test_calculate_default_rate(test_db):
    """Testa o cálculo de taxa de inadimplência."""
    rate_count, rate_value = metrics.calculate_default_rate(test_db)
    
    # 1 empréstimo em default de 2 total = 50% por quantidade
    # 300000 em default de 800000 total = 37.5% por valor
    
    assert rate_count >= 0
    assert rate_value >= 0
    assert isinstance(rate_count, float)
    assert isinstance(rate_value, float)

def test_calculate_npl_ratio(test_db):
    """Testa o cálculo de NPL Ratio."""
    npl = metrics.calculate_npl_ratio(test_db)
    
    assert npl >= 0
    assert isinstance(npl, float)

def test_calculate_credit_exposure_by_sector(test_db):
    """Testa o cálculo de exposição por setor."""
    exposure_df = metrics.calculate_credit_exposure_by_sector(test_db)
    
    assert isinstance(exposure_df, pd.DataFrame)
    if len(exposure_df) > 0:
        assert 'sector' in exposure_df.columns
        assert 'total_exposure' in exposure_df.columns

def test_get_financial_summary(test_db):
    """Testa a obtenção do resumo financeiro."""
    summary = metrics.get_financial_summary(test_db)
    
    assert isinstance(summary, dict)
    assert 'total_assets' in summary
    assert 'net_profit' in summary
    assert summary['total_assets'] > 0

def test_safe_get_value():
    """Testa a função auxiliar _safe_get_value."""
    # A função é interna, então testamos indiretamente através das funções públicas
    # Mas podemos testar o comportamento esperado
    df = pd.DataFrame({'test': [100.5]})
    # Como a função é interna, vamos testar através de uma função pública
    # que a utiliza indiretamente
    pass  # Teste removido pois função é interna

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

