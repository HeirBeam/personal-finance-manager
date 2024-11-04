import streamlit as st
import pandas as pd
from io import StringIO
from datetime import date
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Function to load and format transactions
def load_transactions_from_text(file_lines):
    transactions = []
    header = True  # Flag to skip the first line if it's a header

    for line in file_lines:
        # Skip the header row
        if header:  
            header = False
            continue

        # Remove trailing commas and spaces, then split by ", "
        line = line.strip().rstrip(",")  # Strip extra spaces and trailing commas
        parts = line.split(", ")

        # Ensure the line has at least 3 parts (Date, Type, Amount) for a valid transaction
        if len(parts) < 3:
            st.error(f"Skipping line due to format error: {line}")
            continue

        # Extract and clean data, using defaults where necessary
        date = parts[0].strip()
        transaction_type = parts[1].strip()
        amount = parts[2].strip() if parts[2] else None
        category = parts[3].strip() if len(parts) > 3 and parts[3].strip() != "" else "Uncategorized"

        # Try converting date and amount, handle errors gracefully
        try:
            transaction = {
                "Date": pd.to_datetime(date, errors="coerce"),  # Coerce invalid dates to NaT
                "Type": transaction_type,
                "Amount": float(amount) if amount else None,  # Convert amount to float or set to None
                "Category": category
            }
            # Validate date and amount
            if transaction["Date"] is pd.NaT or transaction["Amount"] is None:
                st.error(f"Skipping line due to invalid date or amount: {line}")
                continue  # Skip invalid entry
            transactions.append(transaction)  # Append only valid entries

        except ValueError:
            st.error(f"Skipping line due to invalid data format: {line}")
            continue

    # Convert transactions to DataFrame and process if not empty
    if transactions:
        df = pd.DataFrame(transactions)
        df['Amount'] = df.apply(lambda x: x['Amount'] if x['Type'] == 'Income' else -x['Amount'], axis=1)
        df['Month'] = df['Date'].dt.to_period('M')
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no valid data


# Initialize Streamlit layout
st.set_page_config(page_title="Personal Finance Manager", layout="wide")

st.title("📊 Personal Finance Manager")

# Sidebar for thresholds and transaction entry
st.sidebar.header("Settings")
st.sidebar.markdown("Set your expense threshold and add new transactions.")

# Sidebar for thresholds and transaction entry
st.sidebar.header("Settings")
st.sidebar.markdown("Set your expense threshold and add new transactions.")

# Threshold setting
threshold = st.sidebar.number_input("Set Expense Threshold", value=3000, help="Set a threshold for monthly expenses")

# Transaction entry form in sidebar
st.sidebar.subheader("Enter Transaction Details")
with st.sidebar.form("transaction_form"):
    entry_date = st.date_input("Date", value=date.today())
    transaction_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f", help="Enter the transaction amount")
    category = st.text_input("Category", placeholder="e.g., Salary, Groceries, Utilities")
    
    # Add transaction button with validation
    if st.form_submit_button("Add Transaction"):
        if amount <= 0:
            st.sidebar.error("Please enter a valid amount greater than zero.")
        else:
            # Add the transaction only if the amount is valid
            st.session_state.transactions.append({
                "Date": entry_date.strftime("%Y-%m-%d"),
                "Type": transaction_type,
                "Amount": f"{amount:.2f}",
                "Category": category
            })
            st.sidebar.success("Transaction added! 🎉")


# Initialize session state for transactions
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Empty container for displaying transaction list
transaction_container = st.empty()

# Function to display the transaction list
def display_transaction_list():
    with transaction_container:
        st.subheader("Transaction List")
        if st.session_state.transactions:
            df_transactions = pd.DataFrame(st.session_state.transactions)
            st.dataframe(df_transactions, height=200)
        else:
            st.info("No transactions added yet. Enter details in the sidebar.")

# Call the function to display the transaction list initially
display_transaction_list()

# Clear transactions button to reset the transaction list
if st.button("Clear Transactions"):
    st.session_state.transactions = []  # Clear the transactions in session state
    st.success("Transaction list cleared.")
    display_transaction_list()  # Refresh the container to show the cleared list

# Display the download button outside of transaction_container to keep it persistent
if st.session_state.transactions:
    # Function to convert the transactions DataFrame to a downloadable .txt format
    def convert_to_txt(df):
        output = StringIO()
        output.write("Date, Type, Amount, Category\n")
        for index, row in df.iterrows():
            output.write(f"{row['Date']}, {row['Type']}, {row['Amount']}, {row['Category']}\n")
        return output.getvalue().encode('utf-8')
    
    # Generate .txt data for download
    df_transactions = pd.DataFrame(st.session_state.transactions)
    txt_data = convert_to_txt(df_transactions)
    
    st.download_button(
        label="Download Transactions as .txt",
        data=txt_data,
        file_name="transactions.txt",
        mime="text/plain"
    )

# Upload file for main app analysis
uploaded_file = st.file_uploader("Upload your transactions.txt file", type="txt")
if uploaded_file is not None:
    file_content = uploaded_file.read().decode("utf-8")
    df = load_transactions_from_text(file_content.splitlines())
    
    if not df.empty:
        st.subheader("Monthly Income and Expenses")
        monthly_data = df.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
        
        # Display monthly data
        monthly_data_display = monthly_data.copy()
        monthly_data_display.index = monthly_data_display.index.to_timestamp()
        st.write("Monthly Data Preview", monthly_data_display)
        st.bar_chart(monthly_data_display)

        # Spending by category
        st.subheader("Spending by Category")
        category_data = df[df['Type'] == 'Expense'].groupby("Category")["Amount"].sum().abs()
        fig1, ax1 = plt.subplots()
        category_data.plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax1)
        ax1.set_ylabel("")
        ax1.set_title("Spending by Category")
        st.pyplot(fig1)

        # Forecasting with ARIMA
        st.subheader("Forecasted Monthly Expenses")
        forecast = None
        try:
            if 'Expense' in monthly_data.columns and not monthly_data['Expense'].empty:
                monthly_expenses = monthly_data['Expense'].asfreq('M').fillna(0)
                if isinstance(monthly_expenses.index, pd.PeriodIndex):
                    monthly_expenses.index = monthly_expenses.index.to_timestamp()

                if len(monthly_expenses) > 1:
                    model = ARIMA(monthly_expenses, order=(1, 1, 1))
                    model_fit = model.fit()
                    forecast_object = model_fit.get_forecast(steps=6)
                    forecast = forecast_object.predicted_mean
                    conf_int = forecast_object.conf_int()

                    fig2, ax2 = plt.subplots()
                    ax2.plot(monthly_expenses, label='Historical Expenses')
                    ax2.plot(forecast.index, forecast.values, label='Forecasted Expenses', linestyle='--')
                    ax2.fill_between(forecast.index, conf_int.iloc[:, 0].values, conf_int.iloc[:, 1].values, color='gray', alpha=0.2)
                    ax2.legend()
                    ax2.set_title("Historical and Forecasted Monthly Expenses")
                    ax2.set_xlabel("Month")
                    ax2.set_ylabel("Amount ($)")
                    st.pyplot(fig2)
                else:
                    st.error("Not enough data points for forecasting.")
            else:
                st.error("Error: No expense data available for forecasting.")
        
        except Exception as e:
            st.error(f"Error during forecasting: {e}")

        # Threshold alerts
        st.subheader("Expense Threshold Alerts")
        if forecast is not None:
            alerts = [f"Month {i+1}: Predicted expense ${expense:.2f}" for i, expense in enumerate(forecast) if expense > threshold]
            if alerts:
                st.warning("Alerts: " + "; ".join(alerts))
            else:
                st.success("No alerts for the forecasted period.")
