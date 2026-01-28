"""
Aplicação Streamlit para análise de desempenho bancário, contabilidade e risco.
Plataforma de Business Analytics para gestão estratégica bancária.
"""

"""
Aplicação Streamlit para análise de desempenho bancário, contabilidade e risco.
Plataforma de Business Analytics para gestão estratégica bancária.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime
from typing import Optional
import metrics
from config import DB_PATH, DB_TIMEOUT, APP_TITLE, APP_ICON, CHART_HEIGHT, CHART_COLORS
from logger_config import logger

# Configuração da página
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar a aparência
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-high {
        color: #d62728;
        font-weight: bold;
    }
    .risk-medium {
        color: #ff7f0e;
        font-weight: bold;
    }
    .risk-low {
        color: #2ca02c;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db_connection() -> sqlite3.Connection:
    """
    Retorna uma conexão com o banco de dados (cacheado).
    A conexão é compartilhada entre threads e não deve ser fechada manualmente.
    O Streamlit gerencia o ciclo de vida da conexão automaticamente.
    
    Returns:
        Conexão SQLite configurada
    """
    try:
        # check_same_thread=False permite usar a conexão em diferentes threads do Streamlit
        # timeout garante que a conexão aguarde se o banco estiver bloqueado
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=DB_TIMEOUT)
        logger.info(f"Conexão com banco de dados estabelecida: {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        st.error(f"⚠️ Erro ao conectar ao banco de dados: {str(e)}")
        raise

def format_currency(value: float) -> str:
    """
    Formata valores monetários.
    
    Args:
        value: Valor numérico a ser formatado
        
    Returns:
        String formatada com símbolo de moeda
    """
    try:
        if value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        elif value >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    except (TypeError, ValueError):
        return "$0.00"

def format_percentage(value: float) -> str:
    """
    Formata valores percentuais.
    
    Args:
        value: Valor numérico a ser formatado
        
    Returns:
        String formatada com símbolo de percentual
    """
    try:
        return f"{value:.2f}%"
    except (TypeError, ValueError):
        return "0.00%"

# ============================================================================
# PÁGINA 1: BANK OVERVIEW
# ============================================================================

def show_bank_overview() -> None:
    """Página de visão geral do banco com KPIs principais."""
    st.markdown('<h1 class="main-header">🏦 Visão Geral do Banco</h1>', unsafe_allow_html=True)
    
    try:
        conn = get_db_connection()
        
        # Calcular métricas
        logger.info("Calculando métricas para visão geral")
        summary = metrics.get_financial_summary(conn)
        roa = metrics.calculate_roa(conn)
        roe = metrics.calculate_roe(conn)
        nim = metrics.calculate_net_interest_margin(conn)
        cir = metrics.calculate_cost_to_income_ratio(conn)
        risk_index = metrics.calculate_bank_risk_index(conn)
    except Exception as e:
        logger.error(f"Erro ao carregar dados da visão geral: {str(e)}")
        st.error(f"⚠️ Erro ao carregar dados: {str(e)}")
        return
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Ativos Totais",
            value=format_currency(summary['total_assets']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="💵 Depósitos Totais",
            value=format_currency(summary['total_deposits']),
            delta=None
        )
    
    with col3:
        st.metric(
            label="📈 Lucro Líquido (12M)",
            value=format_currency(summary['net_profit']),
            delta=None
        )
    
    with col4:
        st.metric(
            label="📊 ROA",
            value=format_percentage(roa),
            delta=None
        )
    
    st.divider()
    
    # Segunda linha de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 ROE",
            value=format_percentage(roe),
            delta=None
        )
    
    with col2:
        st.metric(
            label="💹 Net Interest Margin",
            value=format_percentage(nim),
            delta=None
        )
    
    with col3:
        st.metric(
            label="⚖️ Cost-to-Income Ratio",
            value=format_percentage(cir),
            delta=None
        )
    
    with col4:
        # Determinar nível de risco
        if risk_index < 30:
            risk_level = "Baixo"
            risk_class = "risk-low"
        elif risk_index < 60:
            risk_level = "Médio"
            risk_class = "risk-medium"
        else:
            risk_level = "Alto"
            risk_class = "risk-high"
        
        st.metric(
            label="⚠️ Índice de Risco",
            value=f"{risk_index:.1f}",
            delta=risk_level
        )
    
    st.divider()
    
    # Resumo executivo
    st.subheader("📋 Resumo Executivo")
    
    # Análise de saúde financeira
    health_score = 100 - risk_index
    if health_score >= 70:
        health_status = "Excelente"
        health_color = "🟢"
    elif health_score >= 50:
        health_status = "Boa"
        health_color = "🟡"
    else:
        health_status = "Atenção Necessária"
        health_color = "🔴"
    
    st.markdown(f"""
    **{health_color} Saúde Financeira: {health_status}**
    
    O banco apresenta uma posição financeira sólida com ativos totais de {format_currency(summary['total_assets'])}. 
    O retorno sobre ativos (ROA) de {format_percentage(roa)} e o retorno sobre patrimônio (ROE) de {format_percentage(roe)} 
    indicam eficiência operacional adequada.
    
    **Principais Destaques:**
    - **Margem de Juros Líquida**: {format_percentage(nim)} - indica boa rentabilidade dos ativos
    - **Relação Custo-Receita**: {format_percentage(cir)} - eficiência operacional {'satisfatória' if cir < 60 else 'pode ser melhorada'}
    - **Índice de Risco**: {risk_index:.1f}/100 - nível de risco {risk_level.lower()}
    
    **Recomendações:**
    - Monitorar continuamente a qualidade da carteira de crédito
    - Manter diversificação adequada de ativos e passivos
    - Otimizar custos operacionais para melhorar a relação custo-receita
    """)
    
    # Não fechar a conexão - ela é gerenciada pelo cache do Streamlit

# ============================================================================
# PÁGINA 2: FINANCIAL PERFORMANCE
# ============================================================================

def show_financial_performance():
    """Página de análise de desempenho financeiro."""
    st.markdown('<h1 class="main-header">📊 Desempenho Financeiro</h1>', unsafe_allow_html=True)
    
    conn = get_db_connection()
    
    # Filtros na sidebar
    st.sidebar.header("🔍 Filtros")
    
    # Buscar dados financeiros mensais
    query = """
        SELECT 
            month,
            interest_income,
            interest_expense,
            fee_income,
            operating_cost,
            net_profit
        FROM financial_statements
        ORDER BY month
    """
    df = pd.read_sql_query(query, conn)
    df['month'] = pd.to_datetime(df['month'])
    
    # Filtro de período
    min_date = df['month'].min()
    max_date = df['month'].max()
    
    date_range = st.sidebar.date_input(
        "Período",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[(df['month'].dt.date >= start_date) & (df['month'].dt.date <= end_date)]
    else:
        df_filtered = df
    
    # Gráfico 1: Tendências de Receita e Despesa
    st.subheader("💰 Tendências de Receita e Despesa")
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=df_filtered['month'],
        y=df_filtered['interest_income'],
        mode='lines+markers',
        name='Receita de Juros',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig1.add_trace(go.Scatter(
        x=df_filtered['month'],
        y=df_filtered['fee_income'],
        mode='lines+markers',
        name='Receita de Taxas',
        line=dict(color='#2ca02c', width=3)
    ))
    
    fig1.add_trace(go.Scatter(
        x=df_filtered['month'],
        y=df_filtered['interest_expense'],
        mode='lines+markers',
        name='Despesa de Juros',
        line=dict(color='#d62728', width=3)
    ))
    
    fig1.add_trace(go.Scatter(
        x=df_filtered['month'],
        y=df_filtered['operating_cost'],
        mode='lines+markers',
        name='Custo Operacional',
        line=dict(color='#ff7f0e', width=3)
    ))
    
    fig1.update_layout(
        title="Evolução Mensal de Receitas e Despesas",
        xaxis_title="Mês",
        yaxis_title="Valor (USD)",
        hovermode='x unified',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico 2: Lucro Líquido
    st.subheader("📈 Lucro Líquido Mensal")
    
    fig2 = go.Figure()
    
    colors = ['#2ca02c' if x > 0 else '#d62728' for x in df_filtered['net_profit']]
    
    fig2.add_trace(go.Bar(
        x=df_filtered['month'],
        y=df_filtered['net_profit'],
        name='Lucro Líquido',
        marker_color=colors
    ))
    
    fig2.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break-even")
    
    fig2.update_layout(
        title="Lucro Líquido por Mês",
        xaxis_title="Mês",
        yaxis_title="Lucro Líquido (USD)",
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Gráfico 3: Cost-to-Income Ratio
    st.subheader("⚖️ Relação Custo-Receita (Cost-to-Income Ratio)")
    
    df_filtered['total_income'] = df_filtered['interest_income'] + df_filtered['fee_income']
    df_filtered['cir'] = (df_filtered['operating_cost'] / df_filtered['total_income']) * 100
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=df_filtered['month'],
        y=df_filtered['cir'],
        mode='lines+markers',
        name='CIR (%)',
        line=dict(color='#9467bd', width=3),
        fill='tozeroy'
    ))
    
    # Linha de referência (ideal: < 60%)
    fig3.add_hline(y=60, line_dash="dash", line_color="orange", 
                   annotation_text="Meta: < 60%", annotation_position="right")
    
    fig3.update_layout(
        title="Evolução do Cost-to-Income Ratio",
        xaxis_title="Mês",
        yaxis_title="CIR (%)",
        height=400
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Métricas resumidas do período
    st.subheader("📋 Resumo do Período Selecionado")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Receita Total",
            format_currency(df_filtered['total_income'].sum())
        )
    
    with col2:
        st.metric(
            "Custo Operacional Total",
            format_currency(df_filtered['operating_cost'].sum())
        )
    
    with col3:
        st.metric(
            "Lucro Líquido Total",
            format_currency(df_filtered['net_profit'].sum())
        )
    
    with col4:
        avg_cir = df_filtered['cir'].mean()
        st.metric(
            "CIR Médio",
            format_percentage(avg_cir)
        )
    
    # Não fechar a conexão - ela é gerenciada pelo cache do Streamlit

# ============================================================================
# PÁGINA 3: RISK OVERVIEW
# ============================================================================

def show_risk_overview():
    """Página de análise de risco."""
    st.markdown('<h1 class="main-header">⚠️ Análise de Risco</h1>', unsafe_allow_html=True)
    
    conn = get_db_connection()
    
    # Calcular métricas de risco
    default_rate_count, default_rate_value = metrics.calculate_default_rate(conn)
    npl_ratio = metrics.calculate_npl_ratio(conn)
    risk_index = metrics.calculate_bank_risk_index(conn)
    exposure_df = metrics.calculate_credit_exposure_by_sector(conn)
    
    # KPIs de Risco
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📉 Taxa de Inadimplência (por valor)",
            value=format_percentage(default_rate_value),
            delta=None
        )
    
    with col2:
        st.metric(
            label="📊 NPL Ratio",
            value=format_percentage(npl_ratio),
            delta=None
        )
    
    with col3:
        st.metric(
            label="⚠️ Índice de Risco Bancário",
            value=f"{risk_index:.1f}/100",
            delta=None
        )
    
    with col4:
        # Determinar nível de risco
        if risk_index < 30:
            risk_level = "Baixo"
            risk_color = "🟢"
        elif risk_index < 60:
            risk_level = "Médio"
            risk_color = "🟡"
        else:
            risk_level = "Alto"
            risk_color = "🔴"
        
        st.metric(
            label="🎯 Nível de Risco",
            value=risk_level,
            delta=None
        )
    
    st.divider()
    
    # Gráfico 1: Exposição de Crédito por Setor
    st.subheader("🏭 Exposição de Crédito por Setor")
    
    if len(exposure_df) > 0:
        fig1 = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Exposição Total por Setor', 'Taxa de Inadimplência por Setor'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Gráfico de exposição
        fig1.add_trace(
            go.Bar(
                x=exposure_df['sector'],
                y=exposure_df['total_exposure'],
                name='Exposição Total',
                marker_color='#1f77b4',
                text=[format_currency(x) for x in exposure_df['total_exposure']],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Gráfico de taxa de inadimplência
        colors = ['#d62728' if x > 5 else '#ff7f0e' if x > 2 else '#2ca02c' 
                 for x in exposure_df['default_rate']]
        
        fig1.add_trace(
            go.Bar(
                x=exposure_df['sector'],
                y=exposure_df['default_rate'],
                name='Taxa de Inadimplência (%)',
                marker_color=colors,
                text=[f"{x:.2f}%" for x in exposure_df['default_rate']],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig1.update_xaxes(title_text="Setor", row=1, col=1)
        fig1.update_xaxes(title_text="Setor", row=1, col=2)
        fig1.update_yaxes(title_text="Exposição (USD)", row=1, col=1)
        fig1.update_yaxes(title_text="Taxa (%)", row=1, col=2)
        fig1.update_layout(height=500, showlegend=False)
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Detalhamento por Setor")
        
        display_df = exposure_df[['sector', 'loan_count', 'total_exposure', 
                                  'defaulted_count', 'default_rate', 'exposure_pct']].copy()
        display_df.columns = ['Setor', 'Nº Empréstimos', 'Exposição Total', 
                             'Empréstimos Inadimplentes', 'Taxa Inadimplência (%)', 
                             'Participação (%)']
        display_df['Exposição Total'] = display_df['Exposição Total'].apply(format_currency)
        display_df['Participação (%)'] = display_df['Participação (%)'].apply(lambda x: f"{x:.2f}%")
        display_df['Taxa Inadimplência (%)'] = display_df['Taxa Inadimplência (%)'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Explicação do Índice de Risco
    st.subheader("📊 Explicação do Índice de Risco Bancário")
    
    st.markdown("""
    O **Índice de Risco Bancário** é uma métrica composta (0-100) que avalia a saúde geral do banco 
    considerando múltiplos fatores de risco:
    
    - **NPL Ratio (40%)**: Proporção de empréstimos não performáticos. Valores altos indicam maior risco de crédito.
    - **Loan-to-Deposit Ratio (20%)**: Relação entre empréstimos e depósitos. Valores muito altos ou muito baixos indicam risco de liquidez.
    - **Taxa de Inadimplência (30%)**: Percentual de empréstimos em default. Indica qualidade da carteira de crédito.
    - **Concentração de Setores (10%)**: Diversificação da carteira. Maior concentração = maior risco.
    
    **Interpretação:**
    - **0-30**: Risco Baixo 🟢 - Posição financeira sólida
    - **30-60**: Risco Médio 🟡 - Atenção necessária em algumas áreas
    - **60-100**: Risco Alto 🔴 - Ação corretiva recomendada
    """)
    
    # Gráfico de composição do risco
    risk_components = {
        'NPL Ratio': min(npl_ratio * 10, 40),
        'Loan-to-Deposit': min(abs(metrics.calculate_loan_to_deposit_ratio(conn) - 90) * 0.5, 20),
        'Default Rate': min(default_rate_value * 3, 30),
        'Concentração': 10  # Simplificado
    }
    
    fig2 = go.Figure(data=[
        go.Bar(
            x=list(risk_components.keys()),
            y=list(risk_components.values()),
            marker_color=['#d62728', '#ff7f0e', '#9467bd', '#8c564b']
        )
    ])
    
    fig2.update_layout(
        title="Componentes do Índice de Risco",
        xaxis_title="Fator de Risco",
        yaxis_title="Pontuação de Risco",
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Não fechar a conexão - ela é gerenciada pelo cache do Streamlit

# ============================================================================
# PÁGINA 4: BRANCH & SEGMENT ANALYSIS
# ============================================================================

def show_branch_segment_analysis():
    """Página de análise por filial e segmento."""
    st.markdown('<h1 class="main-header">🌍 Análise por Filial e Segmento</h1>', unsafe_allow_html=True)
    
    conn = get_db_connection()
    
    # Filtros na sidebar
    st.sidebar.header("🔍 Filtros")
    
    # Buscar países disponíveis
    countries_query = "SELECT DISTINCT country FROM customers ORDER BY country"
    countries_df = pd.read_sql_query(countries_query, conn)
    countries = ['Todos'] + countries_df['country'].tolist()
    
    selected_country = st.sidebar.selectbox("País", countries)
    
    # Buscar segmentos
    segments = ['Todos', 'retail', 'corporate']
    selected_segment = st.sidebar.selectbox("Segmento", segments)
    
    # Construir query com filtros (usando parâmetros para evitar SQL injection)
    where_clauses = []
    params = []
    
    if selected_country != 'Todos':
        where_clauses.append("c.country = ?")
        params.append(selected_country)
    if selected_segment != 'Todos':
        where_clauses.append("c.segment = ?")
        params.append(selected_segment)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Análise por país
    st.subheader("📊 Performance por País")
    
    # Query separada para custos operacionais por país
    branches_query = """
        SELECT country, SUM(operating_cost) as total_operating_cost
        FROM branches
        GROUP BY country
    """
    branches_df = pd.read_sql_query(branches_query, conn)
    
    country_query = """
        SELECT 
            c.country,
            COUNT(DISTINCT c.customer_id) as num_customers,
            COUNT(DISTINCT a.account_id) as num_accounts,
            SUM(CASE WHEN a.account_type IN ('checking', 'savings') THEN a.balance ELSE 0 END) as total_deposits,
            SUM(CASE WHEN l.loan_id IS NOT NULL THEN l.loan_amount ELSE 0 END) as total_loans,
            COUNT(CASE WHEN l.default_flag = 1 THEN 1 END) as defaulted_loans
        FROM customers c
        LEFT JOIN accounts a ON c.customer_id = a.customer_id
        LEFT JOIN loans l ON c.customer_id = l.customer_id
        WHERE """ + where_sql + """
        GROUP BY c.country
        ORDER BY total_deposits DESC
    """
    
    # Executar query com parâmetros seguros
    if params:
        country_df = pd.read_sql_query(country_query, conn, params=tuple(params))
    else:
        country_df = pd.read_sql_query(country_query, conn)
    
    # Adicionar custos operacionais
    if len(country_df) > 0 and len(branches_df) > 0:
        country_df = country_df.merge(branches_df, on='country', how='left')
        country_df['total_operating_cost'] = country_df['total_operating_cost'].fillna(0)
    else:
        country_df['total_operating_cost'] = 0
    
    if len(country_df) > 0:
        # Gráfico de depósitos por país
        fig1 = go.Figure(data=[
            go.Bar(
                x=country_df['country'],
                y=country_df['total_deposits'],
                name='Depósitos',
                marker_color='#1f77b4',
                text=[format_currency(x) for x in country_df['total_deposits']],
                textposition='auto'
            )
        ])
        
        fig1.update_layout(
            title="Depósitos Totais por País",
            xaxis_title="País",
            yaxis_title="Depósitos (USD)",
            height=400
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico de empréstimos por país
        fig2 = go.Figure(data=[
            go.Bar(
                x=country_df['country'],
                y=country_df['total_loans'],
                name='Empréstimos',
                marker_color='#2ca02c',
                text=[format_currency(x) for x in country_df['total_loans']],
                textposition='auto'
            )
        ])
        
        fig2.update_layout(
            title="Empréstimos Totais por País",
            xaxis_title="País",
            yaxis_title="Empréstimos (USD)",
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tabela resumo por país
        st.subheader("📋 Resumo por País")
        
        country_df['default_rate'] = (country_df['defaulted_loans'] / 
                                       country_df['total_loans'].replace(0, 1)) * 100
        country_df['default_rate'] = country_df['default_rate'].fillna(0)
        
        display_country_df = country_df[['country', 'num_customers', 'num_accounts', 
                                        'total_deposits', 'total_loans', 'default_rate',
                                        'total_operating_cost']].copy()
        display_country_df.columns = ['País', 'Clientes', 'Contas', 'Depósitos', 
                                      'Empréstimos', 'Taxa Inadimplência (%)', 'Custo Operacional']
        display_country_df['Depósitos'] = display_country_df['Depósitos'].apply(format_currency)
        display_country_df['Empréstimos'] = display_country_df['Empréstimos'].apply(format_currency)
        display_country_df['Custo Operacional'] = display_country_df['Custo Operacional'].apply(format_currency)
        display_country_df['Taxa Inadimplência (%)'] = display_country_df['Taxa Inadimplência (%)'].apply(
            lambda x: f"{x:.2f}%")
        
        st.dataframe(display_country_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Análise por segmento
    st.subheader("👥 Performance por Segmento de Cliente")
    
    segment_query = """
        SELECT 
            c.segment,
            COUNT(DISTINCT c.customer_id) as num_customers,
            COUNT(DISTINCT a.account_id) as num_accounts,
            SUM(CASE WHEN a.account_type IN ('checking', 'savings') THEN a.balance ELSE 0 END) as total_deposits,
            AVG(CASE WHEN a.account_type IN ('checking', 'savings') THEN a.balance ELSE NULL END) as avg_deposit,
            SUM(CASE WHEN l.loan_id IS NOT NULL THEN l.loan_amount ELSE 0 END) as total_loans,
            AVG(CASE WHEN l.loan_id IS NOT NULL THEN l.loan_amount ELSE NULL END) as avg_loan,
            COUNT(CASE WHEN l.default_flag = 1 THEN 1 END) as defaulted_loans
        FROM customers c
        LEFT JOIN accounts a ON c.customer_id = a.customer_id
        LEFT JOIN loans l ON c.customer_id = l.customer_id
        WHERE """ + where_sql + """
        GROUP BY c.segment
    """
    
    # Executar query com parâmetros seguros
    if params:
        segment_df = pd.read_sql_query(segment_query, conn, params=tuple(params))
    else:
        segment_df = pd.read_sql_query(segment_query, conn)
    
    if len(segment_df) > 0:
        # Gráfico comparativo
        fig3 = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Depósitos por Segmento', 'Empréstimos por Segmento'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        fig3.add_trace(
            go.Bar(
                x=segment_df['segment'],
                y=segment_df['total_deposits'],
                name='Depósitos',
                marker_color='#1f77b4',
                text=[format_currency(x) for x in segment_df['total_deposits']],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        fig3.add_trace(
            go.Bar(
                x=segment_df['segment'],
                y=segment_df['total_loans'],
                name='Empréstimos',
                marker_color='#2ca02c',
                text=[format_currency(x) for x in segment_df['total_loans']],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig3.update_xaxes(title_text="Segmento", row=1, col=1)
        fig3.update_xaxes(title_text="Segmento", row=1, col=2)
        fig3.update_yaxes(title_text="Valor (USD)", row=1, col=1)
        fig3.update_yaxes(title_text="Valor (USD)", row=1, col=2)
        fig3.update_layout(height=400, showlegend=False)
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Tabela resumo por segmento
        segment_df['default_rate'] = (segment_df['defaulted_loans'] / 
                                      segment_df['total_loans'].replace(0, 1)) * 100
        segment_df['default_rate'] = segment_df['default_rate'].fillna(0)
        
        display_segment_df = segment_df[['segment', 'num_customers', 'num_accounts',
                                         'total_deposits', 'avg_deposit', 'total_loans',
                                         'avg_loan', 'default_rate']].copy()
        display_segment_df.columns = ['Segmento', 'Clientes', 'Contas', 'Depósitos Totais',
                                      'Depósito Médio', 'Empréstimos Totais', 'Empréstimo Médio',
                                      'Taxa Inadimplência (%)']
        display_segment_df['Depósitos Totais'] = display_segment_df['Depósitos Totais'].apply(format_currency)
        display_segment_df['Depósito Médio'] = display_segment_df['Depósito Médio'].apply(format_currency)
        display_segment_df['Empréstimos Totais'] = display_segment_df['Empréstimos Totais'].apply(format_currency)
        display_segment_df['Empréstimo Médio'] = display_segment_df['Empréstimo Médio'].apply(format_currency)
        display_segment_df['Taxa Inadimplência (%)'] = display_segment_df['Taxa Inadimplência (%)'].apply(
            lambda x: f"{x:.2f}%")
        
        st.dataframe(display_segment_df, use_container_width=True, hide_index=True)
    
    # Não fechar a conexão - ela é gerenciada pelo cache do Streamlit

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

def main():
    """Função principal da aplicação."""
    
    # Sidebar com navegação
    st.sidebar.title("🏦 Bank Analytics")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navegação",
        ["Visão Geral", "Desempenho Financeiro", "Análise de Risco", "Análise por Filial/Segmento"]
    )
    
    # Verificar se o banco de dados existe
    import os
    if not os.path.exists(DB_PATH):
        st.error(f"⚠️ Banco de dados não encontrado! Execute 'python database.py' primeiro para criar o banco de dados.")
        st.stop()
    
    # Navegação entre páginas
    if page == "Visão Geral":
        show_bank_overview()
    elif page == "Desempenho Financeiro":
        show_financial_performance()
    elif page == "Análise de Risco":
        show_risk_overview()
    elif page == "Análise por Filial/Segmento":
        show_branch_segment_analysis()

if __name__ == "__main__":
    main()

