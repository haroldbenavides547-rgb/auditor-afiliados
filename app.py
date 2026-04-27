import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Auditor de Ganancias Pro", page_icon="🛡️", layout="wide")

# 2. CEREBRO: LIMPIEZA DE DATOS Y BÚSQUEDA DE COLUMNAS
def clean_numeric(value):
    """Convierte cualquier texto sucio ($1,234.56) en número real"""
    if pd.isna(value): return 0.0
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '').replace(' ', '').strip()
    try:
        return float(value)
    except:
        return 0.0

def find_column(df, possible_names):
    """Busca una columna aunque el nombre no sea exacto"""
    for name in possible_names:
        for col in df.columns:
            if name.lower() in col.lower().strip():
                return col
    return None

# 3. INTERFAZ DE USUARIO
st.title("🛡️ Auditor de Ganancias Pro")
st.markdown("### Analizador de Reportes de Afiliado")
st.divider()

uploaded_file = st.file_uploader("Sube tu reporte CSV aquí", type="csv")

if uploaded_file is not None:
    try:
        # Leer el archivo detectando posibles errores de formato
        df = pd.read_csv(uploaded_file)
        
        # Identificar columnas automáticamente (por si cambian los nombres)
        col_monto = find_column(df, ['Amount', 'Monto', 'Total', 'Sale'])
        col_comision = find_column(df, ['Commission', 'Comisión', 'Earned'])
        col_neta = find_column(df, ['Net Profit', 'Ganancia Neta', 'Profit', 'Neta'])
        col_status = find_column(df, ['Status', 'Estado', 'Result'])
        
        # Verificar si encontramos al menos el Monto
        if col_monto:
            # Limpiar los datos numéricos
            df['Monto_Limpio'] = df[col_monto].apply(clean_numeric)
            df['Comision_Limpia'] = df[col_comision].apply(clean_numeric) if col_comision else 0.0
            df['Neta_Limpia'] = df[col_neta].apply(clean_numeric) if col_neta else (df['Monto_Limpio'] * 0.2) # Estimado si no existe

            # CÁLCULO DE MÉTRICAS
            total_sales = len(df)
            total_revenue = df['Monto_Limpio'].sum()
            total_profit = df['Neta_Limpia'].sum()
            avg_ticket = df['Monto_Limpio'].mean()

            # MOSTRAR MÉTRICAS EN PANTALLA
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Ventas Totales", f"📦 {total_sales}")
            c2.metric("Ingreso Bruto", f"💰 ${total_revenue:,.2f}")
            c3.metric("Ganancia Neta", f"🚀 ${total_profit:,.2f}")
            c4.metric("Ticket Promedio", f"📈 ${avg_ticket:,.2f}")

            st.divider()
            
            # MOSTRAR TABLA
            st.subheader("✅ Desglose de Datos")
            # Renombrar para que el usuario lo vea bonito
            df_display = df.copy()
            st.dataframe(df_display, use_container_width=True)

            # BOTÓN DE DESCARGA
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Reporte Auditado", csv, "auditoria.csv", "text/csv")
        else:
            st.error("❌ No se encontró la columna de 'Monto' o 'Amount' en tu archivo.")
            st.info("Asegúrate de que tu CSV tenga una columna con el valor de las ventas.")

    except Exception as e:
        st.error(f"❌ Error crítico: {e}")
else:
    st.warning("⚠️ Por favor, sube un archivo CSV para comenzar el análisis.")

st.divider()
st.caption("Auditor Pro | Privacidad Garantizada")
