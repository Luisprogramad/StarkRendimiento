import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="StarkRendimiento", page_icon="🦅", layout="centered")

# --- ESTILOS PREMIUM (MODO OSCURO Y DORADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Helvetica Neue', sans-serif; }
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #D4AF37;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    [data-testid="stSidebar"] { background-color: #12151c; border-right: 1px solid #D4AF37; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
@st.cache_data(ttl=300)
def obtener_precio_actual(ticker):
    try:
        data = yf.Ticker(ticker)
        precio = data.history(period="1d")['Close'].iloc[-1]
        return round(precio, 2)
    except:
        return 0.0

@st.cache_data(ttl=600)
def obtener_clima_local():
    try:
        url = "https://wttr.in/Rio+Grande+Argentina?format=%t|%C|%w"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            datos = res.text.split('|')
            return {"temp": datos[0], "condicion": datos[1], "viento": datos[2]}
    except:
        pass
    return {"temp": "--°C", "condicion": "No disponible", "viento": "-- km/h"}

# --- BARRA DE NAVEGACIÓN LATERAL ---
st.sidebar.title("🦅 StarkRendimiento")
st.sidebar.markdown("---")
seccion = st.sidebar.radio("Navegación:", ["📊 Panel del Fondo", "👤 Mi Portafolio", "📍 Panel Local", "🌍 Mercado Global"])

# --- SECCIÓN 1: PANEL GLOBAL DEL FONDO (NUEVO) ---
if seccion == "📊 Panel del Fondo":
    st.title("Transparencia y Gestión")
    st.write("Métricas globales del capital administrado por StarkRendimiento.")
    
    # Métricas Globales Simuladas
    col1, col2, col3 = st.columns(3)
    col1.metric("Inversores Activos", "24", "+3 este mes")
    col2.metric("Capital Gestionado", "$45,250 USD", "+$5,000 USD")
    col3.metric("Rendimiento Anual", "14.2%", "+2.1%")
    
    st.markdown("---")
    
    # Gráfico 1: Distribución del Fondo (Dona)
    st.subheader("Distribución de Activos")
    datos_activos = pd.DataFrame({
        "Activo": ["S&P 500 (SPY)", "Bonos (AL30)", "Energía (YPF)", "Liquidez"],
        "Porcentaje": [50, 25, 15, 10]
    })
    
    fig_pie = px.pie(datos_activos, values='Porcentaje', names='Activo', hole=0.5, 
                     color_discrete_sequence=['#D4AF37', '#1f77b4', '#2ca02c', '#7f7f7f'])
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'))
    st.plotly_chart(fig_pie, use_container_width=True)

    # Gráfico 2: Crecimiento del Fondo (Barras)
    st.subheader("Crecimiento Histórico del Capital")
    datos_crecimiento = pd.DataFrame({
        "Mes": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
        "Capital (USD)": [30000, 32500, 36000, 39500, 42000, 45250]
    })
    
    fig_bar = px.bar(datos_crecimiento, x='Mes', y='Capital (USD)', text='Capital (USD)',
                     color_discrete_sequence=['#D4AF37'])
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'))
    st.plotly_chart(fig_bar, use_container_width=True)

# --- SECCIÓN 2: PORTAFOLIO INDIVIDUAL ---
elif seccion == "👤 Mi Portafolio":
    st.title("Tu Capital VIP")
    st.write("Monitoreo en tiempo real de tus posiciones.")
    
    precio_compra_spy = 505.50
    precio_actual_spy = obtener_precio_actual("SPY")
    ganancia_spy = ((precio_actual_spy - precio_compra_spy) / precio_compra_spy) * 100 if precio_compra_spy else 0
    
    precio_compra_ypf = 16.20
    precio_actual_ypf = obtener_precio_actual("YPF")
    ganancia_ypf = ((precio_actual_ypf - precio_compra_ypf) / precio_compra_ypf) * 100 if precio_compra_ypf else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="S&P 500 (SPY)", value=f"${precio_actual_spy}", delta=f"{round(ganancia_spy, 2)}%")
    with col2:
        st.metric(label="YPF (ADR)", value=f"${precio_actual_ypf}", delta=f"{round(ganancia_ypf, 2)}%")
        
    st.markdown("---")
    st.info("💡 **Análisis Estratégico:** Fase de acumulación detectada con bajo volumen. Sostenemos posiciones esperando el próximo impulso alcista.")

# --- SECCIÓN 3: PANEL LOCAL (RÍO GRANDE) ---
elif seccion == "📍 Panel Local":
    st.title("Centro de Información Local")
    st.subheader("☁️ Clima Actual en Río Grande")
    clima = obtener_clima_local()
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Temperatura", clima["temp"])
    col_c2.metric("Condición", clima["condicion"])
    col_c3.metric("Viento", clima["viento"])
    
    st.markdown("---")
    st.subheader("⛽ Red de Combustibles (Autosur)")
    datos_combustible = {
        "Zona": ["Río Grande", "Río Grande", "CABA (Promedio)", "CABA (Promedio)"],
        "Producto": ["Super", "Infinia", "Super", "Infinia"],
        "Precio x Litro": ["$661", "$839", "$980", "$1180"]
    }
    st.table(pd.DataFrame(datos_combustible))

# --- SECCIÓN 4: MERCADO GLOBAL ---
elif seccion == "🌍 Mercado Global":
    st.title("Pulso Económico 🌐")
    st.write("Las noticias que mueven los mercados mundiales hoy.")
    st.success("🇺🇸 **Wall Street:** Índices en verde tras un reporte de inflación menor al esperado.")
    st.warning("💶 **Europa:** El Banco Central Europeo evalúa recortar las tasas antes de fin de año.")
    st.info("⚡ **Materias Primas:** El oro alcanza nuevos máximos históricos ante la búsqueda de activos refugio.")
    st.markdown("---")
    st.write(f"*Información actualizada a las: {datetime.now().strftime('%H:%M')}*")

# Pie de página general
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 StarkRendimiento Management")
st.sidebar.caption("Tecnología financiera de vanguardia.")