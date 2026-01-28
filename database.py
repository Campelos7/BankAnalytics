"""
Script de inicialização do banco de dados SQLite.
Cria e popula as tabelas com dados sintéticos realistas para simulação bancária.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configuração de semente para reprodutibilidade
np.random.seed(42)
random.seed(42)

def create_database(db_path='bank_data.db'):
    """Cria o banco de dados e todas as tabelas."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabela de clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            country TEXT NOT NULL,
            segment TEXT NOT NULL,
            join_date DATE NOT NULL
        )
    ''')
    
    # Tabela de contas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL,
            interest_rate REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')
    
    # Tabela de empréstimos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            sector TEXT NOT NULL,
            loan_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            default_flag INTEGER NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')
    
    # Tabela de transações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            transaction_date DATE NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
    ''')
    
    # Tabela de filiais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            branch_id TEXT PRIMARY KEY,
            country TEXT NOT NULL,
            operating_cost REAL NOT NULL
        )
    ''')
    
    # Tabela de demonstrações financeiras mensais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_statements (
            month TEXT PRIMARY KEY,
            interest_income REAL NOT NULL,
            interest_expense REAL NOT NULL,
            fee_income REAL NOT NULL,
            operating_cost REAL NOT NULL,
            net_profit REAL NOT NULL
        )
    ''')
    
    # Criar índices para otimizar queries
    create_indexes(cursor)
    
    conn.commit()
    return conn

def create_indexes(cursor):
    """Cria índices nas colunas frequentemente consultadas."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country)",
        "CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(segment)",
        "CREATE INDEX IF NOT EXISTS idx_accounts_customer_id ON accounts(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type)",
        "CREATE INDEX IF NOT EXISTS idx_loans_customer_id ON loans(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_loans_sector ON loans(sector)",
        "CREATE INDEX IF NOT EXISTS idx_loans_default_flag ON loans(default_flag)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id)",
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)",
        "CREATE INDEX IF NOT EXISTS idx_branches_country ON branches(country)",
        "CREATE INDEX IF NOT EXISTS idx_financial_statements_month ON financial_statements(month)"
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except sqlite3.Error as e:
            print(f"⚠️ Aviso ao criar índice: {str(e)}")
    
    print("✓ Índices criados para otimização de queries")

def populate_customers(conn, n_customers=5000):
    """Popula a tabela de clientes com dados sintéticos."""
    countries = ['Brasil', 'Argentina', 'Chile', 'Colômbia', 'México', 'Peru']
    segments = ['retail', 'corporate']
    
    customers = []
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for i in range(n_customers):
        customer_id = f"CUST{str(i+1).zfill(6)}"
        country = np.random.choice(countries, p=[0.4, 0.15, 0.15, 0.1, 0.1, 0.1])
        segment = np.random.choice(segments, p=[0.7, 0.3])
        
        # Data de adesão aleatória
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        join_date = start_date + timedelta(days=random_days)
        
        customers.append({
            'customer_id': customer_id,
            'country': country,
            'segment': segment,
            'join_date': join_date.strftime('%Y-%m-%d')
        })
    
    df = pd.DataFrame(customers)
    df.to_sql('customers', conn, if_exists='replace', index=False)
    print(f"✓ {n_customers} clientes criados")

def populate_accounts(conn):
    """Popula a tabela de contas."""
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    account_types = ['checking', 'savings', 'loan']
    accounts = []
    account_counter = 1
    
    for customer_id in customer_ids:
        # Cada cliente tem pelo menos uma conta corrente
        account_id = f"ACC{str(account_counter).zfill(6)}"
        account_counter += 1
        
        # Conta corrente
        balance = np.random.lognormal(mean=8, sigma=1.5)
        accounts.append({
            'account_id': account_id,
            'customer_id': customer_id,
            'account_type': 'checking',
            'balance': round(balance, 2),
            'interest_rate': round(np.random.uniform(0.01, 0.05), 4)
        })
        
        # 60% dos clientes têm conta poupança
        if np.random.random() < 0.6:
            account_id = f"ACC{str(account_counter).zfill(6)}"
            account_counter += 1
            balance = np.random.lognormal(mean=9, sigma=1.8)
            accounts.append({
                'account_id': account_id,
                'customer_id': customer_id,
                'account_type': 'savings',
                'balance': round(balance, 2),
                'interest_rate': round(np.random.uniform(0.05, 0.12), 4)
            })
    
    df = pd.DataFrame(accounts)
    df.to_sql('accounts', conn, if_exists='replace', index=False)
    print(f"✓ {len(accounts)} contas criadas")
    return accounts

def populate_loans(conn):
    """Popula a tabela de empréstimos."""
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers WHERE segment = 'corporate'")
    corporate_customers = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT customer_id FROM customers WHERE segment = 'retail'")
    retail_customers = [row[0] for row in cursor.fetchall()]
    
    sectors = ['Technology', 'Manufacturing', 'Retail', 'Real Estate', 
               'Healthcare', 'Energy', 'Financial Services', 'Agriculture']
    
    loans = []
    loan_counter = 1
    
    # Empréstimos corporativos (maiores valores)
    n_corporate_loans = int(len(corporate_customers) * 0.8)
    for i in range(n_corporate_loans):
        customer_id = np.random.choice(corporate_customers)
        loan_id = f"LOAN{str(loan_counter).zfill(6)}"
        loan_counter += 1
        
        sector = np.random.choice(sectors)
        loan_amount = np.random.lognormal(mean=12, sigma=1.2)
        interest_rate = round(np.random.uniform(0.08, 0.15), 4)
        
        # Taxa de inadimplência por setor
        default_probs = {
            'Technology': 0.02,
            'Manufacturing': 0.04,
            'Retail': 0.05,
            'Real Estate': 0.06,
            'Healthcare': 0.02,
            'Energy': 0.03,
            'Financial Services': 0.02,
            'Agriculture': 0.07
        }
        default_flag = 1 if np.random.random() < default_probs.get(sector, 0.04) else 0
        
        loans.append({
            'loan_id': loan_id,
            'customer_id': customer_id,
            'sector': sector,
            'loan_amount': round(loan_amount, 2),
            'interest_rate': interest_rate,
            'default_flag': default_flag
        })
    
    # Empréstimos varejo (menores valores)
    n_retail_loans = int(len(retail_customers) * 0.3)
    for i in range(n_retail_loans):
        customer_id = np.random.choice(retail_customers)
        loan_id = f"LOAN{str(loan_counter).zfill(6)}"
        loan_counter += 1
        
        sector = 'Retail'
        loan_amount = np.random.lognormal(mean=9, sigma=1.0)
        interest_rate = round(np.random.uniform(0.12, 0.25), 4)
        default_flag = 1 if np.random.random() < 0.05 else 0
        
        loans.append({
            'loan_id': loan_id,
            'customer_id': customer_id,
            'sector': sector,
            'loan_amount': round(loan_amount, 2),
            'interest_rate': interest_rate,
            'default_flag': default_flag
        })
    
    df = pd.DataFrame(loans)
    df.to_sql('loans', conn, if_exists='replace', index=False)
    print(f"✓ {len(loans)} empréstimos criados")
    return loans

def populate_transactions(conn, accounts, n_transactions=50000):
    """Popula a tabela de transações."""
    transaction_types = ['deposit', 'withdrawal', 'transfer', 'fee', 'interest']
    
    transactions = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    account_ids = [acc['account_id'] for acc in accounts]
    
    for i in range(n_transactions):
        transaction_id = f"TXN{str(i+1).zfill(8)}"
        account_id = np.random.choice(account_ids)
        
        # Data aleatória
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        transaction_date = start_date + timedelta(days=random_days)
        
        transaction_type = np.random.choice(transaction_types, 
                                           p=[0.25, 0.25, 0.20, 0.15, 0.15])
        
        # Valores baseados no tipo de transação
        if transaction_type in ['deposit', 'transfer']:
            amount = abs(np.random.lognormal(mean=6, sigma=1.5))
        elif transaction_type == 'withdrawal':
            amount = -abs(np.random.lognormal(mean=6, sigma=1.5))
        elif transaction_type == 'fee':
            amount = -abs(np.random.uniform(5, 50))
        else:  # interest
            amount = abs(np.random.uniform(10, 500))
        
        transactions.append({
            'transaction_id': transaction_id,
            'account_id': account_id,
            'transaction_date': transaction_date.strftime('%Y-%m-%d'),
            'amount': round(amount, 2),
            'transaction_type': transaction_type
        })
    
    df = pd.DataFrame(transactions)
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    print(f"✓ {n_transactions} transações criadas")

def populate_branches(conn):
    """Popula a tabela de filiais."""
    countries = ['Brasil', 'Argentina', 'Chile', 'Colômbia', 'México', 'Peru']
    branches = []
    
    for i, country in enumerate(countries):
        n_branches = np.random.randint(5, 15)
        for j in range(n_branches):
            branch_id = f"BR{str(i+1).zfill(2)}{str(j+1).zfill(3)}"
            # Custo operacional baseado no país (Brasil mais caro)
            base_cost = 500000 if country == 'Brasil' else 300000
            operating_cost = base_cost * np.random.uniform(0.8, 1.2)
            
            branches.append({
                'branch_id': branch_id,
                'country': country,
                'operating_cost': round(operating_cost, 2)
            })
    
    df = pd.DataFrame(branches)
    df.to_sql('branches', conn, if_exists='replace', index=False)
    print(f"✓ {len(branches)} filiais criadas")

def populate_financial_statements(conn):
    """Popula a tabela de demonstrações financeiras mensais."""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    statements = []
    current_date = start_date
    
    # Tendência de crescimento ao longo do tempo
    month_counter = 0
    
    while current_date <= end_date:
        month_str = current_date.strftime('%Y-%m')
        
        # Base crescente ao longo do tempo
        growth_factor = 1 + (month_counter * 0.01)
        
        # Receita de juros (cresce com o tempo)
        interest_income = np.random.uniform(8000000, 12000000) * growth_factor
        
        # Despesa de juros (proporcional à receita)
        interest_expense = interest_income * np.random.uniform(0.3, 0.5)
        
        # Receita de taxas
        fee_income = np.random.uniform(2000000, 4000000) * growth_factor
        
        # Custo operacional (mais estável)
        operating_cost = np.random.uniform(5000000, 7000000) * (1 + month_counter * 0.005)
        
        # Lucro líquido
        net_profit = interest_income - interest_expense + fee_income - operating_cost
        
        statements.append({
            'month': month_str,
            'interest_income': round(interest_income, 2),
            'interest_expense': round(interest_expense, 2),
            'fee_income': round(fee_income, 2),
            'operating_cost': round(operating_cost, 2),
            'net_profit': round(net_profit, 2)
        })
        
        # Próximo mês
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
        
        month_counter += 1
    
    df = pd.DataFrame(statements)
    df.to_sql('financial_statements', conn, if_exists='replace', index=False)
    print(f"✓ {len(statements)} meses de demonstrações financeiras criados")

def initialize_database(db_path='bank_data.db'):
    """Função principal para inicializar todo o banco de dados."""
    print("Inicializando banco de dados...")
    print("=" * 50)
    
    conn = create_database(db_path)
    
    populate_customers(conn)
    accounts = populate_accounts(conn)
    populate_loans(conn)
    populate_transactions(conn, accounts)
    populate_branches(conn)
    populate_financial_statements(conn)
    
    # Os índices já foram criados em create_database
    conn.commit()
    conn.close()
    print("=" * 50)
    print("✓ Banco de dados inicializado com sucesso!")
    print(f"✓ Arquivo criado: {db_path}")

if __name__ == "__main__":
    initialize_database()

