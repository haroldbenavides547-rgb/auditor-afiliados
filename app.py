import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Auditor de Ganancias Pro", page_icon="🛡️", layout="wide")

# 2. DEFINICIÓN DE FUNCIONES
def clean_currency(value):
    """Convierte texto de moneda ($1,234.56) a número real (1234.56)"""
    if isinstance(value, str):
        # Quita el símbolo $, las comas y espacios
        value = value.replace('$', '').replace(',', '').strip()
    return pd.to_numeric(value, errors='coerce')

def map_columns(df):
    mapping = {
        'Date': 'Fecha',
        'Status': 'Estado',
        'Amount': 'Monto',
        'Commission': 'Comisión',
        'Net Profit': 'Ganancia Neta',
        'Product': 'Producto'
    }
    df.columns = [c.strip() for c in df.columns]
    return df.rename(columns=mapping)

def calculate_metrics(df):
    # Limpiar las columnas numéricas antes de sumar
    for col in ['Monto', 'Comisión', 'Ganancia Neta']:
        if col in df.columns:
            df[col] = df[col].apply(clean_currency).fillna(0)
    
    metrics = {
        'total_sales': len(df),
        'total_revenue': df['Monto'].sum(),
        'total_profit': df['Ganancia Neta'].sum(),
        'avg_ticket': df['Monto'].mean() if len(df) > 0 else 0
    }
    return metrics

# 3. INTERFAZ DE USUARIO
st.title("🛡️ Auditor de Ganancias Pro")
st.divider()

uploaded_file = st.file_uploader("Sube tu reporte CSV", type="csv")

if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)
        
        # Procesar
        df = map_columns(df_raw)
        stats = calculate_metrics(df) # Aquí ya se limpian los números
        
        # MOSTRAR MÉTRICAS
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ventas Totales", f"📦 {stats['total_sales']}")
        with col2:
            st.metric("Ingreso Bruto", f"💰 ${stats['total_revenue']:,.2f}")
        with col3:
            st.metric("Ganancia Neta", f"🚀 ${stats['total_profit']:,.2f}")
        with col4:
            st.metric("Ticket Promedio", f"📈 ${stats['avg_ticket']:,.2f}")
            
        st.divider()
        st.subheader("✅ Vista de Datos Procesados")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Sube un archivo para ver los cálculos.")
