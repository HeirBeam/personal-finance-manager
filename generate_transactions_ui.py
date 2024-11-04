import streamlit as st
import pandas as pd
from io import StringIO

# Initialize session state to store transactions
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

st.title("Transaction Data Entry for Personal Finance Manager")

# Input form for new transaction
with st.form("transaction_form"):
    st.subheader("Enter Transaction Details")
    
    date = st.date_input("Date")
    transaction_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
    category = st.text_input("Category")
    
    # Add transaction button
    submit_button = st.form_submit_button("Add Transaction")
    if submit_button:
        st.session_state.transactions.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Type": transaction_type,
            "Amount": f"{amount:.2f}",
            "Category": category
        })
        st.success("Transaction added!")

# Display entered transactions
st.subheader("Transaction List")
if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    st.write(df)

    # Generate .txt file
    def convert_to_txt(df):
        output = StringIO()
        # Manually format each row
        output.write("Date, Type, Amount, Category\n")
        for index, row in df.iterrows():
            output.write(f"{row['Date']}, {row['Type']}, {row['Amount']}, {row['Category']}\n")
        return output.getvalue().encode('utf-8')


    # Download button
    txt_data = convert_to_txt(df)
    st.download_button(
        label="Download Transactions as .txt",
        data=txt_data,
        file_name="transactions.txt",
        mime="text/plain"
    )
else:
    st.info("No transactions added yet. Please enter some details above.")

# Reset button to clear transactions
if st.button("Clear Transactions"):
    st.session_state.transactions = []
    st.success("Transaction list cleared.")
