"""
Testes unitários para o módulo de banco de dados.
"""

import pytest
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import database

def test_create_database():
    """Testa a criação do banco de dados."""
    test_db = ':memory:'
    conn = database.create_database(test_db)
    
    cursor = conn.cursor()
    
    # Verificar se as tabelas foram criadas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['customers', 'accounts', 'loans', 'transactions', 'branches', 'financial_statements']
    for table in expected_tables:
        assert table in tables, f"Tabela {table} não foi criada"
    
    # Verificar se os índices foram criados
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    assert len(indexes) > 0, "Nenhum índice foi criado"
    
    conn.close()

def test_populate_customers():
    """Testa a população de clientes."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            country TEXT NOT NULL,
            segment TEXT NOT NULL,
            join_date DATE NOT NULL
        )
    ''')
    
    database.populate_customers(conn, n_customers=10)
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    count = cursor.fetchone()[0]
    
    assert count == 10, f"Esperado 10 clientes, obtido {count}"
    
    conn.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

