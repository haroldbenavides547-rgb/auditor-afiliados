import streamlit as st
import pandas as pd

# Configuración de Página
st.set_page_config(
    page_title="Auditor de Ganancias Pro",
    page_icon="🛡️"
)

# Robustez: Envuelve la lectura del CSV en un bloque try/except
try:
    uploaded_file = st.sidebar.file_uploader("Sube tu reporte (CSV o Excel)", type=["csv", "xlsx"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        
        # Verifica si las columnas 'Inversión' e 'Ingresos' están presentes
        if 'Inversión' not in df.columns or 'Ingresos' not in df.columns:
            st.error('⚠️ El archivo no tiene el formato correcto. Asegúrate de incluir las columnas Inversión e Ingresos.')
            st.stop()
        
        final_df = map_columns(df)
        
        if len(final_df.columns) < 3:
            st.error("❌ Error: Columnas no encontradas. Asegúrate de tener: Producto, Inversión e Ingresos.")
        else:
            final_df = calculate_metrics(final_df)
            render_dashboard(final_df)
            
except Exception as e:
    st.error(f"Error crítico: {e}")
else:
    st.info("👋 Bienvenido. Por favor sube un archivo para auditar tu rentabilidad.")

# ==============================
# 2. CARGA DE ESTILOS
# ==============================
def load_custom_css():
    """Carga el archivo CSS externo para el diseño de lujo"""
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró styles.css en la carpeta raíz.")

# ==============================
# 3. FUNCIONES DE PROCESAMIENTO
# ==============================
def clean_currency(column):
    """Limpia profundamente cualquier carácter no numérico y fuerza float"""
    # Convertimos a string y eliminamos todo lo que no sea número o punto
    cleaned = column.astype(str).str.replace(r'[^\d.]', '', regex=True)
    # Convertimos a numérico, los valores vacíos o erróneos pasan a ser 0.0
    return pd.to_numeric(cleaned, errors='coerce').fillna(0.0)

def map_columns(df):
    """Mapea columnas según nombres comunes (Mapeo Inteligente)"""
    col_map = {
        'Campaña': ['producto', 'item', 'campaña', 'curso'],
        'Inversión': ['inversión', 'gasto', 'costo', 'ads', 'spend'],
        'Ingresos': ['ingresos', 'ventas', 'bruta', 'comisión', 'revenue']
    }
    
    final_df = pd.DataFrame()
    for key, options in col_map.items():
        matches = [c for c in df.columns if any(opt.lower() in c.lower() for opt in options)]
        if matches:
            final_df[key] = df[matches[0]]
        else:
            # Busca la columna que más se parezca
            closest_match = min(df.columns, key=lambda x: sum(1 for opt in options if opt.lower() in x.lower()), default=None)
            if closest_match:
                final_df[key] = df[closest_match]
    return final_df

def calculate_metrics(final_df):
    """Asegura que los cálculos se hagan sobre tipos numéricos"""
    # Forzamos la limpieza de las columnas críticas antes de operar
    final_df['Inversión'] = clean_currency(final_df['Inversión'])
    final_df['Ingresos'] = clean_currency(final_df['Ingresos'])
    
    # Realizamos las operaciones matemáticas
    final_df['Profit'] = final_df['Ingresos'] - final_df['Inversión']
    
    # ROI con protección contra división por cero
    final_df['ROI'] = np.where(
        final_df['Inversión'] > 0, 
        (final_df['Profit'] / final_df['Inversión']) * 100, 
        0.0
    )
    
    # Aplica las reglas de ROI
    final_df.loc[(final_df['Inversión'] == 0) & (final_df['Ingresos'].notna()), 'ROI'] = float('inf')
    final_df.loc[final_df['ROI'] == 0, 'ROI'] = 0.0
    
    # Maneja filas con datos incompletos
    final_df.loc[(final_df['Inversión'].isna()) | (final_df['Ingresos'].isna()), 'ROI'] = float('inf')
    
    # Crea la columna Estado
    final_df['Estado'] = np.where(final_df['ROI'] == float('inf'), 'Orgánico',
                                 np.where(final_df['ROI'] > 0, 'Rentable', 
                                          np.where(final_df['ROI'] == 0, 'Punto de Equilibrio', 'Fuga de Dinero')))
    
    return final_df

# ==============================
# 4. INTERFAZ DE USUARIO (DASHBOARD)
# ==============================
def render_dashboard(final_df):
    """Renderiza métricas de lujo y visualizaciones"""
    
    # MÉTRICAS EN TARJETAS DE CRISTAL
    with st.container():
        st.title("💎 Auditor de Ganancias Pro")
        st.markdown("### Auditoría de Rentabilidad para Afiliados Pro")
        
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f'''<div class="card">
                <p style="color:#888; margin:0; font-size:0.9rem;">VENTAS TOTALES</p>
                <h2 style="color:#00FF88; margin:0;">${final_df['Ingresos'].sum():,.2f}</h2>
            </div>''', unsafe_allow_html=True)
        with m2:
            profit_t = final_df['Profit'].sum()
            color = "#00FF88" if profit_t >= 0 else "#FF3131"
            st.markdown(f'''<div class="card">
                <p style="color:#888; margin:0; font-size:0.9rem;">PROFIT NETO</p>
                <h2 style="color:{color}; margin:0;">${profit_t:,.2f}</h2>
            </div>''', unsafe_allow_html=True)
    
    st.divider()
    
    # TABS PARA ORGANIZACIÓN
    tab1, tab2 = st.tabs(["📈 Análisis Visual", "🔍 Auditoría de Campañas"])
    
    with tab1:
        fig = px.bar(final_df, x='Campaña', y='Profit', color='Estado',
                     color_discrete_map={
                         'Rentable': '#00FF00', 
                         'Fuga de Dinero': '#FF0000', 
                         'Punto de Equilibrio': '#FFFF00', 
                         'Orgánico': '#00FFFF'
                     },
                     category_orders={'Estado': ['Rentable', 'Fuga de Dinero', 'Punto de Equilibrio', 'Orgánico']})
        fig.update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.markdown("### 🛡️ Detector de Fugas de Dinero")
        for _, row in final_df.iterrows():
            if pd.isna(row['Campaña']) or (row['Inversión'] == 0 and row['Ingresos'] == 0):
                continue
            
            if row['Estado'] == 'Rentable':
                message = f"**{row['Campaña']}**: Es rentable. ROI: {row['ROI']:.1f}% | Profit: ${row['Profit']:,.2f}"
                icon = "\u2705"
            elif row['Estado'] == 'Orgánico':
                message = f"**{row['Campaña']}**: Es tráfico orgánico puro. ¡Ventas sin gasto! | Profit: ${row['Profit']:,.2f}"
                icon = "\U0001F680"
            elif row['Estado'] == 'Punto de Equilibrio':
                message = f"**{row['Campaña']}**: Es un Punto de Equilibrio. Recuperaste la inversión."
                icon = "\U0001F7E1"
            elif row['Estado'] == 'Fuga de Dinero':
                message = f"**{row['Campaña']}**: Es una fuga de dinero. ROI: {-abs(row['ROI']):,.1f}% | Profit: -${abs(row['Profit']):,.2f}"
                icon = "\u274C"
            
            st.markdown(f"{icon} {message}")

# ==============================
# 5. EJECUCIÓN PRINCIPAL
# ==============================
load_custom_css()
