import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Set page config
st.set_page_config(page_title="Smart Demand Signals", layout="wide")

# Function to load data
@st.cache_data
def load_data():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assume the file is in the data folder relative to the script
    file_path = os.path.join(script_dir, 'data', 'database_clean.xlsx')  # or 'cleandataset.csv'
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)  # or pd.read_csv(file_path)
    else:
        st.error(f"Dataset file not found at {file_path}. Please ensure 'database_clean.xlsx' is in the 'data' folder.")
        return pd.DataFrame()
    return df

# Load the data
df = load_data()
if df.empty:
    st.stop()

# Rename columns to match assumptions (adjust based on actual data)
df = df.rename(columns={
    'Fecha': 'Date',
    'Id.Cliente': 'Client_ID',
    'Familia_H': 'Product_Family',
    'Unidades': 'Quantity',
    'Valores_H': 'Transaction_Value',
    'Potencial_H': 'Client_Potential'
})

# Drop unnecessary columns if any
if 'Id. Producto' in df.columns:
    df = df.drop(columns=['Id. Producto'])

# Convert Date to datetime
df['Date'] = pd.to_datetime(df['Date'])

# 1. DATA PREPARATION

# Create Analytical_Block
def classify_family(family_name):
    if pd.isna(family_name): return 'Technical'
    name = str(family_name).upper()
    # Busca si la palabra contiene estos fragmentos, no hace falta que sea exacta
    if 'ANESTE' in name or 'AGUJA' in name or 'DESINFEC' in name:
        return 'Commodities'
    return 'Technical'# Escalar el Nivel de Riesgo de 1 a 100
min_score = alerts_df['Priority_Score'].min()
max_score = alerts_df['Priority_Score'].max()

if max_score > min_score:
    alerts_df['Priority_Score'] = ((alerts_df['Priority_Score'] - min_score) / (max_score - min_score)) * 99 + 1
else:
    alerts_df['Priority_Score'] = 50 # Por si solo hay una alerta en total

# Redondear para que quede bonito
alerts_df['Priority_Score'] = alerts_df['Priority_Score'].round(0)

df['Analytical_Block'] = df['Product_Family'].apply(classify_family)
# Calculate Loyalty Factor
# Group by Client_ID to get Average Monthly Spend
client_spend = df.groupby('Client_ID').agg(
    Total_Spend=('Transaction_Value', 'sum'),
    Months_Active=('Date', lambda x: (x.max() - x.min()).days / 30 if len(x) > 1 else 1),
    Potential=('Client_Potential', 'first')
).reset_index()
client_spend['Average_Monthly_Spend'] = client_spend['Total_Spend'] / client_spend['Months_Active']
client_spend['Loyalty_Factor'] = client_spend.apply(
    lambda row: 'Loyal' if row['Average_Monthly_Spend'] >= 0.85 * row['Potential'] else 'Promiscuous', axis=1
)

# Merge back to df
df = df.merge(client_spend[['Client_ID', 'Loyalty_Factor', 'Average_Monthly_Spend', 'Potential']], on='Client_ID')

# Group transactional data at [Client_ID, Date, Product_Family] level
df_agg = df.groupby(['Client_ID', 'Date', 'Product_Family']).agg(
    Quantity=('Quantity', 'sum'),
    Transaction_Value=('Transaction_Value', 'sum'),
    Analytical_Block=('Analytical_Block', 'first'),
    Loyalty_Factor=('Loyalty_Factor', 'first'),
    Average_Monthly_Spend=('Average_Monthly_Spend', 'first'),
    Potential=('Potential', 'first')
).reset_index()

# Sort by Client_ID, Product_Family, Date
df_agg = df_agg.sort_values(['Client_ID', 'Product_Family', 'Date'])

# Calculate Days between purchases per Client/Family
df_agg['Days_Between'] = df_agg.groupby(['Client_ID', 'Product_Family'])['Date'].diff().dt.days

# 2. MATHEMATICAL CRITERIA FOR ALERTS

# Calculate Mean and Std per Client/Family
stats = df_agg.groupby(['Client_ID', 'Product_Family']).agg(
    Mean_Qty=('Quantity', 'mean'),
    Std_Qty=('Quantity', 'std'),
    Mean_Days=('Days_Between', 'mean'),
    Std_Days=('Days_Between', 'std'),
    Purchase_Count=('Quantity', 'count')
).reset_index()

# Fallback: If <3 purchases, use global Family Mean and Std
global_stats = df_agg.groupby('Product_Family').agg(
    Global_Mean_Qty=('Quantity', 'mean'),
    Global_Std_Qty=('Quantity', 'std'),
    Global_Mean_Days=('Days_Between', 'mean'),
    Global_Std_Days=('Days_Between', 'std')
).reset_index()

stats = stats.merge(global_stats, on='Product_Family', how='left')
stats['Mean_Qty'] = stats.apply(lambda row: row['Global_Mean_Qty'] if row['Purchase_Count'] < 3 else row['Mean_Qty'], axis=1)
stats['Std_Qty'] = stats.apply(lambda row: row['Global_Std_Qty'] if row['Purchase_Count'] < 3 else row['Std_Qty'], axis=1)
stats['Mean_Days'] = stats.apply(lambda row: row['Global_Mean_Days'] if row['Purchase_Count'] < 3 else row['Mean_Days'], axis=1)
stats['Std_Days'] = stats.apply(lambda row: row['Global_Std_Days'] if row['Purchase_Count'] < 3 else row['Std_Days'], axis=1)

# Get last purchase per Client/Family
last_purchase = df_agg.groupby(['Client_ID', 'Product_Family']).agg(
    Last_Date=('Date', 'max'),
    Last_Qty=('Quantity', 'last'),
    Average_Transaction_Value=('Transaction_Value', 'mean'),
    Analytical_Block=('Analytical_Block', 'first'),
    Loyalty_Factor=('Loyalty_Factor', 'first'),
    Average_Monthly_Spend=('Average_Monthly_Spend', 'first'),
    Potential=('Potential', 'first')
).reset_index()

# Assume today is the max date in the dataset
today = df_agg['Date'].max()

last_purchase['Days_Since_Last'] = (today - last_purchase['Last_Date']).dt.days

# Merge stats
alerts_df = last_purchase.merge(stats[['Client_ID', 'Product_Family', 'Mean_Qty', 'Std_Qty', 'Mean_Days', 'Std_Days']], on=['Client_ID', 'Product_Family'])

# Rule A: Commodities
alerts_df['Alert_Reason'] = ''
alerts_df['Opportunity_Value'] = 0.0
alerts_df['Days_Delayed'] = 0.0

for idx, row in alerts_df.iterrows():
    if row['Analytical_Block'] == 'Commodities':
        if row['Days_Since_Last'] >= row['Mean_Days']:
            alerts_df.at[idx, 'Alert_Reason'] = 'Ventana de Captura'
            alerts_df.at[idx, 'Opportunity_Value'] = row['Potential'] - row['Average_Monthly_Spend']
            alerts_df.at[idx, 'Days_Delayed'] = row['Days_Since_Last'] - row['Mean_Days']
    elif row['Analytical_Block'] == 'Technical':
        # Rule B
        expected_days = row['Mean_Days'] * (row['Last_Qty'] / row['Mean_Qty']) if row['Mean_Qty'] != 0 else row['Mean_Days']
        qty_condition = row['Last_Qty'] < row['Mean_Qty'] - 1 * row['Std_Qty']
        time_condition = row['Days_Since_Last'] > expected_days + 1.5 * row['Std_Days']
        if qty_condition or time_condition:
            if qty_condition:
                alerts_df.at[idx, 'Alert_Reason'] = 'Caída drástica de volumen'
            elif time_condition:
                alerts_df.at[idx, 'Alert_Reason'] = 'Retraso anómalo en tiempo'
            alerts_df.at[idx, 'Opportunity_Value'] = row['Average_Monthly_Spend']
            alerts_df.at[idx, 'Days_Delayed'] = max(0, row['Days_Since_Last'] - expected_days)

# Fill NaNs in Opportunity_Value with 0
alerts_df['Opportunity_Value'] = alerts_df['Opportunity_Value'].fillna(0)

# Filter out no alerts
alerts_df = alerts_df[alerts_df['Alert_Reason'] != '']

# 3. PRIORITIZATION SCORE
# Escalar el Nivel de Riesgo de 1 a 100
min_score = alerts_df['Priority_Score'].min()
max_score = alerts_df['Priority_Score'].max()

if max_score > min_score:
    alerts_df['Priority_Score'] = ((alerts_df['Priority_Score'] - min_score) / (max_score - min_score)) * 99 + 1
else:
    alerts_df['Priority_Score'] = 50 # Por si solo hay una alerta en total

# Redondear para que quede bonito
alerts_df['Priority_Score'] = alerts_df['Priority_Score'].round(0)
# Rename columns for display
alerts_df = alerts_df.rename(columns={
    'Priority_Score': 'Nivel de Riesgo',
    'Alert_Reason': 'Motivo',
    'Opportunity_Value': 'Valor_Oportunidad'
})

# 4. OUTPUT & UI

st.title("Smart Demand Signals Dashboard")

# Sidebar filter
filter_option = st.sidebar.selectbox("Filter Alerts by Analytical Block", ["All", "Commodities", "Technical"])

if filter_option == "All":
    filtered_alerts = alerts_df
else:
    filtered_alerts = alerts_df[alerts_df['Analytical_Block'] == filter_option]

# Display table
st.subheader("Prioritized Alerts")
if not filtered_alerts.empty:
    # Add Register Action column
    filtered_alerts['Register_Action'] = ''

    # Display with editable Register_Action
    edited_df = st.data_editor(
        filtered_alerts[['Client_ID', 'Product_Family', 'Motivo', 'Nivel de Riesgo', 'Valor_Oportunidad', 'Register_Action']],
        column_config={
            "Register_Action": st.column_config.SelectboxColumn(
                "Register Action",
                help="Simulate ML Feedback Loop",
                options=["", "Success", "False Positive"],
                required=False,
            )
        },
        hide_index=True,
    )
else:
    st.write("No alerts to display.")