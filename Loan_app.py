import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf  # Import numpy_financial
import plotly.express as px

# Loan amortization function
def calculate_amortization(principal, annual_rate, years, extra_monthly=0, extra_yearly=0, balloon_year=0, balloon_amount=0):
    monthly_rate = annual_rate / 12 / 100
    total_months = years * 12
    emi = npf.pmt(monthly_rate, total_months, -principal)  # Use numpy_financial's pmt function

    schedule = []
    balance = principal
    total_interest = 0

    for month in range(1, total_months + 1):
        interest = balance * monthly_rate
        principal_payment = emi - interest
        total_interest += interest

        # Handle extra payments
        principal_payment += extra_monthly
        if month % 12 == 0:  # Yearly extra payment
            principal_payment += extra_yearly

        # Handle balloon payment
        if month == balloon_year * 12 and balloon_year > 0:
            principal_payment += balloon_amount

        balance -= principal_payment
        balance = max(balance, 0)  # Avoid negative balance

        schedule.append([month, emi, interest, principal_payment, balance])

        if balance <= 0:
            break

    df = pd.DataFrame(schedule, columns=["Month", "EMI", "Interest", "Principal", "Balance"])
    return df, total_interest

# Streamlit App
st.title("Loan Amortization Calculator")
st.sidebar.header("Loan Parameters")

# Input fields
principal = st.sidebar.number_input("Loan Amount (₹)", min_value=0.0, step=1000.0, value=500000.0)
annual_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.1, step=0.1, value=7.5)
years = st.sidebar.slider("Loan Tenure (Years)", min_value=1, max_value=30, value=20)

extra_monthly = st.sidebar.number_input("Extra Monthly Payment (₹)", min_value=0.0, step=500.0, value=0.0)
extra_yearly = st.sidebar.number_input("Extra Yearly Payment (₹)", min_value=0.0, step=5000.0, value=0.0)
balloon_year = st.sidebar.slider("Balloon Payment Year (0 = None)", min_value=0, max_value=years, value=0)
balloon_amount = st.sidebar.number_input("Balloon Payment Amount (₹)", min_value=0.0, step=10000.0, value=0.0)

if st.sidebar.button("Calculate"):
    # Calculate amortization
    df, total_interest = calculate_amortization(principal, annual_rate, years, extra_monthly, extra_yearly, balloon_year, balloon_amount)
    total_payment = total_interest + principal

    st.subheader("Amortization Schedule")
    st.dataframe(df)

    # Display Total Interest and Payment
    st.write(f"### Total Interest Paid: ₹{total_interest:,.2f}")
    st.write(f"### Total Payments (Principal + Interest): ₹{total_payment:,.2f}")

    # Pie Chart
    pie_data = pd.DataFrame({
        "Category": ["Principal", "Interest"],
        "Amount": [principal, total_interest]
    })
    st.subheader("Proportion of Principal and Interest")
    fig_pie = px.pie(pie_data, values="Amount", names="Category", title="Principal vs Interest")
    st.plotly_chart(fig_pie)

    # Combined Graph
    st.subheader("Payment Cycle Overview")
    combined_chart = px.line(
        df, 
        x="Month", 
        y=["Balance", "Interest", "Principal"], 
        labels={"value": "Amount (₹)", "Month": "Month"},
        title="Balance, Interest, and Principal Over Payment Cycle"
    )
    combined_chart.update_layout(legend_title_text="Components")
    st.plotly_chart(combined_chart)

    # Amortization Benefits and Losses
    st.subheader("Loan Amortization: Benefits and Losses")
    st.markdown("""
    **Benefits**:
    - Predictable fixed payments make it easier to plan your finances.
    - Helps you systematically pay off debt over time, reducing the risk of default.
    - Extra payments and balloon payments provide flexibility to reduce loan tenure or interest burden.
    
    **Drawbacks**:
    - Fixed payments may not adapt well to changes in income or interest rates.
    - High-interest costs over long tenures may result in significantly higher overall payments.
    - Early repayment penalties might apply for some loans.

    """)
    st.sidebar.info("Adjust the parameters to see how extra payments or balloon payments impact the schedule!")
