import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Page setup must be first
st.set_page_config(page_title="Startup Investment Dashboard", layout="wide")

# Add dashboard title at the top
st.title("🚀 Startup Investment Analysis Dashboard")

# Add description
st.markdown("""
Welcome to the Startup Investment Analysis Dashboard! This dashboard provides insights into startup funding trends and patterns.

You can use the filters on the left sidebar to explore different aspects of the data.
""")

# CSV path
file_path = r"C:\Users\fariz\OneDrive\Desktop\experiments\misc\Startup_Funding.csv"

# Load data
@st.cache_data
def load_data(path):
    if os.path.exists(path):
        df = pd.read_csv(path, encoding='utf-8')
        df.columns = df.columns.str.strip()
        df.dropna(how='all', inplace=True)
        return df
    else:
        return None

# Load data first
df = load_data(file_path)

if df is None:
    st.error(f"❌ File not found at: {file_path}")
    st.stop()
else:
    st.success("✅ Data loaded successfully!")

    # Process date
    if 'Date dd/mm/yyyy' in df.columns:
        df['Date'] = pd.to_datetime(df['Date dd/mm/yyyy'], format='%d/%m/%Y', errors='coerce')
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month_name()

    # Process funding amount
    if 'Amount in USD' in df.columns:
        df['Amount in USD'] = (
            df['Amount in USD']
            .astype(str)
            .str.replace(',', '', regex=False)
            .str.extract(r'(\d+)', expand=False)
            .astype(float)
        )

    # Show data
    with st.expander("📄 Show Raw Data"):
        st.dataframe(df.head())

    # Sidebar filters first
    with st.sidebar:
        st.header("🔍 Filters")
        years = df['Year'].dropna().unique()
        selected_years = st.multiselect(
            "Select Year(s):",
            sorted(years),
            default=sorted(years),
            key='year_filter'
        )

    # Filter data based on selected years
    if selected_years:
        df = df[df['Year'].isin(selected_years)]

    # Investment Over Time
    st.subheader("📈 Investment Over Time")
    if not df.empty and 'Date' in df.columns:
        monthly_funding = df.groupby(df['Date'].dt.to_period('M'))['Amount in USD'].sum()
        monthly_funding.index = monthly_funding.index.astype(str)
        st.line_chart(monthly_funding)
    else:
        st.warning("No data available for the selected filter.")

    # Top Startups
    if 'Startup Name' in df.columns:
        st.subheader("🏆 Top 10 Funded Startups")
        top_startups = df.groupby('Startup Name')['Amount in USD'].sum().sort_values(ascending=False).head(10)
        st.bar_chart(top_startups)

    # Top Industries
    if 'Industry Vertical' in df.columns:
        st.subheader("🏭 Top 10 Funded Industries")
        top_industries = df.groupby('Industry Vertical')['Amount in USD'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=top_industries.values, y=top_industries.index, ax=ax)
        ax.set_xlabel("Funding Amount (USD)")
        ax.set_title("Top Industries by Investment")
        st.pyplot(fig)

