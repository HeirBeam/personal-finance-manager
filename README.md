
# Personal Finance Manager

This is a Python-based finance management app that allows users to track, analyze, and forecast their income and expenses. The app is built with Streamlit and provides a user-friendly interface for adding transactions, analyzing monthly expenses, and forecasting future expenses.

## Features

### 1. Personal Finance Manager
- **Visualize** monthly income and expenses with interactive bar charts.
- **Analyze** spending by category with pie charts.
- **Forecast** future expenses using the ARIMA model.
- **Set Thresholds** for expenses and receive alerts for predicted overages.

### 2. Transaction Data Entry UI
- **Enter transaction details** Date, type (income or expense), amount, and category.
- **Validation** ensures that a valid transaction amount greater than zero is entered.
- **Download Transactions** as a `.txt` file formatted to be easily uploaded into the app. 
- **Clear Transactions** allows for resetting transaction list in a single click.

## Setup Instructions

### Prerequisites
- Python 3.x
- Streamlit

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/personal-finance-manager.git
   cd personal-finance-manager
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Apps

#### 1. Personal Finance Manager App

This is the main finance management app where you can upload a `.txt` file with transaction data for analysis.

```bash
streamlit run app.py
```

- **Upload a `transactions.txt` file** (format shown below) to view your income and expenses analysis.

#### Example `transactions.txt` Format
```
Date, Type, Amount, Category
2022-01-01, Income, 3000, Salary
2022-01-05, Expense, 200, Groceries
...
```

#### 2. Transaction Data Entry UI

This UI lets you create transaction files if you don’t have one ready to upload.

```bash
streamlit run generate_transactions_ui.py
```

- **Enter transaction details** in the provided fields (date, type, amount, category).
- **Amount Validation**: The app ensures that only amounts greater than zero can be added.
- **Download the generated file** as `transactions.txt` and use it in the main app.

## Usage

### Using the Personal Finance Manager App

1. Run `app.py` and open the Streamlit app in your browser.
2. Upload a file named `transactions.txt` with the following structure:
   ```
   Date, Type, Amount, Category
   2022-01-01, Income, 3000, Salary
   2022-01-05, Expense, 200, Groceries
   ...
   ```
3. View the visualizations:
   - **Monthly Income and Expenses** bar chart.
   - **Spending by Category** pie chart.
   - **Forecasted Monthly Expenses** line chart with confidence intervals.

### Using the Transaction Data Entry UI

1. Run `generate_transactions_ui.py` and open the app in your browser.
2. Enter transaction details in the form and click **Add Transaction**.
   - Ensure that the amount is greater than zero for the transaction to be valid.
3. Once all entries are added, click **Download Transactions as .txt**.
4. Use the downloaded `transactions.txt` file in the main finance manager app.

## Future Improvements

- **Database Integration**: Store transactions in a database for persistent storage.
- **Update Transactions**: Allow the user to upload a transaction file that they can edit or add transactions to. 

