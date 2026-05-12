import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import plotly.express as px

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="StarkRendimiento", page_icon="🦅", layout="centered")

# --- ESTILOS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'Helvetica Neue', sans-serif; }
    div[data-testid="metric-container"] {
        background-color: #161b22; border: 1px solid #30363d; padding: 15px;
        border-radius: 10px; border-left: 4px solid #D4AF37; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    [data-testid="stSidebar"] { background-color: #12151c; border-right: 1px solid #D4AF37; }
    .ad-banner { background-color: #1a1e24; border: 1px dashed #D4AF37; text-align: center;
        padding: 20px; border-radius: 8px; margin-bottom: 25px; margin-top: 10px; }
    .ad-title { color: #D4AF37; font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }
    .ad-text { color: #888; font-size: 0.9em; }
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

@st.cache_data(ttl=3600)
def obtener_noticias_financieras():
    try:
        spy = yf.Ticker("SPY")
        return spy.news[:5]
    except:
        return []

# --- BARRA DE NAVEGACIÓN LATERAL ---
st.sidebar.title("🦅 StarkRendimiento")
st.sidebar.markdown("---")
seccion = st.sidebar.radio("Navegación:", ["📊 Panel del Fondo", "👤 Fondo Público Stark", "📍 Panel Local", "🌍 Mercado Global"])

# --- ESPACIO PUBLICITARIO GLOBAL ---
st.markdown("""
    <div class="ad-banner">
        <div class="ad-title">ESPACIO PUBLICITARIO DISPONIBLE</div>
        <div class="ad-text">Destaca tu marca frente a inversores y profesionales.<br>Contáctanos para anunciar aquí.</div>
    </div>
""", unsafe_allow_html=True)

# --- SECCIÓN 1: PANEL GLOBAL (CON ORO Y BTC) ---
if seccion == "📊 Panel del Fondo":
    st.title("Transparencia y Gestión")
    st.write("Métricas globales del capital y commodities clave.")
    
    # Precios en vivo de commodities
    precio_btc = obtener_precio_actual("BTC-USD")
    precio_oro = obtener_precio_actual("GC=F") # Ticker del futuro del Oro
    
    col1, col2 = st.columns(2)
    col1.metric("Bitcoin (BTC)", f"${precio_btc:,.2f}")
    col2.metric("Oro (Onza)", f"${precio_oro:,.2f}")
    
    st.markdown("---")
    st.subheader("Distribución de Activos")
    datos_activos = pd.DataFrame({
        "Activo": ["S&P 500 (SPY)", "Bonos (AL30 / AO27)", "Energía (YPF)", "Bitcoin"],
        "Porcentaje": [40, 30, 15, 15]
    })
    
    fig_pie = px.pie(datos_activos, values='Porcentaje', names='Activo', hole=0.5, 
                     color_discrete_sequence=['#D4AF37', '#1f77b4', '#2ca02c', '#f7931a'])
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#e0e0e0'))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- SECCIÓN 2: SKIN IN THE GAME (EL DINERO REAL) ---
elif seccion == "👤 Fondo Público Stark":
    st.title("Capital Administrado 🦅")
    st.write("Transparencia total: Monitoreo en tiempo real de nuestras propias inversiones.")
    
    # === ACÁ PONÉS TUS PRECIOS DE COMPRA REALES ===
    compra_btc = 60000.00
    compra_spy = 505.50
    compra_ypf = 16.20
    compra_al30 = 55.00 # Ejemplo de cotización de bono
    
    # Precios actuales en vivo
    actual_btc = obtener_precio_actual("BTC-USD")
    actual_spy = obtener_precio_actual("SPY")
    actual_ypf = obtener_precio_actual("YPF")
    actual_al30 = obtener_precio_actual("AL30.BA") # Cotización en BCBA
    
    # Cálculo de rentabilidad
    def calc_ganancia(actual, compra):
        if compra > 0 and actual > 0:
            return ((actual - compra) / compra) * 100
        return 0.0

    st.subheader("Rendimiento del Portafolio Vivo")
    
    c1, c2 = st.columns(2)
    c1.metric(label="Bitcoin (BTC)", value=f"${actual_btc:,.2f}", delta=f"{calc_ganancia(actual_btc, compra_btc):.2f}%")
    c2.metric(label="S&P 500 (SPY)", value=f"${actual_spy:,.2f}", delta=f"{calc_ganancia(actual_spy, compra_spy):.2f}%")
    
    c3, c4 = st.columns(2)
    c3.metric(label="YPF (ADR)", value=f"${actual_ypf:,.2f}", delta=f"{calc_ganancia(actual_ypf, compra_ypf):.2f}%")
    c4.metric(label="Bono AL30", value=f"${actual_al30:,.2f}", delta=f"{calc_ganancia(actual_al30, compra_al30):.2f}%")
        
    st.markdown("---")
    st.success("💡 **Estrategia Stark:** Nuestra piel está en el juego. Operamos bajo el Método Wyckoff buscando zonas de acumulación institucional antes de abrir posiciones.")

# --- SECCIÓN 3: PANEL LOCAL ---
elif seccion == "📍 Panel Local":
    st.title("Centro de Información Local")
    st.subheader("☁️ Clima Actual en Río Grande")
    clima = obtener_clima_local()
    col_c1, col_c2, col_c3 = st.columns(3)
    col_c1.metric("Temperatura", clima["temp"])
    col_c2.metric("Condición", clima["condicion"])
    col_c3.metric("Viento", clima["viento"])
    
    st.markdown("---")
    st.subheader("⛽ Red de Combustibles")
    datos_combustible = {
        "Zona": ["Río Grande", "Río Grande", "Río Grande", "Río Grande"],
        "Producto": ["Super", "Infinia", "Infinia Diesel", "Diesel 500"],
        "Precio": ["$1666", "$1839", "$2021", "$1981"]
    }
    st.table(pd.DataFrame(datos_combustible))

# --- SECCIÓN 4: MERCADO GLOBAL ---
elif seccion == "🌍 Mercado Global":
    st.title("Pulso Económico 🌐")
    st.write("Titulares financieros en tiempo real (Fuente: Yahoo Finance).")
    st.markdown("---")
    noticias = obtener_noticias_financieras()
    if noticias:
        for noticia in noticias:
            st.subheader(noticia.get('title', 'Noticia sin título'))
            st.write(noticia.get('publisher', 'Agencia Financiera'))
            st.markdown(f"[Leer artículo completo]({noticia.get('link', '#')})")
            st.markdown("---")
    else:
        st.warning("Mercado cerrado o sin noticias recientes.")

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 StarkRendimiento Management")