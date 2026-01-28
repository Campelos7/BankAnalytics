# 🏦 Bank Analytics Platform

A complete Streamlit application for analyzing banking performance, accounting, and risk management. This platform simulates a Business Analytics system to support strategic decision-making in financial institutions.

## 📋 Features

- **Executive Dashboard**: Key performance indicators (ROA, ROE, NIM, CIR)
- **Financial Analysis**: Monthly trends of revenues, expenses, and profit
- **Risk Management**: Non-performing loan metrics, NPL ratio, and banking risk index
- **Segmented Analysis**: Performance by country, branch, and customer segment
- **Interactive Visualizations**: Dynamic charts with Plotly
- **Realistic Synthetic Data**: SQLite database with simulated data

## 🛠️ Technologies Used

- **Python 3.10+**
- **Streamlit**: Interactive web interface
- **SQLite**: Relational database
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations

## 📊 Data Structure

The database contains the following tables:

1. **customers**: Customer information (country, segment, join date)
2. **accounts**: Bank accounts (type, balance, interest rate)
3. **loans**: Loans (sector, amount, rate, default status)
4. **transactions**: Financial transactions
5. **branches**: Branches and operational costs
6. **financial_statements**: Monthly financial statements

## 🚀 Installation and Setup

### 1. Prerequisites

Ensure you have Python 3.10 or higher installed:

```bash
python --version
```

### 2. Install Dependencies

Clone or download this repository and install the dependencies:

```bash
pip install -r requirements.txt
```

**Note**: The `sqlite3` module is already included in standard Python, but is listed in requirements.txt for reference.

### 3. Initialize the Database

Run the initialization script to create and populate the database with synthetic data:

```bash
python database.py
```

This script will:
- Create the `bank_data.db` file
- Populate all tables with realistic synthetic data
- Generate approximately 5,000 customers, accounts, loans, and transactions

### 4. Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

### 5. Run Tests (Optional)

To run the unit tests:

```bash
pytest tests/ -v
```

To run with code coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## 📱 Application Pages

### 1. Bank Overview
- Key performance indicators (Assets, Deposits, Profit, ROA, ROE)
- Net Interest Margin and Cost-to-Income Ratio
- Banking Risk Index
- Executive summary with financial health analysis

### 2. Financial Performance
- Monthly trends of revenues and expenses
- Net profit evolution
- Cost-to-Income Ratio analysis
- Period filters

### 3. Risk Analysis
- Default rate and NPL Ratio
- Credit exposure by sector
- Banking Risk Index with detailed explanation
- Risk components

### 4. Branch/Segment Analysis
- Performance by country
- Segment analysis (retail vs corporate)
- Interactive filters
- Comparative metrics

## 📈 Calculated Metrics

### Financial Metrics
- **Net Interest Margin (NIM)**: Net interest margin
- **ROA (Return on Assets)**: Return on assets
- **ROE (Return on Equity)**: Return on equity
- **Cost-to-Income Ratio (CIR)**: Cost-to-income ratio
- **Loan-to-Deposit Ratio (LDR)**: Loan-to-deposit ratio

### Risk Metrics
- **Default Rate**: Percentage of loans in default
- **NPL Ratio**: Proportion of non-performing loans
- **Sector Exposure**: Credit concentration
- **Banking Risk Index**: Composite score (0-100)

## 🎨 Design and Interface

- Clean and professional layout
- Interactive visualizations with Plotly
- Sidebar filters for segmented analysis
- Clear explanations for non-technical users
- Executive-style dashboard

## 📝 Project Structure

```
.
├── app.py                 # Main Streamlit application
├── database.py            # Database initialization script
├── metrics.py             # Metrics calculation module
├── config.py              # Centralized configuration
├── logger_config.py       # Logging configuration
├── requirements.txt       # Project dependencies
├── README.md             # This file
├── tests/                # Unit tests
│   ├── __init__.py
│   ├── test_metrics.py
│   └── test_database.py
└── bank_data.db          # SQLite database (generated after execution)
```

## 🔧 Customization

### Modify Synthetic Data

Edit the `database.py` file to adjust:
- Number of customers, accounts, and transactions
- Available countries and sectors
- Value and rate distributions
- Historical data periods

### Add New Metrics

1. Add the calculation function in `metrics.py`
2. Integrate the metric on the appropriate page in `app.py`
3. Add visualizations as needed

## 📚 Technical Notes

- **Synthetic Data**: Data is generated randomly but follows realistic distributions
- **Performance**: SQLite database is suitable for demonstration. For production, consider PostgreSQL or MySQL
- **Cache**: Streamlit uses cache to optimize database queries
- **Reproducibility**: Data is generated with a fixed seed (42) to ensure reproducibility
- **Indexes**: The database includes indexes on frequently queried columns for optimization
- **Logging**: Structured logging system for operation tracking
- **Error Handling**: All critical functions include robust error handling
- **Type Hints**: Code with type annotations for better maintainability
- **Tests**: Unit tests included for metrics validation

## 🎯 Use Cases

This application is ideal for:
- Business Analytics project portfolio
- Demonstration of financial analysis skills
- Learning Streamlit and data visualization
- Banking executive dashboard simulation

## 👤 TOMÁS CAMPELOS

Developed as a portfolio project to demonstrate skills in:
- Data Engineering
- Business Analytics
- Financial Analysis
- Python Development
- Streamlit Development

---


