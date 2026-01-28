"""
Módulo de cálculo de métricas financeiras e de risco para análise bancária.
"""

import pandas as pd
import numpy as np
import sqlite3
from typing import Tuple, Dict, Optional, Union
from logger_config import logger
from config import EQUITY_PERCENTAGE, MONTHS_FOR_ANALYSIS

def get_db_connection(db_path: str = 'bank_data.db') -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco de dados.
    
    Args:
        db_path: Caminho para o arquivo do banco de dados
        
    Returns:
        Conexão SQLite
        
    Raises:
        sqlite3.Error: Se não conseguir conectar ao banco
    """
    try:
        return sqlite3.connect(db_path)
    except sqlite3.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados {db_path}: {str(e)}")
        raise

def _safe_query_execution(conn: sqlite3.Connection, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
    """
    Executa uma query SQL de forma segura com tratamento de erros.
    
    Args:
        conn: Conexão com o banco de dados
        query: Query SQL a ser executada
        params: Parâmetros opcionais para a query (tupla)
        
    Returns:
        DataFrame com os resultados
        
    Raises:
        sqlite3.Error: Se houver erro na execução da query
    """
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        
        if df.empty:
            logger.warning(f"Query retornou DataFrame vazio: {query[:50]}...")
        
        return df
    except sqlite3.Error as e:
        logger.error(f"Erro ao executar query: {str(e)}")
        logger.debug(f"Query: {query}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao executar query: {str(e)}")
        raise

def _safe_get_value(df: pd.DataFrame, column: str, default: float = 0.0) -> float:
    """
    Extrai um valor de forma segura de um DataFrame.
    
    Args:
        df: DataFrame
        column: Nome da coluna
        default: Valor padrão se não encontrar
        
    Returns:
        Valor extraído ou padrão
    """
    try:
        if df.empty or column not in df.columns:
            return default
        value = df[column].iloc[0]
        return float(value) if value is not None and not pd.isna(value) else default
    except (IndexError, KeyError, ValueError) as e:
        logger.warning(f"Erro ao extrair valor da coluna {column}: {str(e)}")
        return default

def calculate_net_interest_margin(conn: sqlite3.Connection) -> float:
    """
    Calcula o Net Interest Margin (NIM).
    NIM = (Receita de Juros - Despesa de Juros) / Ativos Médios
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        NIM em percentual (float)
    """
    try:
        logger.debug("Calculando Net Interest Margin")
        
        # Buscar receitas e despesas de juros dos últimos 12 meses
        query = f"""
            SELECT 
                month,
                interest_income,
                interest_expense
            FROM financial_statements
            ORDER BY month DESC
            LIMIT {MONTHS_FOR_ANALYSIS}
        """
        df = _safe_query_execution(conn, query)
        
        # Somar os últimos 12 meses
        total_interest_income = df['interest_income'].sum() if len(df) > 0 else 0.0
        total_interest_expense = df['interest_expense'].sum() if len(df) > 0 else 0.0
        
        # Calcular ativos médios
        deposits_query = """
            SELECT COALESCE(SUM(balance), 0) as deposits
            FROM accounts
            WHERE account_type IN ('checking', 'savings')
        """
        deposits_df = _safe_query_execution(conn, deposits_query)
        
        loans_query = """
            SELECT COALESCE(SUM(loan_amount), 0) as loans
            FROM loans
        """
        loans_df = _safe_query_execution(conn, loans_query)
        
        deposits = _safe_get_value(deposits_df, 'deposits')
        loans = _safe_get_value(loans_df, 'loans')
        avg_assets = deposits + loans
        
        if avg_assets == 0:
            logger.warning("Ativos médios são zero, retornando NIM = 0")
            return 0.0
        
        nim = ((total_interest_income - total_interest_expense) / avg_assets) * 100
        logger.info(f"NIM calculado: {nim:.2f}%")
        return round(nim, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular NIM: {str(e)}")
        return 0.0

def calculate_roa(conn: sqlite3.Connection) -> float:
    """
    Calcula o Return on Assets (ROA).
    ROA = Lucro Líquido / Ativos Totais
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        ROA em percentual (float)
    """
    try:
        logger.debug("Calculando ROA")
        
        # Lucro líquido dos últimos 12 meses
        profit_query = f"""
            SELECT net_profit
            FROM financial_statements
            ORDER BY month DESC
            LIMIT {MONTHS_FOR_ANALYSIS}
        """
        profit_df = _safe_query_execution(conn, profit_query)
        total_profit = profit_df['net_profit'].sum() if len(profit_df) > 0 else 0.0
        
        # Ativos totais
        deposits_query = """
            SELECT COALESCE(SUM(balance), 0) as deposits
            FROM accounts
            WHERE account_type IN ('checking', 'savings')
        """
        deposits_df = _safe_query_execution(conn, deposits_query)
        
        loans_query = """
            SELECT COALESCE(SUM(loan_amount), 0) as loans
            FROM loans
        """
        loans_df = _safe_query_execution(conn, loans_query)
        
        deposits = _safe_get_value(deposits_df, 'deposits')
        loans = _safe_get_value(loans_df, 'loans')
        total_assets = deposits + loans
        
        if total_assets == 0:
            logger.warning("Ativos totais são zero, retornando ROA = 0")
            return 0.0
        
        roa = (total_profit / total_assets) * 100
        logger.info(f"ROA calculado: {roa:.2f}%")
        return round(roa, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular ROA: {str(e)}")
        return 0.0

def calculate_roe(conn: sqlite3.Connection) -> float:
    """
    Calcula o Return on Equity (ROE).
    ROE = Lucro Líquido / Patrimônio Líquido
    Para simplificação, assumimos PL = 15% dos ativos totais
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        ROE em percentual (float)
    """
    try:
        logger.debug("Calculando ROE")
        
        # Lucro líquido dos últimos 12 meses
        profit_query = f"""
            SELECT net_profit
            FROM financial_statements
            ORDER BY month DESC
            LIMIT {MONTHS_FOR_ANALYSIS}
        """
        profit_df = _safe_query_execution(conn, profit_query)
        total_profit = profit_df['net_profit'].sum() if len(profit_df) > 0 else 0.0
        
        # Ativos totais
        deposits_query = """
            SELECT COALESCE(SUM(balance), 0) as deposits
            FROM accounts
            WHERE account_type IN ('checking', 'savings')
        """
        deposits_df = _safe_query_execution(conn, deposits_query)
        
        loans_query = """
            SELECT COALESCE(SUM(loan_amount), 0) as loans
            FROM loans
        """
        loans_df = _safe_query_execution(conn, loans_query)
        
        deposits = _safe_get_value(deposits_df, 'deposits')
        loans = _safe_get_value(loans_df, 'loans')
        total_assets = deposits + loans
        
        # Patrimônio líquido estimado
        equity = total_assets * EQUITY_PERCENTAGE
        
        if equity == 0:
            logger.warning("Patrimônio líquido é zero, retornando ROE = 0")
            return 0.0
        
        roe = (total_profit / equity) * 100
        logger.info(f"ROE calculado: {roe:.2f}%")
        return round(roe, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular ROE: {str(e)}")
        return 0.0

def calculate_cost_to_income_ratio(conn: sqlite3.Connection) -> float:
    """
    Calcula o Cost-to-Income Ratio.
    CIR = Custo Operacional / (Receita de Juros + Receita de Taxas)
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        CIR em percentual (float)
    """
    try:
        logger.debug("Calculando Cost-to-Income Ratio")
        
        query = f"""
            SELECT 
                operating_cost,
                interest_income,
                fee_income
            FROM financial_statements
            ORDER BY month DESC
            LIMIT {MONTHS_FOR_ANALYSIS}
        """
        df = _safe_query_execution(conn, query)
        
        total_costs = df['operating_cost'].sum() if len(df) > 0 else 0.0
        total_income = (df['interest_income'].sum() + df['fee_income'].sum()) if len(df) > 0 else 0.0
        
        if total_income == 0:
            logger.warning("Receita total é zero, retornando CIR = 0")
            return 0.0
        
        cir = (total_costs / total_income) * 100
        logger.info(f"CIR calculado: {cir:.2f}%")
        return round(cir, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular CIR: {str(e)}")
        return 0.0

def calculate_loan_to_deposit_ratio(conn: sqlite3.Connection) -> float:
    """
    Calcula o Loan-to-Deposit Ratio (LDR).
    LDR = Total de Empréstimos / Total de Depósitos
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        LDR em percentual (float)
    """
    try:
        logger.debug("Calculando Loan-to-Deposit Ratio")
        
        deposits_query = """
            SELECT SUM(balance) as total_deposits
            FROM accounts
            WHERE account_type IN ('checking', 'savings')
        """
        deposits_df = _safe_query_execution(conn, deposits_query)
        
        loans_query = """
            SELECT SUM(loan_amount) as total_loans
            FROM loans
        """
        loans_df = _safe_query_execution(conn, loans_query)
        
        total_deposits = _safe_get_value(deposits_df, 'total_deposits')
        total_loans = _safe_get_value(loans_df, 'total_loans')
        
        if total_deposits == 0:
            logger.warning("Depósitos totais são zero, retornando LDR = 0")
            return 0.0
        
        ldr = (total_loans / total_deposits) * 100
        logger.info(f"LDR calculado: {ldr:.2f}%")
        return round(ldr, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular LDR: {str(e)}")
        return 0.0

def calculate_default_rate(conn: sqlite3.Connection) -> Tuple[float, float]:
    """
    Calcula a taxa de inadimplência.
    Default Rate = Empréstimos em Inadimplência / Total de Empréstimos
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        Tupla com (taxa por quantidade, taxa por valor) em percentual
    """
    try:
        logger.debug("Calculando taxa de inadimplência")
        
        query = """
            SELECT 
                COUNT(CASE WHEN default_flag = 1 THEN 1 END) as defaulted_loans,
                COUNT(*) as total_loans,
                SUM(CASE WHEN default_flag = 1 THEN loan_amount ELSE 0 END) as defaulted_amount,
                SUM(loan_amount) as total_amount
            FROM loans
        """
        df = _safe_query_execution(conn, query)
        
        total_loans = _safe_get_value(df, 'total_loans')
        defaulted_loans = _safe_get_value(df, 'defaulted_loans')
        defaulted_amount = _safe_get_value(df, 'defaulted_amount')
        total_amount = _safe_get_value(df, 'total_amount')
        
        if total_loans == 0:
            logger.warning("Total de empréstimos é zero, retornando taxa = 0")
            return 0.0, 0.0
        
        # Taxa por quantidade e por valor
        rate_by_count = (defaulted_loans / total_loans) * 100
        rate_by_value = (defaulted_amount / total_amount) * 100 if total_amount > 0 else 0.0
        
        logger.info(f"Taxa de inadimplência calculada: {rate_by_count:.2f}% (quantidade), {rate_by_value:.2f}% (valor)")
        return round(rate_by_count, 2), round(rate_by_value, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular taxa de inadimplência: {str(e)}")
        return 0.0, 0.0

def calculate_npl_ratio(conn: sqlite3.Connection) -> float:
    """
    Calcula o Non-Performing Loan (NPL) Ratio.
    NPL = Empréstimos Não Performáticos / Total de Empréstimos
    (Assumindo que default_flag = 1 significa NPL)
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        NPL Ratio em percentual (float)
    """
    try:
        logger.debug("Calculando NPL Ratio")
        
        query = """
            SELECT 
                SUM(CASE WHEN default_flag = 1 THEN loan_amount ELSE 0 END) as npl_amount,
                SUM(loan_amount) as total_loans
            FROM loans
        """
        df = _safe_query_execution(conn, query)
        
        total_loans = _safe_get_value(df, 'total_loans')
        npl_amount = _safe_get_value(df, 'npl_amount')
        
        if total_loans == 0:
            logger.warning("Total de empréstimos é zero, retornando NPL = 0")
            return 0.0
        
        npl_ratio = (npl_amount / total_loans) * 100
        logger.info(f"NPL Ratio calculado: {npl_ratio:.2f}%")
        return round(npl_ratio, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular NPL Ratio: {str(e)}")
        return 0.0

def calculate_credit_exposure_by_sector(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Calcula a exposição de crédito por setor.
    Retorna um DataFrame com setor, total de empréstimos e taxa de inadimplência.
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        DataFrame com exposição por setor
    """
    try:
        logger.debug("Calculando exposição de crédito por setor")
        
        query = """
            SELECT 
                sector,
                COUNT(*) as loan_count,
                SUM(loan_amount) as total_exposure,
                SUM(CASE WHEN default_flag = 1 THEN loan_amount ELSE 0 END) as defaulted_exposure,
                COUNT(CASE WHEN default_flag = 1 THEN 1 END) as defaulted_count
            FROM loans
            GROUP BY sector
            ORDER BY total_exposure DESC
        """
        df = _safe_query_execution(conn, query)
        
        if len(df) == 0:
            logger.warning("Nenhum dado de exposição por setor encontrado")
            return df
        
        df['default_rate'] = (df['defaulted_count'] / df['loan_count']) * 100
        df['exposure_pct'] = (df['total_exposure'] / df['total_exposure'].sum()) * 100
        
        logger.info(f"Exposição calculada para {len(df)} setores")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao calcular exposição por setor: {str(e)}")
        return pd.DataFrame()

def calculate_bank_risk_index(conn: sqlite3.Connection) -> float:
    """
    Calcula um índice de risco bancário (0-100).
    Baseado em múltiplos fatores ponderados:
    - NPL Ratio (peso: 40%)
    - Loan-to-Deposit Ratio (peso: 20%)
    - Default Rate (peso: 30%)
    - Diversificação de setores (peso: 10%)
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        Índice de risco (0-100)
    """
    try:
        logger.debug("Calculando índice de risco bancário")
        
        # NPL Ratio
        npl_ratio = calculate_npl_ratio(conn)
        npl_score = min(npl_ratio * 10, 40)  # Máximo 40 pontos
        
        # Loan-to-Deposit Ratio (ideal: 80-90%)
        ldr = calculate_loan_to_deposit_ratio(conn)
        if ldr < 80:
            ldr_score = (80 - ldr) * 0.5  # Penaliza se muito baixo
        elif ldr > 100:
            ldr_score = (ldr - 100) * 0.5  # Penaliza se muito alto
        else:
            ldr_score = 0
        ldr_score = min(ldr_score, 20)  # Máximo 20 pontos
        
        # Default Rate
        _, default_rate_value = calculate_default_rate(conn)
        default_score = min(default_rate_value * 3, 30)  # Máximo 30 pontos
        
        # Diversificação (concentração de risco)
        exposure_df = calculate_credit_exposure_by_sector(conn)
        if len(exposure_df) > 0:
            # Calcula índice de Herfindahl (concentração)
            exposure_df['exposure_pct'] = (exposure_df['total_exposure'] / exposure_df['total_exposure'].sum()) * 100
            hhi = (exposure_df['exposure_pct'] ** 2).sum()  # HHI (0-10000)
            # Normaliza para 0-10 pontos (maior concentração = maior risco)
            concentration_score = (hhi / 10000) * 10
        else:
            concentration_score = 10  # Máximo risco se não houver dados
        
        # Soma total (quanto maior, maior o risco)
        total_risk_score = npl_score + ldr_score + default_score + concentration_score
        
        # Normaliza para 0-100
        risk_index = min(total_risk_score, 100)
        
        logger.info(f"Índice de risco bancário calculado: {risk_index:.2f}/100")
        return round(risk_index, 2)
        
    except Exception as e:
        logger.error(f"Erro ao calcular índice de risco: {str(e)}")
        return 0.0

def get_financial_summary(conn: sqlite3.Connection) -> Dict[str, float]:
    """
    Retorna um resumo financeiro consolidado.
    
    Args:
        conn: Conexão com o banco de dados
        
    Returns:
        Dicionário com resumo financeiro
    """
    try:
        logger.debug("Obtendo resumo financeiro")
        
        query = f"""
            SELECT 
                interest_income,
                interest_expense,
                fee_income,
                operating_cost,
                net_profit
            FROM financial_statements
            ORDER BY month DESC
            LIMIT {MONTHS_FOR_ANALYSIS}
        """
        df = _safe_query_execution(conn, query)
        
        # Somar os últimos 12 meses
        total_interest_income = df['interest_income'].sum() if len(df) > 0 else 0.0
        total_interest_expense = df['interest_expense'].sum() if len(df) > 0 else 0.0
        total_fee_income = df['fee_income'].sum() if len(df) > 0 else 0.0
        total_operating_cost = df['operating_cost'].sum() if len(df) > 0 else 0.0
        total_net_profit = df['net_profit'].sum() if len(df) > 0 else 0.0
        
        # Ativos e depósitos
        deposits_query = """
            SELECT SUM(balance) as total_deposits
            FROM accounts
            WHERE account_type IN ('checking', 'savings')
        """
        deposits_df = _safe_query_execution(conn, deposits_query)
        
        loans_query = """
            SELECT SUM(loan_amount) as total_loans
            FROM loans
        """
        loans_df = _safe_query_execution(conn, loans_query)
        
        total_deposits = _safe_get_value(deposits_df, 'total_deposits')
        total_loans = _safe_get_value(loans_df, 'total_loans')
        
        summary = {
            'total_assets': total_deposits + total_loans,
            'total_deposits': total_deposits,
            'total_loans': total_loans,
            'interest_income': total_interest_income,
            'interest_expense': total_interest_expense,
            'fee_income': total_fee_income,
            'operating_cost': total_operating_cost,
            'net_profit': total_net_profit
        }
        
        logger.info("Resumo financeiro obtido com sucesso")
        return summary
        
    except Exception as e:
        logger.error(f"Erro ao obter resumo financeiro: {str(e)}")
        return {
            'total_assets': 0.0,
            'total_deposits': 0.0,
            'total_loans': 0.0,
            'interest_income': 0.0,
            'interest_expense': 0.0,
            'fee_income': 0.0,
            'operating_cost': 0.0,
            'net_profit': 0.0
        }
