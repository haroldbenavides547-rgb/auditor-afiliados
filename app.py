import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA (Debe ir primero)
st.set_page_config(page_title="Auditor de Ganancias Pro", page_icon="🛡️", layout="wide")

# 2. DEFINICIÓN DE FUNCIONES (Las herramientas del manual)

def map_columns(df):
    """Limpia nombres de columnas y las traduce al español"""
    mapping = {
        'Date': 'Fecha',
        'Status': 'Estado',
        'Amount': 'Monto',
        'Commission': 'Comisión',
        'Net Profit': 'Ganancia Neta',
        'Product': 'Producto'
    }
    # Limpiar espacios invisibles en los nombres de las columnas
    df.columns = [c.strip() for c in df.columns]
    return df.rename(columns=mapping)

def calculate_metrics(df):
    """Calcula los totales asegurando que no haya errores matemáticos"""
    # Convertir columnas a números, si hay error pone 0 (evita que la app se rompa)
    for col in ['Monto', 'Comisión', 'Ganancia Neta']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    metrics = {
        'total_sales': len(df),
        'total_revenue': df['Monto'].sum() if 'Monto' in df.columns else 0.0,
        'total_profit': df['Ganancia Neta'].sum() if 'Ganancia Neta' in df.columns else 0.0,
        'avg_ticket': df['Monto'].mean() if 'Monto' in df.columns else 0.0
    }
    return metrics

# 3. INTERFAZ DE USUARIO (Lo que el cliente ve)

st.title("🛡️ Auditor de Ganancias Pro")
st.markdown("### Análisis de ROI y Comisiones en Tiempo Real")
st.divider()

# Cargador de archivos
uploaded_file = st.file_uploader("Sube tu reporte CSV (Exportado de tu plataforma)", type="csv")

if uploaded_file is not None:
    try:
        # Leer el archivo
        df_raw = pd.read_csv(uploaded_file)
        
        # Procesar datos usando las funciones de arriba
        df = map_columns(df_raw)
        stats = calculate_metrics(df)
        
        # MOSTRAR MÉTRICAS (Ecuaciones aplicadas)
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
        
        # Mostrar tabla con resultados
        st.subheader("✅ Desglose de Datos Auditados")
        st.dataframe(df, use_container_width=True)
        
        # Botón para que el usuario descargue el resultado limpio
        csv_ready = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte en Excel/CSV",
            data=csv_ready,
            file_name="auditoria_final.csv",
            mime="text/csv",
        )
        
    except Exception as e:
        st.error(f"❌ Error al procesar: {e}")
        st.info("Sugerencia: Revisa que tu archivo CSV no esté dañado.")
else:
    st.info("👋 Bienvenida/o. Por favor, sube un archivo CSV para empezar la auditoría.")

# Pie de página
st.divider()
st.caption("Herramienta Privada de Auditoría | Proceso 100% Seguro")
