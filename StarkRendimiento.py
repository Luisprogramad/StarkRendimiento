import io
import requests
import qrcode
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Pasarela de Cobro Cripto (USDT / USDC)",
    page_icon="💳",
    layout="centered"
)

# 1. Recuperar API Key desde st.secrets
API_KEY = st.secrets.get("NOWPAYMENTS_API_KEY", "")

def crear_factura_nowpayments(monto_usd: float, descripcion: str):
    """
    Genera una factura en NOWPayments.
    IMPORTANTE: Al omitir el parámetro 'pay_currency', NOWPayments despliega
    automáticamente la pantalla interactiva donde el cliente selecciona
    si desea pagar en USDT o USDC (y en qué red: Polygon, Arbitrum, BSC, etc.).
    """
    url = "https://api.nowpayments.io/v1/invoice"
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "price_amount": monto_usd,
        "price_currency": "usd",       # Moneda base en USD
        "order_description": descripcion
        # Se omite 'pay_currency' para no limitar al usuario a un solo token.
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        
        if response.status_code in [200, 201]:
            return data
        else:
            st.error(f"Error de la API: {data.get('message', 'No se pudo crear la factura')}")
            return None
    except Exception as e:
        st.error(f"Error de conexión con NOWPayments: {e}")
        return None

def generar_qr_bytes(url: str) -> bytes:
    """Genera la imagen PNG del código QR directamente en memoria."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- INTERFAZ STREAMLIT ---
st.title("💳 Pasarela de Cobro Cripto")
st.caption("Acepta pagos en USDT y USDC (Polygon, Arbitrum, TRC20, BSC)")

if not API_KEY:
    st.warning("⚠️ Falta configurar `NOWPAYMENTS_API_KEY` en `st.secrets`.")

st.subheader("Datos de la Transacción")

col1, col2 = st.columns([1, 2])
with col1:
    monto = st.number_input("Monto (USD)", min_value=1.0, value=10.0, step=1.0, format="%.2f")
with col2:
    concepto = st.text_input("Concepto / Detalle", value="Cobro de servicios StarkRendimiento")

if st.button("🚀 Generar Enlace y QR de Pago", use_container_width=True):
    if not API_KEY:
        st.error("Configura tu API Key en `.streamlit/secrets.toml` antes de continuar.")
    else:
        with st.spinner("Conectando con NOWPayments..."):
            factura = crear_factura_nowpayments(monto, concepto)
            
            if factura and "invoice_url" in factura:
                invoice_url = factura["invoice_url"]
                invoice_id = factura.get("id", "N/A")
                
                st.success("¡Cobro generado con éxito!")
                
                st.markdown(f"**ID Factura:** `{invoice_id}`")
                st.markdown(f"**Monto a pagar:** `${monto:.2f} USD`")
                
                # Generar imagen QR
                qr_png = generar_qr_bytes(invoice_url)
                
                st.write("---")
                st.subheader("Escanea para pagar")
                
                st.image(
                    qr_png, 
                    caption="Escanear con la cámara del celular o wallet cripto", 
                    width=250
                )
                
                st.link_button("🔗 Ir a la Pasarela de Pago", invoice_url, use_container_width=True)
                
                st.info(
                    "💡 **Instrucciones para el cliente:** Al abrir la pasarela, podrá seleccionar "
                    "si prefiere pagar en **USDT** o **USDC** y la red deseada (Polygon, Arbitrum, etc.)."
                )
