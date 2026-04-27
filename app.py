import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Auditor de Ganancias Pro", page_icon="🛡️", layout="wide")

# 2. FUNCIÓN DE LIMPIEZA EXTREMA
def limpiar_dinero(serie):
    # Convierte a string, quita basura y pasa a número
    return pd.to_numeric(
        serie.astype(str)
        .str.replace(r'[^\d.]', '', regex=True), 
        errors='coerce'
    ).fillna(0)

# 3. INTERFAZ
st.title("🛡️ Auditor de Ganancias Universal")
st.markdown("---")

archivo = st.file_uploader("Sube tu reporte CSV", type="csv")

if archivo:
    try:
        # Leer el CSV
        df = pd.read_csv(archivo)
        st.success("✅ Archivo detectado")
        
        # Mostrar las columnas que encontró el sistema
        columnas = df.columns.tolist()
        
        st.subheader("⚙️ Configuración Manual")
        st.write("Selecciona qué nombre tiene cada dato en tu archivo:")
        
        col1, col2 = st.columns(2)
        with col1:
            col_monto = st.selectbox("Columna de VENTAS (Dinero que entró)", columnas)
        with col2:
            col_neta = st.selectbox("Columna de GANANCIA NETA (Tu tajada)", columnas)
            
        if st.button("🚀 GENERAR AUDITORÍA"):
            # Procesar los datos elegidos por el usuario
            df['VENTA_NUM'] = limpiar_dinero(df[col_monto])
            df['NETA_NUM'] = limpiar_dinero(df[col_neta])
            
            # Cálculos
            total_v = len(df)
            suma_bruta = df['VENTA_NUM'].sum()
            suma_neta = df['NETA_NUM'].sum()
            roi = (suma_neta / suma_bruta * 100) if suma_bruta > 0 else 0
            
            # Mostrar Resultados
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Ventas Totales", f"{total_v}")
            m2.metric("Ingreso Bruto", f"${suma_bruta:,.2f}")
            m3.metric("Ganancia Neta", f"${suma_neta:,.2f}")
            m4.metric("Rendimiento (ROI)", f"{roi:.1f}%")
            
            st.subheader("📋 Datos Auditados")
            st.dataframe(df[[col_monto, col_neta]], use_container_width=True)
            
            # Botón de descarga
            st.download_button("📥 Descargar Resultados", df.to_csv(index=False), "auditoria_final.csv")

    except Exception as e:
        st.error(f"Hubo un problema: {e}")
else:
    st.info("Sube el archivo para configurar el auditor.")

st.markdown("---")
st.caption("Si esto no lee tu archivo, es que el formato del CSV es muy inusual.")
