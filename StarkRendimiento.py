import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import os
import qrcode
from io import BytesIO

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config(page_title="StarkRendimiento", page_icon="🦅", layout="wide")

# --- VARIABLES DE ENTORNO Y PASARELA ---
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "")

# Configura aquí tus datos locales para cobros sin impuestos internacionales
MI_ALIAS_PESOS = "Luisfiwind12"  # Cambia por tu Alias CBU/CVU real
MI_WALLET_USDT = "0x0000000000000000000000000000000000000000"  # Tu wallet Polygon/TRC20

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

@st.cache_data(ttl=180)
def obtener_dolares_argentina():
    try:
        res = requests.get("https://dolarapi.com/v1/dolares", timeout=5)
        if res.status_code == 200:
            data = res.json()
            precios = {}
            for item in data:
                precios[item['casa']] = {
                    'compra': item.get('compra', 0),
                    'venta': item.get('venta', 0)
                }
            return precios
    except:
        pass
    return {}

@st.cache_data(ttl=600)
def obtener_panel_acciones():
    activos = [
        {"Ticker": "SPY", "Nombre": "S&P 500 ETF", "Tipo": "Global (USD)"},
        {"Ticker": "QQQ", "Nombre": "Nasdaq 100 ETF", "Tipo": "Global (USD)"},
        {"Ticker": "AAPL", "Nombre": "Apple Inc.", "Tipo": "Acción (USD)"},
        {"Ticker": "MSFT", "Nombre": "Microsoft", "Tipo": "Acción (USD)"},
        {"Ticker": "GGAL", "Nombre": "Grupo Galicia (ADR)", "Tipo": "Argentinas (USD)"},
        {"Ticker": "YPF", "Nombre": "YPF (ADR)", "Tipo": "Argentinas (USD)"},
        {"Ticker": "AL30.BA", "Nombre": "Bono AL30", "Tipo": "Renta Fija (ARS)"}
    ]
    
    resultados = []
    for activo in activos:
        precio = obtener_precio_actual(activo["Ticker"])
        resultados.append({
            "Activo": activo["Nombre"],
            "Ticker": activo["Ticker"],
            "Categoría": activo["Tipo"],
            "Precio": f"{precio:,.2f}"
        })
    return pd.DataFrame(resultados)

def generar_invoice_nowpayments(monto, moneda, api_key):
    url = "https://api.nowpayments.io/v1/invoice"
    payload = {
        "price_amount": float(monto),
        "price_currency": moneda,
        # AL OMITIR 'pay_currency', LA PASARELA MOSTRARÁ EL MENÚ PARA ELEGIR USDT O USDC
        "is_fee_paid_by_user": True,
        "order_description": "Cobro via StarkRendimiento"
    }
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            return response.json().get("invoice_url")
        else:
            st.error(f"Error API: {response.text}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
    return None

def generar_qr_imagen(texto_o_url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(texto_o_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- BARRA DE NAVEGACIÓN LATERAL ---
st.sidebar.title("🦅 StarkRendimiento")
st.sidebar.markdown("---")
seccion = st.sidebar.radio("Navegación:", [
    "🌍 Terminal de Mercado", 
    "📊 Portafolio Stark",
    "💳 Billetera y Cobros (Sin Impuestos)"
])

# --- SECCIÓN 1: TERMINAL DE MERCADO ---
if seccion == "🌍 Terminal de Mercado":
    st.title("Terminal Financiera Global y Local 🌐")
    
    # Cotizaciones Dólar Argentina
    st.subheader("🇦🇷 Cotizaciones Dólar (Tiempo Real)")
    dolares = obtener_dolares_argentina()
    
    if dolares:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Dólar Oficial", f"${dolares.get('oficial', {}).get('venta', 0):,.2f}")
        c2.metric("Dólar MEP", f"${dolares.get('bolsa', {}).get('venta', 0):,.2f}")
        c3.metric("Dólar Blue", f"${dolares.get('blue', {}).get('venta', 0):,.2f}")
        c4.metric("Dólar CCL", f"${dolares.get('contadoconliqui', {}).get('venta', 0):,.2f}")
        c5.metric("Dólar Cripto", f"${dolares.get('cripto', {}).get('venta', 0):,.2f}")
    else:
        st.warning("No se pudieron cargar las cotizaciones del dólar en este momento.")
        
    st.markdown("---")
    
    # Panel de Acciones tipo Yahoo
    st.subheader("📈 Monitor de Activos (Equities & ETFs)")
    df_acciones = obtener_panel_acciones()
    st.dataframe(df_acciones, use_container_width=True, hide_index=True)
    
    st.caption("💡 Los precios se actualizan con un retraso de 15 min según la fuente (Yahoo Finance).")

# --- SECCIÓN 2: PORTAFOLIO ---
elif seccion == "📊 Portafolio Stark":
    st.title("Capital Administrado 🦅")
    st.write("Monitoreo en tiempo real de nuestras inversiones.")
    
    compra_btc = 60000.00
    compra_spy = 505.50
    
    actual_btc = obtener_precio_actual("BTC-USD")
    actual_spy = obtener_precio_actual("SPY")
    
    def calc_ganancia(actual, compra):
        if compra > 0 and actual > 0:
            return ((actual - compra) / compra) * 100
        return 0.0
    
    c1, c2 = st.columns(2)
    c1.metric(label="Bitcoin (BTC)", value=f"${actual_btc:,.2f}", delta=f"{calc_ganancia(actual_btc, compra_btc):.2f}%")
    c2.metric(label="S&P 500 (SPY)", value=f"${actual_spy:,.2f}", delta=f"{calc_ganancia(actual_spy, compra_spy):.2f}%")

# --- SECCIÓN 3: BILLETERA Y COBROS ---
elif seccion == "💳 Billetera y Cobros (Sin Impuestos)":
    st.title("Gestor de Cobros y Billetera 💱")
    st.write("Calcula importes y genera métodos de cobro locales e internacionales de forma transparente.")
    
    dolares = obtener_dolares_argentina()
    precio_mep = dolares.get('bolsa', {}).get('venta', 1300)
    precio_cripto = dolares.get('cripto', {}).get('venta', 1300)
    precio_oficial = dolares.get('oficial', {}).get('venta', 1000)
    
    col_input, col_calc = st.columns([1, 1])
    
    with col_input:
        monto_ars = st.number_input("Monto a cobrar en Pesos (ARS)", min_value=1000.0, value=20000.0, step=1000.0)
        
    with col_calc:
        st.subheader("Equivalencias de Mercado")
        st.write(f"• **Al Dólar MEP (${precio_mep:,.2f}):** u$s {(monto_ars / precio_mep):.2f}")        
        st.write(f"• **Al Dólar Cripto (${precio_cripto:,.2f}):** {(monto_ars / precio_cripto):.2f} USDT")        
        st.write(f"• **Al Dólar Oficial (${precio_oficial:,.2f}):** u$s {(monto_ars / precio_oficial):.2f}")
    
    st.markdown("---")
    st.subheader("Selecciona el Método de Cobro")
    
    metodo = st.radio(
        "Opción de pago:", 
        [
            "🇦🇷 Transferencia CVU / Pesos (0% Impuesto Tarjeta)", 
            "⚡ Transferencia Cripto Directa / USDT (0% Impuesto Tarjeta)",
            "🌐 Pasarela NOWPayments (USDT / USDC)"
        ]
    )
    
    if "CVU / Pesos" in metodo:
        st.success("✅ **Opción 100% libre de impuesto al dólar internacional.**")
        st.markdown(f"""
        1. El cliente debe transferir **${monto_ars:,.2f} ARS**.
        2. **Alias CVU:** `{MI_ALIAS_PESOS}`
        3. Acepta transferencias desde Mercado Pago, Fiwind, Lemon, Belo o cualquier banco argentino.
        """)
        qr_bytes = generar_qr_imagen(MI_ALIAS_PESOS)
        st.image(qr_bytes, caption="Escanear Alias para transferir en ARS", width=250)
        
    elif "Cripto Directa" in metodo:
        st.success("✅ **Opción 100% libre de impuesto al dólar internacional.**")
        usdt_a_cobrar = round(monto_ars / precio_cripto, 2)
        st.markdown(f"""
        1. El cliente transfiere **{usdt_a_cobrar} USDT** (Red Polygon / TRC20).
        2. **Dirección Wallet:** `{MI_WALLET_USDT}`
        3. Directo desde Fiwind, Belo, Lemon Cash, Bitget o Binance sin comisiones bancarias.
        """)
        qr_bytes = generar_qr_imagen(MI_WALLET_USDT)
        st.image(qr_bytes, caption=f"Escanear para enviar {usdt_a_cobrar} USDT", width=250)
        
    elif "NOWPayments" in metodo:
        st.info("💡 **NUEVO:** Al abrir el enlace, el cliente podrá elegir pagar con **USDT** o **USDC** y seleccionar la red más económica (como Polygon).")
        st.warning("⚠️ *Nota: Si el cliente usa tarjeta de crédito en plataformas integradas, pueden aplicar recargos.*")
        
        if st.button("🚀 Crear Orden NOWPayments", type="primary"):
            if not NOWPAYMENTS_API_KEY:
                st.error("⚠️ Error: Falta la API Key en las variables de entorno.")
            else:
                with st.spinner("Generando enlace interactivo..."):
                    url_pago = generar_invoice_nowpayments(monto_ars, "ars", NOWPAYMENTS_API_KEY)
                    if url_pago:
                        qr_bytes = generar_qr_imagen(url_pago)
                        st.success(f"✅ Orden por ${monto_ars:,.2f} ARS creada.")
                        st.image(qr_bytes, caption="Escanear para elegir USDT / USDC y pagar", width=250)
                        st.markdown(f"🔗 [Abrir Pasarela de Pago]({url_pago})")

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 StarkRendimiento Management")
