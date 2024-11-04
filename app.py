import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

def load_transactions_from_text(file_lines):
    # Process each line as a transaction
    transactions = []
    for line in file_lines:
        try:
            date, transaction_type, amount, category = line.strip().split(", ")
            transactions.append({
                "Date": pd.to_datetime(date),  # Convert date string to datetime
                "Type": transaction_type,
                "Amount": float(amount),  # Convert amount to float
                "Category": category
            })
        except ValueError as e:
            print(f"Skipping line due to error: {line} - {e}")
    
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(transactions)
    
    # Check if DataFrame is empty
    if df.empty:
        print("Warning: The DataFrame is empty. Please check the input data format.")
        return df

    # Apply transformations
    df['Amount'] = df.apply(lambda x: x['Amount'] if x['Type'] == 'Income' else -x['Amount'], axis=1)
    df['Month'] = df['Date'].dt.to_period('M')  # Add a monthly period column
    
    return df

# Streamlit interface
st.title("Personal Finance Manager")

uploaded_file = st.file_uploader("Upload your text file", type="txt")
if uploaded_file is not None:
    # Decode and load data
    file_content = uploaded_file.read().decode("utf-8")
    df = load_transactions_from_text(file_content.splitlines())
    
    # Display the DataFrame in Streamlit for debugging
    st.write("DataFrame Preview:", df)
    
    # Ensure DataFrame is not empty before proceeding
    if df.empty:
        st.error("Error: The uploaded file resulted in an empty DataFrame. Check the file format.")
    else:
        # Calculate monthly income and expenses without changing the index type
        st.subheader("Monthly Income and Expenses")
        monthly_data = df.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)

        # Create a separate DataFrame for display with DatetimeIndex
        monthly_data_display = monthly_data.copy()
        monthly_data_display.index = monthly_data_display.index.to_timestamp()

        # Display and plot monthly data
        st.write("Monthly Data:", monthly_data_display)
        st.bar_chart(monthly_data_display)

        # Spending by Category (Taking absolute values to avoid negative amounts)
        st.subheader("Spending by Category")
        category_data = df[df['Type'] == 'Expense'].groupby("Category")["Amount"].sum().abs()
        fig1, ax1 = plt.subplots()
        category_data.plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax1)
        ax1.set_ylabel("")
        ax1.set_title("Spending by Category")
        st.pyplot(fig1)

        # Forecasting with ARIMA
        st.subheader("Forecasted Monthly Expenses")
        
        # Initialize forecast variable
        forecast = None
        
        try:
            # Ensure 'Expense' column exists in monthly_data and is non-empty
            if 'Expense' in monthly_data.columns and not monthly_data['Expense'].empty:
                # Focusing on Monthly Expenses for Forecasting
                monthly_expenses = monthly_data['Expense'].asfreq('M').fillna(0)

                # Convert PeriodIndex to DatetimeIndex if necessary
                if isinstance(monthly_expenses.index, pd.PeriodIndex):
                    monthly_expenses.index = monthly_expenses.index.to_timestamp()

                # Debugging: Display the first few rows of monthly_expenses
                st.write("Monthly Expenses for Forecasting (after asfreq):")
                st.write(monthly_expenses.head())

                # Check if monthly_expenses is still non-empty and has at least two data points
                if isinstance(monthly_expenses, pd.Series) and len(monthly_expenses) > 1:
                    # Build and Fit ARIMA Model
                    model = ARIMA(monthly_expenses, order=(1, 1, 1))
                    model_fit = model.fit()

                    # Forecast Expenses for Next 6 Months using get_forecast for safer indexing
                    forecast_object = model_fit.get_forecast(steps=6)
                    forecast = forecast_object.predicted_mean
                    conf_int = forecast_object.conf_int()

                    st.write("Forecasted Expenses for Next 6 Months:", forecast)
                    st.write("Confidence Intervals for Forecast:", conf_int)

                    # Plotting Historical Data, Forecasted Expenses, and Confidence Intervals
                    fig2, ax2 = plt.subplots()
                    ax2.plot(monthly_expenses, label='Historical Expenses')
                    ax2.plot(forecast.index, forecast.values, label='Forecasted Expenses', linestyle='--')  # Use .values
                    ax2.fill_between(forecast.index, conf_int.iloc[:, 0].values, conf_int.iloc[:, 1].values, color='gray', alpha=0.2)  # Use .values
                    ax2.legend()
                    ax2.set_title("Historical and Forecasted Monthly Expenses")
                    ax2.set_xlabel("Month")
                    ax2.set_ylabel("Amount ($)")
                    st.pyplot(fig2)
                else:
                    st.error("Not enough data points for forecasting. Monthly expenses require at least two data points.")
            else:
                st.error("Error: No expense data available for forecasting.")

        except Exception as e:
            st.error(f"Error during forecasting: {e}")

        # Alerts for Threshold
        st.subheader("Expense Threshold Alerts")
        threshold = st.number_input("Set Expense Threshold", value=3000)
        
        # Check if forecast was successful before generating alerts
        if forecast is not None:
            alerts = [f"Month {i+1}: Predicted expense ${expense:.2f}" 
                      for i, expense in enumerate(forecast) if expense > threshold]
            if alerts:
                st.warning("Alerts: " + "; ".join(alerts))
            else:
                st.success("No alerts for the forecasted period.")
