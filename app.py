import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import smtplib
import html
import os
import re
import threading
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

DATA_FILE = Path(__file__).parent / "data" / "resultados.csv"
_DATA_LOCK = threading.Lock()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="FinPulse | Diagnóstico Financiero",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — compact, no wasted space
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    /* ── Global ── */
    .stApp {
        background: linear-gradient(145deg, #0a0a1a 0%, #1a1a3e 40%, #0d0d2b 100%);
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: #0d0d2b;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── Kill ALL Streamlit default spacing ── */
    #MainMenu, footer, header, .stDeployButton, [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 8px;
    }

    /* ── Logo ── */
    .finpulse-logo {
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #4ECDC4, #C77DFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Welcome — two-column hero ── */
    .welcome-hero {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 48px;
        padding: 16px 0;
        min-height: calc(100vh - 120px);
    }
    .welcome-left {
        flex: 1;
        max-width: 480px;
    }
    .welcome-right {
        flex: 1;
        max-width: 400px;
    }
    .welcome-emoji {
        font-size: 44px;
        animation: floater 3s ease-in-out infinite;
        margin-bottom: 10px;
    }
    @keyframes floater {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    .welcome-title {
        font-size: 34px;
        font-weight: 700;
        letter-spacing: -1.2px;
        line-height: 1.15;
        color: #E8E8F0;
        margin-bottom: 8px;
    }
    .welcome-gradient {
        background: linear-gradient(135deg, #4ECDC4, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .welcome-sub {
        color: rgba(255,255,255,0.82);
        font-size: 15px;
        line-height: 1.7;
        margin-bottom: 20px;
    }
    .welcome-sections {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 20px;
    }
    .welcome-section-item {
        text-align: center;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: 10px 14px;
        flex: 1;
        min-width: 80px;
        transition: transform 0.2s, background 0.2s;
    }
    .welcome-section-item:hover {
        background: rgba(255,255,255,0.13);
        transform: translateY(-2px);
    }
    .welcome-section-item .ws-icon { font-size: 26px; display: block; }
    .welcome-section-item .ws-label { font-size: 10px; color: rgba(255,255,255,0.85); margin-top: 6px; display: block; font-weight: 500; line-height: 1.3; }
    .form-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 28px 24px;
    }
    .form-title {
        font-size: 16px;
        font-weight: 600;
        color: #E8E8F0;
        margin-bottom: 4px;
    }
    .form-sub {
        font-size: 13px;
        color: rgba(255,255,255,0.75);
        margin-bottom: 16px;
    }

    /* ── Section Badge ── */
    .section-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 6px 14px;
        border-radius: 10px;
        margin-bottom: 16px;
    }
    .section-icon { font-size: 24px; }
    .section-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* ── Question ── */
    .question-text {
        font-size: 20px;
        font-weight: 600;
        color: #E8E8F0;
        line-height: 1.4;
        letter-spacing: -0.3px;
        margin-bottom: 20px;
    }

    /* ── Progress dots ── */
    .progress-dots {
        display: flex;
        justify-content: center;
        gap: 4px;
        margin-top: 24px;
        flex-wrap: wrap;
    }
    .dot {
        width: 6px;
        height: 6px;
        border-radius: 3px;
        background: rgba(255,255,255,0.1);
        transition: all 0.3s;
    }
    .dot-active {
        width: 18px;
        background: var(--dot-color, #4ECDC4);
    }
    .dot-done {
        background: var(--dot-color, #4ECDC4);
        opacity: 0.5;
    }

    /* ── Results ── */
    .result-hero {
        text-align: center;
        padding: 20px;
        margin-bottom: 24px;
    }
    .result-emoji {
        font-size: 52px;
        animation: floater 3s ease-in-out infinite;
        margin-bottom: 8px;
    }
    .grade-badge {
        display: inline-block;
        padding: 3px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }
    .result-name {
        font-size: 26px;
        font-weight: 700;
        color: #E8E8F0;
        letter-spacing: -1px;
        margin-bottom: 2px;
    }
    .result-profile {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .result-summary {
        color: rgba(255,255,255,0.8);
        font-size: 13px;
        max-width: 500px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* ── Metric Card ── */
    .metric-card {
        padding: 14px 18px;
        border-radius: 12px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #E8E8F0;
    }
    .metric-value {
        font-size: 13px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
    }
    .metric-bar {
        height: 8px;
        border-radius: 4px;
        background: rgba(255,255,255,0.06);
        margin-top: 6px;
        overflow: hidden;
    }
    .metric-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 1s ease;
    }

    /* ── Tags ── */
    .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    .tag {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 500;
    }

    /* ── Insights ── */
    .insight-card {
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .insight-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .insight-item {
        font-size: 13px;
        color: rgba(255,255,255,0.82);
        line-height: 1.5;
        margin-bottom: 3px;
    }

    /* ── Archetype ── */
    .archetype-card {
        display: flex;
        gap: 20px;
        align-items: center;
        padding: 20px 24px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    .archetype-emoji { font-size: 56px; line-height: 1; }
    .archetype-kicker {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: rgba(255,255,255,0.6);
    }
    .archetype-name { font-size: 24px; font-weight: 700; letter-spacing: -0.5px; margin: 2px 0 6px; }
    .archetype-desc { font-size: 14px; color: rgba(255,255,255,0.85); line-height: 1.55; }
    .archetype-slogan { font-size: 13px; font-style: italic; margin-top: 8px; }

    /* ── Bias & campaign cards ── */
    .bias-card, .campaign-card {
        padding: 16px 18px;
        border-radius: 12px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 10px;
        height: 100%;
    }
    .bias-name { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
    .bias-row { font-size: 13px; color: rgba(255,255,255,0.82); line-height: 1.5; margin-bottom: 6px; }
    .bias-row b { color: #E8E8F0; }
    .campaign-head { font-size: 15px; font-weight: 700; margin-bottom: 8px; }
    .campaign-kpi {
        display: inline-block;
        font-family: 'Space Mono', monospace !important;
        font-size: 11px;
        padding: 3px 10px;
        border-radius: 8px;
        background: rgba(255,217,61,0.12);
        color: #FFD93D;
        margin-bottom: 8px;
    }
    .lab-result {
        padding: 14px 18px;
        border-radius: 12px;
        background: rgba(78,205,196,0.08);
        border: 1px solid rgba(78,205,196,0.25);
        font-size: 14px;
        color: rgba(255,255,255,0.88);
        line-height: 1.6;
    }
    .lab-result b { color: #4ECDC4; }

    /* ── Admin ── */
    .admin-row {
        display: grid;
        grid-template-columns: 2fr 2fr 1fr 1fr 1.5fr;
        padding: 10px 14px;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 6px;
        font-size: 12px;
        align-items: center;
    }
    .admin-header {
        display: grid;
        grid-template-columns: 2fr 2fr 1fr 1fr 1.5fr;
        padding: 6px 14px;
        font-size: 10px;
        font-weight: 600;
        color: rgba(255,255,255,0.35);
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 6px;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        padding: 16px;
        border-radius: 12px;
        background: rgba(78,205,196,0.06);
        border: 1px solid rgba(78,205,196,0.12);
        margin-top: 16px;
    }
    .stat-item { text-align: center; }
    .stat-value {
        font-size: 24px;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
    }
    .stat-label {
        font-size: 10px;
        color: rgba(255,255,255,0.4);
        margin-top: 2px;
    }

    /* ── Streamlit input overrides ── */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.2s;
    }
    .stButton > button:hover,
    .stButton > button:hover p,
    .stButton > button:hover span,
    .stButton > button:focus,
    .stButton > button:active,
    .stButton > button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover p,
    .stButton > button[kind="primary"]:hover span,
    .stButton > button[kind="primary"]:focus,
    .stButton > button[kind="primary"]:active {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .stTextInput > div > div > input,
    .stTextInput input,
    input[type="text"],
    input[type="email"],
    input[type="password"],
    [data-testid="stTextInput"] input {
        font-family: 'DM Sans', sans-serif !important;
        background: rgba(255,255,255,0.92) !important;
        border: 1px solid rgba(78,205,196,0.5) !important;
        border-radius: 10px !important;
        color: #111111 !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        caret-color: #0a6b65 !important;
        -webkit-text-fill-color: #111111 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextInput input:focus,
    [data-testid="stTextInput"] input:focus,
    .stTextInput > div > div > input:active,
    .stTextInput input:active,
    input[type="email"]:focus,
    input[type="email"]:active {
        border-color: rgba(78,205,196,0.9) !important;
        box-shadow: 0 0 0 2px rgba(78,205,196,0.3) !important;
        background: #ffffff !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextInput input::placeholder,
    [data-testid="stTextInput"] input::placeholder {
        color: rgba(0,0,0,0.4) !important;
        -webkit-text-fill-color: rgba(0,0,0,0.4) !important;
    }
    .stTextInput label,
    [data-testid="stTextInput"] label {
        color: rgba(255,255,255,0.5) !important;
        font-size: 12px !important;
    }
    .js-plotly-plot .plotly .bg { fill: transparent !important; }

    /* ── Email section ── */
    .email-section {
        padding: 20px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(78,205,196,0.08), rgba(199,125,255,0.08));
        border: 1px solid rgba(78,205,196,0.2);
        text-align: center;
        margin-top: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA: SURVEY SECTIONS
# ──────────────────────────────────────────────
SECTIONS = [
    {
        "id": "gastos",
        "title": "Hábitos de Gasto",
        "icon": "💸",
        "color": "#FF6B6B",
        "questions": [
            {
                "id": "g1",
                "text": "Cuando recibes tu ingreso mensual, ¿qué es lo primero que haces?",
                "options": [
                    {"text": "Pago mis obligaciones fijas y ahorro antes de gastar", "score": 5, "tag": "disciplinado"},
                    {"text": "Pago lo urgente y voy gastando según surjan necesidades", "score": 3, "tag": "reactivo"},
                    {"text": "Me doy un gusto primero, lo merezco por trabajar duro", "score": 1, "tag": "impulsivo"},
                    {"text": "Honestamente, no tengo un orden específico", "score": 2, "tag": "desorganizado"},
                ],
            },
            {
                "id": "g2",
                "text": "¿Con qué frecuencia compras algo que NO tenías planeado comprar?",
                "options": [
                    {"text": "Casi nunca, soy muy estricto con mis compras", "score": 5, "tag": "controlado"},
                    {"text": "Ocasionalmente, pero solo cosas pequeñas", "score": 4, "tag": "moderado"},
                    {"text": "Frecuentemente, las ofertas me atrapan", "score": 2, "tag": "tentado"},
                    {"text": "Muy seguido, comprar me hace sentir bien", "score": 1, "tag": "compulsivo"},
                ],
            },
            {
                "id": "g3",
                "text": "¿Cómo clasificarías tus suscripciones digitales (streaming, apps, etc.)?",
                "options": [
                    {"text": "Solo tengo las que realmente uso y reviso periódicamente", "score": 5, "tag": "eficiente"},
                    {"text": "Tengo varias pero las uso todas", "score": 4, "tag": "consciente"},
                    {"text": "Tengo algunas que ni recuerdo que pago", "score": 2, "tag": "descuidado"},
                    {"text": "Ni sé exactamente cuántas tengo ni cuánto pago", "score": 1, "tag": "inconsciente"},
                ],
            },
            {
                "id": "g4",
                "text": "Cuando sales con amigos, ¿cómo manejas los gastos sociales?",
                "options": [
                    {"text": "Tengo un presupuesto mensual destinado a ocio", "score": 5, "tag": "planificador"},
                    {"text": "Intento no excederme pero no llevo un control estricto", "score": 3, "tag": "flexible"},
                    {"text": "Gasto lo que sea necesario para no quedar mal", "score": 1, "tag": "presión social"},
                    {"text": "Alterno entre salir mucho y luego restringirme", "score": 2, "tag": "irregular"},
                ],
            },
        ],
    },
    {
        "id": "ahorro",
        "title": "Cultura de Ahorro",
        "icon": "🏦",
        "color": "#4ECDC4",
        "questions": [
            {
                "id": "a1",
                "text": "¿Qué porcentaje de tus ingresos destinas al ahorro?",
                "options": [
                    {"text": "Más del 20%", "score": 5, "tag": "ahorrador élite"},
                    {"text": "Entre 10% y 20%", "score": 4, "tag": "buen ahorrador"},
                    {"text": "Menos del 10%", "score": 2, "tag": "ahorrador básico"},
                    {"text": "No logro ahorrar consistentemente", "score": 1, "tag": "sin ahorro"},
                ],
            },
            {
                "id": "a2",
                "text": "¿Tienes un fondo de emergencia que cubra al menos 3 meses de gastos?",
                "options": [
                    {"text": "Sí, tengo más de 6 meses cubiertos", "score": 5, "tag": "blindado"},
                    {"text": "Sí, entre 3 y 6 meses", "score": 4, "tag": "protegido"},
                    {"text": "Tengo algo, pero no llega a 3 meses", "score": 2, "tag": "vulnerable"},
                    {"text": "No tengo fondo de emergencia", "score": 1, "tag": "expuesto"},
                ],
            },
            {
                "id": "a3",
                "text": "¿Cuál es tu principal motivación para ahorrar?",
                "options": [
                    {"text": "Construir patrimonio y libertad financiera a largo plazo", "score": 5, "tag": "visionario"},
                    {"text": "Tener un colchón para imprevistos", "score": 4, "tag": "previsor"},
                    {"text": "Comprar algo específico que quiero", "score": 3, "tag": "orientado a metas"},
                    {"text": "Realmente no tengo una motivación clara", "score": 1, "tag": "sin dirección"},
                ],
            },
            {
                "id": "a4",
                "text": "¿Utilizas alguna herramienta o método para ahorrar?",
                "options": [
                    {"text": "Sí, automatizo transferencias a cuentas de ahorro/inversión", "score": 5, "tag": "sistematizado"},
                    {"text": "Uso apps de finanzas personales para hacer seguimiento", "score": 4, "tag": "tecnológico"},
                    {"text": "Lo hago manualmente cuando me acuerdo", "score": 2, "tag": "informal"},
                    {"text": "No uso ningún método específico", "score": 1, "tag": "improvisado"},
                ],
            },
        ],
    },
    {
        "id": "inversiones",
        "title": "Mundo de las Inversiones",
        "icon": "📈",
        "color": "#FFD93D",
        "questions": [
            {
                "id": "i1",
                "text": "¿Cuál es tu experiencia con instrumentos de inversión?",
                "options": [
                    {"text": "Invierto activamente en varios instrumentos (acciones, fondos, crypto, etc.)", "score": 5, "tag": "inversionista activo"},
                    {"text": "Tengo inversiones básicas como CDTs o fondos de inversión", "score": 4, "tag": "inversionista conservador"},
                    {"text": "He investigado pero aún no me animo a invertir", "score": 2, "tag": "explorador"},
                    {"text": "No sé por dónde empezar a invertir", "score": 1, "tag": "novato"},
                ],
            },
            {
                "id": "i2",
                "text": "¿Qué harías si recibieras un ingreso extra inesperado de $5.000.000 COP?",
                "options": [
                    {"text": "Invertiría al menos el 70% en instrumentos financieros", "score": 5, "tag": "mentalidad inversora"},
                    {"text": "Ahorraría una parte e invertiría otra", "score": 4, "tag": "equilibrado"},
                    {"text": "Lo guardaría todo en mi cuenta de ahorros", "score": 3, "tag": "conservador"},
                    {"text": "Aprovecharía para comprar cosas que necesito o quiero", "score": 1, "tag": "consumista"},
                ],
            },
            {
                "id": "i3",
                "text": "¿Conoces la diferencia entre renta fija y renta variable?",
                "options": [
                    {"text": "Sí, y tengo posiciones en ambos tipos", "score": 5, "tag": "conocedor"},
                    {"text": "Sí, la conozco teóricamente", "score": 3, "tag": "teórico"},
                    {"text": "He escuchado los términos pero no estoy seguro", "score": 2, "tag": "aprendiz"},
                    {"text": "No, no conozco la diferencia", "score": 1, "tag": "desinformado"},
                ],
            },
            {
                "id": "i4",
                "text": "¿Cómo reaccionarías si una inversión tuya pierde 20% de su valor en una semana?",
                "options": [
                    {"text": "Analizo si los fundamentales cambiaron; si no, mantengo o compro más", "score": 5, "tag": "racional"},
                    {"text": "Espero a que se recupere sin hacer nada", "score": 3, "tag": "pasivo"},
                    {"text": "Me asusto pero intento no vender", "score": 2, "tag": "nervioso"},
                    {"text": "Vendería inmediatamente para no perder más", "score": 1, "tag": "pánico"},
                ],
            },
        ],
    },
    {
        "id": "deuda",
        "title": "Gestión de Deuda",
        "icon": "⚖️",
        "color": "#C77DFF",
        "questions": [
            {
                "id": "d1",
                "text": "¿Cuál es tu relación actual con las tarjetas de crédito?",
                "options": [
                    {"text": "Las uso estratégicamente y pago el total cada mes", "score": 5, "tag": "estratega"},
                    {"text": "Las uso moderadamente, a veces difiero compras", "score": 3, "tag": "moderado"},
                    {"text": "Tengo saldo pendiente que pago en mínimos", "score": 1, "tag": "endeudado"},
                    {"text": "No tengo tarjeta de crédito", "score": 3, "tag": "sin crédito"},
                ],
            },
            {
                "id": "d2",
                "text": "¿Sabes exactamente cuánto debes en total (créditos, tarjetas, préstamos)?",
                "options": [
                    {"text": "Sí, al centavo, y tengo plan de pago", "score": 5, "tag": "controlador"},
                    {"text": "Tengo una idea general pero no exacta", "score": 3, "tag": "aproximado"},
                    {"text": "Prefiero no pensar en eso", "score": 1, "tag": "evasivo"},
                    {"text": "No tengo deudas actualmente", "score": 5, "tag": "libre de deuda"},
                ],
            },
            {
                "id": "d3",
                "text": "¿Cómo evalúas antes de tomar un crédito o préstamo?",
                "options": [
                    {"text": "Analizo tasa de interés, plazo, costo total y mi capacidad de pago", "score": 5, "tag": "analítico"},
                    {"text": "Comparo opciones y elijo la cuota más cómoda", "score": 3, "tag": "práctico"},
                    {"text": "Si me lo aprueban, asumo que puedo pagarlo", "score": 1, "tag": "confiado"},
                    {"text": "Nunca he tomado un crédito formal", "score": 3, "tag": "sin historial"},
                ],
            },
        ],
    },
    {
        "id": "planificacion",
        "title": "Visión Financiera",
        "icon": "🎯",
        "color": "#6BCB77",
        "questions": [
            {
                "id": "p1",
                "text": "¿Tienes metas financieras definidas con plazos específicos?",
                "options": [
                    {"text": "Sí, tengo metas a corto, mediano y largo plazo documentadas", "score": 5, "tag": "planificador"},
                    {"text": "Tengo ideas generales de lo que quiero lograr", "score": 3, "tag": "aspirante"},
                    {"text": "Solo pienso en llegar bien a fin de mes", "score": 1, "tag": "superviviente"},
                    {"text": "No he pensado en metas financieras concretas", "score": 1, "tag": "sin rumbo"},
                ],
            },
            {
                "id": "p2",
                "text": "¿Con qué frecuencia revisas tu situación financiera (ingresos, gastos, patrimonio)?",
                "options": [
                    {"text": "Semanalmente, es parte de mi rutina", "score": 5, "tag": "disciplinado"},
                    {"text": "Mensualmente, cuando llegan los extractos", "score": 4, "tag": "regular"},
                    {"text": "Solo cuando siento que algo anda mal", "score": 2, "tag": "reactivo"},
                    {"text": "Casi nunca, prefiero no mirar", "score": 1, "tag": "evitativo"},
                ],
            },
            {
                "id": "p3",
                "text": "¿Cómo te educas en temas financieros?",
                "options": [
                    {"text": "Leo libros, tomo cursos y sigo expertos del tema activamente", "score": 5, "tag": "estudiante activo"},
                    {"text": "Veo contenido en redes sociales sobre finanzas", "score": 3, "tag": "consumidor casual"},
                    {"text": "Solo aprendo cuando tengo un problema financiero", "score": 2, "tag": "reactivo"},
                    {"text": "No invierto tiempo en educación financiera", "score": 1, "tag": "desconectado"},
                ],
            },
            {
                "id": "p4",
                "text": "¿Tienes algún tipo de seguro (vida, salud complementario, auto, hogar)?",
                "options": [
                    {"text": "Sí, tengo varios seguros como parte de mi planificación", "score": 5, "tag": "protegido"},
                    {"text": "Solo los obligatorios (EPS, SOAT)", "score": 3, "tag": "básico"},
                    {"text": "No, creo que no los necesito aún", "score": 1, "tag": "descubierto"},
                    {"text": "No he investigado opciones de seguros", "score": 1, "tag": "desinformado"},
                ],
            },
        ],
    },
    {
        "id": "consumidor",
        "title": "Consumidor vs. Marketer",
        "icon": "🧠",
        "color": "#FF9F1C",
        "questions": [
            {
                "id": "c1",
                "text": "Ves unos audífonos con el precio tachado: <s>$350.000</s> → HOY $199.900. ¿Qué haces?",
                "options": [
                    {"text": "Busco el precio en otras tiendas: el precio tachado no me dice nada", "score": 5, "tag": "comparador"},
                    {"text": "Me parece buena oferta, pero solo compro si ya los necesitaba", "score": 4, "tag": "selectivo"},
                    {"text": "Los guardo en el carrito y vuelvo cuando me llegue el recordatorio", "score": 2, "tag": "retargeteado", "bias": "anclaje"},
                    {"text": "¡Me ahorro $150.000! Los compro antes de que suba", "score": 1, "tag": "anclado", "bias": "anclaje"},
                ],
            },
            {
                "id": "c2",
                "text": "Un sitio te muestra: «Solo quedan 2 unidades · 14 personas están viendo esto». ¿Cómo reaccionas?",
                "options": [
                    {"text": "Lo reconozco como táctica de escasez y decido con calma", "score": 5, "tag": "inmune al FOMO"},
                    {"text": "Me genera algo de presión, pero me doy unas horas para pensarlo", "score": 4, "tag": "pausado"},
                    {"text": "Lo compro rápido; no quiero quedarme sin él", "score": 1, "tag": "FOMO", "bias": "escasez"},
                    {"text": "Depende: si es algo que me encanta, caigo", "score": 2, "tag": "emocional", "bias": "escasez"},
                ],
            },
            {
                "id": "c3",
                "text": "En el checkout aparece: «Llévalo hoy y págalo en 4 cuotas». ¿Qué piensas?",
                "options": [
                    {"text": "Calculo el costo total y reviso si hay intereses o comisiones ocultas", "score": 5, "tag": "calculador"},
                    {"text": "Solo lo uso si es 0% real y la cuota cabe en mi presupuesto", "score": 4, "tag": "prudente"},
                    {"text": "Me animo a comprar algo más caro porque la cuota se ve pequeña", "score": 1, "tag": "cuotificado", "bias": "cuotas"},
                    {"text": "Uso cuotas seguido y a veces pierdo la cuenta de cuánto debo", "score": 1, "tag": "sobre-diferido", "bias": "cuotas"},
                ],
            },
            {
                "id": "c4",
                "text": "Un creador de contenido que sigues recomienda un producto con su código de descuento. ¿Qué haces?",
                "options": [
                    {"text": "Sé que es contenido pagado; investigo reseñas independientes", "score": 5, "tag": "crítico"},
                    {"text": "Me genera interés, pero lo comparo con otras opciones", "score": 4, "tag": "analítico"},
                    {"text": "Si él lo usa, confío y lo compro con el código", "score": 2, "tag": "influenciable", "bias": "prueba_social"},
                    {"text": "Ya he comprado varias cosas así y algunas casi no las uso", "score": 1, "tag": "seguidor", "bias": "prueba_social"},
                ],
            },
            {
                "id": "c5",
                "text": "Te ofrecen 30 días gratis de una app premium, pero piden tu tarjeta. ¿Qué haces?",
                "options": [
                    {"text": "Activo la prueba y pongo un recordatorio para cancelar antes del cobro", "score": 5, "tag": "estratégico"},
                    {"text": "Solo la activo si estoy dispuesto a pagarla después", "score": 4, "tag": "intencional"},
                    {"text": "La activo y casi siempre se me olvida cancelar", "score": 1, "tag": "inercia", "bias": "default"},
                    {"text": "Nunca reviso qué se me cobra automáticamente", "score": 1, "tag": "piloto automático", "bias": "default"},
                ],
            },
        ],
    },
]

# Marketing tactics the student both designs (as a marketer) and falls for (as a consumer)
BIASES = {
    "anclaje": {
        "name": "⚓ Efecto ancla",
        "como": "El primer número que ves (el precio tachado) se vuelve tu referencia, aunque sea inventado.",
        "marketer": "Mostrar un precio 'antes' alto o un plan premium carísimo para que el intermedio parezca barato.",
        "antidoto": "Pregúntate: ¿pagaría $199.900 si nunca hubiera visto los $350.000? Compara en 2 fuentes.",
    },
    "escasez": {
        "name": "⏳ Escasez y FOMO",
        "como": "Lo escaso se percibe más valioso y la urgencia apaga el pensamiento analítico.",
        "marketer": "Contadores de tiempo, 'últimas unidades', 'X personas viendo esto', drops limitados.",
        "antidoto": "Regla de las 24 horas: si mañana sigue pareciéndote buena idea, cómpralo.",
    },
    "cuotas": {
        "name": "🧩 Ilusión de la cuota",
        "como": "Dividir el precio reduce el 'dolor de pagar': evalúas la cuota, no el costo total.",
        "marketer": "Comunicar el precio por día o por cuota ('menos que un café al día').",
        "antidoto": "Multiplica siempre: cuota × número de cuotas + intereses = precio real. Usa el simulador de abajo.",
    },
    "prueba_social": {
        "name": "📱 Prueba social y autoridad",
        "como": "Confiamos en lo que hacen personas que admiramos o que se parecen a nosotros.",
        "marketer": "Marketing de influencers, reseñas destacadas, 'el más vendido', testimonios.",
        "antidoto": "Busca reseñas de personas sin código de descuento y pregúntate si lo querías antes de verlo.",
    },
    "default": {
        "name": "🔁 Poder del default (inercia)",
        "como": "Tendemos a dejar las cosas como están: cancelar requiere un esfuerzo que posponemos.",
        "marketer": "Pruebas gratis con renovación automática, casillas pre-marcadas, suscripciones por defecto.",
        "antidoto": "Revisa tu extracto cada mes y usa el mismo poder a tu favor: automatiza tu ahorro.",
    },
}

# Brand archetypes (Mark & Pearson) applied to the student's financial behaviour
ARCHETYPES = {
    "gobernante": {
        "name": "El Gobernante", "emoji": "👑", "color": "#10B981",
        "desc": "Tu marca financiera transmite control, orden y visión de legado. Tomas decisiones con datos y piensas a largo plazo.",
        "slogan": "«El dinero trabaja para mí, no al revés.»",
        "riesgo": "El exceso de control puede hacerte perder oportunidades; revisa si estás demasiado conservador.",
    },
    "sabio": {
        "name": "El Sabio", "emoji": "🦉", "color": "#3B82F6",
        "desc": "Tu fortaleza es la planeación y el conocimiento. Antes de actuar, entiendes; tu propuesta de valor es la claridad.",
        "slogan": "«Primero entiendo, luego decido.»",
        "riesgo": "Analizar demasiado puede convertirse en parálisis: pasa del plan a la ejecución.",
    },
    "explorador": {
        "name": "El Explorador", "emoji": "🧭", "color": "#FFD93D",
        "desc": "Te atrae descubrir nuevas oportunidades de inversión y no le temes al riesgo calculado.",
        "slogan": "«Mi dinero también viaja y busca nuevos destinos.»",
        "riesgo": "La curiosidad sin fondo de emergencia es peligrosa: asegura la base antes de explorar.",
    },
    "cuidador": {
        "name": "El Cuidador", "emoji": "🛡️", "color": "#4ECDC4",
        "desc": "Proteger es tu instinto: ahorras, evitas deudas innecesarias y piensas en los imprevistos.",
        "slogan": "«Primero la tranquilidad, después todo lo demás.»",
        "riesgo": "Proteger no es lo mismo que crecer: tu ahorro puede estar perdiendo contra la inflación.",
    },
    "heroe": {
        "name": "El Héroe", "emoji": "🦸", "color": "#FF9F1C",
        "desc": "Tu disciplina frente a la tentación es tu superpoder: resistes promociones, impulsos y presión social.",
        "slogan": "«Ninguna oferta decide por mí.»",
        "riesgo": "Controlar el gasto es la mitad del camino; la otra mitad es poner ese dinero a crecer.",
    },
    "amante": {
        "name": "El Amante", "emoji": "❤️‍🔥", "color": "#FF6B6B",
        "desc": "Vives el presente y valoras las experiencias. Eres el target soñado de cualquier campaña emocional.",
        "slogan": "«Solo se vive una vez» — y la tarjeta lo sabe.",
        "riesgo": "Tu yo del futuro también es tu cliente: dale un presupuesto para disfrutar sin culpa y sin deuda.",
    },
    "inocente": {
        "name": "El Inocente", "emoji": "🌱", "color": "#C77DFF",
        "desc": "Confías en que las cosas saldrán bien y prefieres no complicarte con números. Esa calma es valiosa, pero arriesgada.",
        "slogan": "«Ya veremos cómo se resuelve.»",
        "riesgo": "El optimismo no reemplaza un plan: empieza por conocer cuánto entra, cuánto sale y cuánto debes.",
    },
}

# 30-day "campaign" templates for the weakest areas, written like a marketing brief
CAMPAIGNS = {
    "gastos": {
        "objetivo": "Reducir 15% los gastos no planeados en los próximos 30 días",
        "kpi": "KPI: % de compras no planeadas (meta < 10%)",
        "tacticas": ["Regla de las 48 horas para compras mayores a $100.000",
                     "Desactiva las notificaciones push de apps de compras y domicilios",
                     "Registra cada gasto el mismo día (app o nota del celular)"],
        "insight": "Mapea tu propio customer journey de gasto: ¿en qué touchpoints te 'convierten' más?",
    },
    "ahorro": {
        "objetivo": "Automatizar un ahorro del 10% de tu ingreso",
        "kpi": "KPI: tasa de ahorro mensual (ahorro ÷ ingreso)",
        "tacticas": ["Programa una transferencia automática el mismo día que recibes el pago",
                     "Abre una cuenta separada solo para tu fondo de emergencia",
                     "Meta inicial: 1 mes de gastos; luego escala a 3"],
        "insight": "El default es el nudge más poderoso: haz que ahorrar sea la opción por defecto.",
    },
    "inversiones": {
        "objetivo": "Dar tu primer paso de inversión con un monto que no te duela",
        "kpi": "KPI: # de instrumentos que puedes explicar (rentabilidad, riesgo, liquidez)",
        "tacticas": ["Aprende la diferencia entre CDT, fondo de inversión colectiva y acciones",
                     "Verifica que la entidad esté vigilada por la Superintendencia Financiera",
                     "Define el horizonte: ¿cuándo vas a necesitar ese dinero?"],
        "insight": "Haz investigación de mercado antes de 'comprar' una inversión, como evaluarías a un proveedor.",
    },
    "deuda": {
        "objetivo": "Mapear el 100% de tus deudas y su costo real",
        "kpi": "KPI: tasa EA promedio de tu deuda y meses para salir de ella",
        "tacticas": ["Lista cada deuda con saldo, tasa EA, cuota y plazo",
                     "Paga primero la de mayor tasa (avalancha) o la más pequeña (bola de nieve)",
                     "Compra a 1 cuota con tarjeta, salvo que el 0% de interés sea real"],
        "insight": "La cuota es el precio psicológico; el costo total es el precio real. No caigas en tu propio pricing.",
    },
    "planificacion": {
        "objetivo": "Escribir 3 metas financieras SMART con monto y fecha",
        "kpi": "KPI: % de avance mensual hacia cada meta",
        "tacticas": ["Una meta a 1 año, una a 3 años y una a 10 años",
                     "Agenda contigo una 'reunión de resultados' mensual de 30 minutos",
                     "Revisa tu protección básica: salud, vida o incapacidad"],
        "insight": "Trata tus finanzas como un plan de marketing anual: objetivos, presupuesto, KPIs y revisión.",
    },
    "consumidor": {
        "objetivo": "Detectar y neutralizar 3 tácticas de persuasión esta semana",
        "kpi": "KPI: # de compras evitadas por identificar una táctica",
        "tacticas": ["Antes de pagar, pregúntate: ¿qué táctica me están aplicando?",
                     "Compara el precio en al menos 2 fuentes e ignora el precio tachado",
                     "Deja de seguir cuentas que solo te venden"],
        "insight": "Tú diseñas estas estrategias: aplica tu ojo crítico de marketer cuando el target eres tú.",
    },
}

PROFILES = [
    {
        "min": 85, "max": 100, "name": "Maestro Financiero", "emoji": "🏆", "grade": "A+",
        "color": "#10B981",
        "summary": "Tienes un dominio excepcional de tus finanzas personales. Eres disciplinado, informado y estratégico.",
        "strengths": ["Excelente disciplina de gasto", "Cultura de ahorro sólida", "Visión de largo plazo clara"],
        "improvements": ["Diversifica aún más tus inversiones", "Considera asesoría para optimización fiscal", "Comparte tu conocimiento con otros"],
        "book": "📖 'El inversor inteligente' de Benjamin Graham",
    },
    {
        "min": 70, "max": 84, "name": "Estratega Financiero", "emoji": "⭐", "grade": "A",
        "color": "#3B82F6",
        "summary": "Tienes buenos hábitos financieros y conocimiento sólido. Con algunos ajustes llegarás al siguiente nivel.",
        "strengths": ["Buenos hábitos de ahorro", "Consciencia financiera", "Gestión responsable del crédito"],
        "improvements": ["Automatiza más tus procesos financieros", "Explora inversiones de mayor rendimiento", "Establece metas con plazos concretos"],
        "book": "📖 'Padre Rico, Padre Pobre' de Robert Kiyosaki",
    },
    {
        "min": 55, "max": 69, "name": "Aprendiz Financiero", "emoji": "📘", "grade": "B",
        "color": "#F59E0B",
        "summary": "Tienes fundamentos pero hay oportunidades significativas de mejora. Estás en el camino correcto.",
        "strengths": ["Consciencia de la importancia del ahorro", "Disposición para mejorar", "Algunos hábitos positivos"],
        "improvements": ["Crea un presupuesto mensual detallado", "Construye un fondo de emergencia de 3 meses", "Comienza a invertir con montos pequeños", "Edúcate activamente en finanzas personales"],
        "book": "📖 'El hombre más rico de Babilonia' de George S. Clason",
    },
    {
        "min": 35, "max": 54, "name": "En Zona de Riesgo", "emoji": "⚠️", "grade": "C",
        "color": "#EF4444",
        "summary": "Tus hábitos financieros necesitan atención urgente. Reconocerlo es el primer paso para transformar tu realidad.",
        "strengths": ["Has dado el primer paso al evaluar tu situación", "Tienes potencial de mejora significativo"],
        "improvements": ["URGENTE: Inventario completo de deudas", "Elimina gastos innecesarios", "Empieza a ahorrar el 5% de tus ingresos", "Busca educación financiera básica"],
        "book": "📖 'Las trampas del dinero' de Dan Ariely",
    },
    {
        "min": 0, "max": 34, "name": "Alerta Financiera", "emoji": "🚨", "grade": "D",
        "color": "#DC2626",
        "summary": "Tu situación financiera necesita una intervención completa. La transformación es posible pero requiere acción inmediata.",
        "strengths": ["La honestidad al responder es valiosa", "Nunca es tarde para empezar"],
        "improvements": ["PRIORIDAD 1: Para gastos innecesarios hoy", "PRIORIDAD 2: Lista de todas tus deudas", "PRIORIDAD 3: Busca asesoría financiera gratuita", "Empieza con micro-ahorro diario"],
        "book": "📖 'Pequeño cerdo capitalista' de Sofía Macías",
    },
]

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def get_total_questions():
    return sum(len(s["questions"]) for s in SECTIONS)

def get_profile(pct):
    for p in PROFILES:
        if p["min"] <= pct <= p["max"]:
            return p
    return PROFILES[-1]

def get_section_score(answers, section_id):
    section = next((s for s in SECTIONS if s["id"] == section_id), None)
    if not section:
        return 0, 0, 0
    total = 0
    mx = len(section["questions"]) * 5
    for q in section["questions"]:
        if q["id"] in answers:
            total += answers[q["id"]]["score"]
    return total, mx, round((total / mx) * 100) if mx > 0 else 0

def compute_results(answers):
    section_results = []
    for s in SECTIONS:
        score, mx, pct = get_section_score(answers, s["id"])
        section_results.append({
            "id": s["id"], "title": s["title"], "icon": s["icon"],
            "color": s["color"], "score": score, "max": mx, "pct": pct,
        })
    total_score = sum(r["score"] for r in section_results)
    total_max = sum(r["max"] for r in section_results)
    total_pct = round((total_score / total_max) * 100) if total_max > 0 else 0
    profile = get_profile(total_pct)
    tags = [answers[qid]["tag"] for qid in answers]
    return section_results, total_score, total_max, total_pct, profile, tags

def esc(s):
    """Escape user/content text for HTML and keep '$' from being parsed as LaTeX."""
    return html.escape(str(s)).replace("$", "&#36;")

def get_archetype(section_results, total_pct):
    pcts = {r["id"]: r["pct"] for r in section_results}
    if total_pct >= 80:
        return ARCHETYPES["gobernante"]
    if total_pct < 50:
        weakest = min(pcts, key=pcts.get)
        return ARCHETYPES["amante" if weakest in ("gastos", "consumidor") else "inocente"]
    strongest = max(pcts, key=pcts.get)
    return ARCHETYPES[{
        "planificacion": "sabio",
        "inversiones": "explorador",
        "ahorro": "cuidador",
        "deuda": "cuidador",
        "gastos": "heroe",
        "consumidor": "heroe",
    }[strongest]]

def get_biases(answers):
    """Return the bias ids triggered by the answers, in question order, without duplicates."""
    found = []
    for s in SECTIONS:
        for q in s["questions"]:
            b = answers.get(q["id"], {}).get("bias")
            if b and b not in found:
                found.append(b)
    return found

def get_weakest_sections(section_results, n=2):
    return sorted(section_results, key=lambda r: r["pct"])[:n]

def tag_color(qid):
    for s in SECTIONS:
        if any(q["id"] == qid for q in s["questions"]):
            return s["color"]
    return "#4ECDC4"

def save_result(row):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _DATA_LOCK:
        pd.DataFrame([row]).to_csv(DATA_FILE, mode="a", header=not DATA_FILE.exists(), index=False, encoding="utf-8")

def load_results():
    if not DATA_FILE.exists():
        return pd.DataFrame()
    with _DATA_LOCK:
        return pd.read_csv(DATA_FILE, encoding="utf-8")

def get_admin_password():
    try:
        return st.secrets["admin"]["password"]
    except Exception:
        return os.environ.get("FINPULSE_ADMIN_PASSWORD")

def monthly_rate(ea_pct):
    return (1 + ea_pct / 100) ** (1 / 12) - 1

def fmt_cop(x):
    return "$" + f"{x:,.0f}".replace(",", ".")

def build_email_body(name, total_pct, profile, section_results, tags, biases=()):
    name = esc(name)
    archetype = get_archetype(section_results, total_pct)
    campaign_html = "".join(
        f'<div style="margin-bottom:12px;"><div style="font-size:14px;font-weight:600;color:{r["color"]};">'
        f'{r["title"]}: {esc(CAMPAIGNS[r["id"]]["objetivo"])}</div>'
        f'<div style="font-size:12px;color:#FFD93D;font-family:\'Courier New\',monospace;">{esc(CAMPAIGNS[r["id"]]["kpi"])}</div>'
        + "".join(f'<div style="font-size:13px;color:rgba(255,255,255,0.75);padding:2px 0;">&#9642; {esc(t)}</div>'
                  for t in CAMPAIGNS[r["id"]]["tacticas"])
        + "</div>"
        for r in get_weakest_sections(section_results)
    )
    biases_html = "".join(
        f'<div style="font-size:13px;color:rgba(255,255,255,0.75);padding:4px 0;">'
        f'<strong style="color:#FF9F1C;">{esc(BIASES[b]["name"])}</strong> &mdash; {esc(BIASES[b]["antidoto"])}</div>'
        for b in biases
    ) or '<div style="font-size:13px;color:rgba(255,255,255,0.75);">No caíste en ninguna táctica. ¡Ojo de marketer entrenado!</div>'

    # Build section bars HTML
    section_bars = ""
    for r in section_results:
        section_bars += f'''
        <tr>
            <td style="padding:8px 0;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td style="font-size:13px;color:#E8E8F0;font-weight:600;padding-bottom:4px;">
                            {r['title']}
                        </td>
                        <td style="font-size:13px;color:{r['color']};font-weight:700;text-align:right;font-family:'Courier New',monospace;">
                            {r['pct']}%
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <div style="background:rgba(255,255,255,0.08);border-radius:6px;height:10px;width:100%;">
                                <div style="background:{r['color']};border-radius:6px;height:10px;width:{r['pct']}%;"></div>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>'''

    # Build strengths
    strengths_html = "".join(
        f'<div style="font-size:13px;color:rgba(255,255,255,0.7);padding:3px 0;">&#10003; {s}</div>'
        for s in profile["strengths"]
    )

    # Build improvements
    improvements_html = "".join(
        f'<div style="font-size:13px;color:rgba(255,255,255,0.7);padding:3px 0;">&#9642; {s}</div>'
        for s in profile["improvements"]
    )

    # Build tags
    tags_html = "".join(
        f'<span style="display:inline-block;padding:4px 12px;border-radius:20px;font-size:11px;'
        f'background:rgba(78,205,196,0.15);color:#4ECDC4;margin:3px 4px;">{esc(t)}</span>'
        for t in tags
    )

    # Grade colors for the circle
    grade_bg = profile["color"]

    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0a1a;font-family:'Helvetica Neue',Arial,sans-serif;color:#E8E8F0;">

<!-- Wrapper -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#0a0a1a;">
<tr><td align="center" style="padding:20px 16px;">
<table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;">

    <!-- Header -->
    <tr><td style="padding:20px 24px;border-bottom:1px solid rgba(255,255,255,0.08);">
        <span style="font-size:20px;font-weight:700;background:linear-gradient(135deg,#4ECDC4,#C77DFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;color:#4ECDC4;">
            FinPulse
        </span>
        <span style="float:right;font-size:11px;color:rgba(255,255,255,0.3);padding-top:6px;">Diagnostico Financiero</span>
    </td></tr>

    <!-- Hero -->
    <tr><td style="text-align:center;padding:32px 24px 20px;">
        <!-- Score Circle -->
        <div style="width:120px;height:120px;border-radius:50%;border:4px solid {grade_bg};margin:0 auto 16px;display:flex;align-items:center;justify-content:center;position:relative;">
            <table cellpadding="0" cellspacing="0" border="0" width="120" height="120">
                <tr><td align="center" valign="middle" style="width:120px;height:120px;border-radius:50%;border:4px solid {grade_bg};">
                    <div style="font-size:36px;font-weight:700;color:{grade_bg};font-family:'Courier New',monospace;line-height:1;">{total_pct}%</div>
                    <div style="font-size:9px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:2px;">SCORE</div>
                </td></tr>
            </table>
        </div>
        <div style="display:inline-block;padding:4px 16px;border-radius:20px;background:{grade_bg}33;border:1px solid {grade_bg}66;color:{grade_bg};font-size:12px;font-weight:600;letter-spacing:1.5px;margin-bottom:10px;">
            GRADO {profile['grade']}
        </div>
        <div style="font-size:24px;font-weight:700;color:#E8E8F0;margin:8px 0 2px;">Hola, {name}</div>
        <div style="font-size:18px;font-weight:600;color:{grade_bg};margin-bottom:8px;">{profile['name']}</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.6;max-width:440px;margin:0 auto;">
            {profile['summary']}
        </div>
    </td></tr>

    <!-- Archetype -->
    <tr><td style="padding:0 24px 24px;">
        <div style="background:{archetype['color']}1A;border:1px solid {archetype['color']}55;border-radius:12px;padding:18px;text-align:center;">
            <div style="font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:1.5px;text-transform:uppercase;">Tu arquetipo de marca financiera</div>
            <div style="font-size:34px;margin:6px 0;">{archetype['emoji']}</div>
            <div style="font-size:20px;font-weight:700;color:{archetype['color']};">{archetype['name']}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.75);line-height:1.6;margin-top:6px;">{esc(archetype['desc'])}</div>
            <div style="font-size:13px;font-style:italic;color:{archetype['color']};margin-top:6px;">{esc(archetype['slogan'])}</div>
        </div>
    </td></tr>

    <!-- Divider -->
    <tr><td style="padding:0 24px;"><div style="height:1px;background:rgba(255,255,255,0.06);"></div></td></tr>

    <!-- Section Results -->
    <tr><td style="padding:24px;">
        <div style="font-size:15px;font-weight:600;color:#E8E8F0;margin-bottom:12px;">Resultados por Area</div>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:16px;">
            {section_bars}
        </table>
    </td></tr>

    <!-- Strengths & Improvements -->
    <tr><td style="padding:0 24px 24px;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td width="48%" valign="top" style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:16px;">
                    <div style="font-size:14px;font-weight:600;color:#10B981;margin-bottom:8px;">Fortalezas</div>
                    {strengths_html}
                </td>
                <td width="4%"></td>
                <td width="48%" valign="top" style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:12px;padding:16px;">
                    <div style="font-size:14px;font-weight:600;color:#EF4444;margin-bottom:8px;">Areas de Mejora</div>
                    {improvements_html}
                </td>
            </tr>
        </table>
    </td></tr>

    <!-- Tags -->
    <tr><td style="padding:0 24px 24px;">
        <div style="font-size:15px;font-weight:600;color:#E8E8F0;margin-bottom:10px;">Tu ADN Financiero</div>
        <div style="line-height:2.2;">
            {tags_html}
        </div>
    </td></tr>

    <!-- Book Recommendation -->
    <tr><td style="padding:0 24px 24px;">
        <div style="background:linear-gradient(135deg,rgba(78,205,196,0.1),rgba(199,125,255,0.1));border:1px solid rgba(78,205,196,0.2);border-radius:12px;padding:16px;text-align:center;">
            <div style="font-size:13px;color:rgba(255,255,255,0.5);margin-bottom:4px;">Lectura recomendada para tu nivel</div>
            <div style="font-size:15px;font-weight:600;color:#4ECDC4;">{profile['book'].replace('📖', '').strip()}</div>
        </div>
    </td></tr>

    <!-- 30-day campaign -->
    <tr><td style="padding:0 24px 24px;">
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:20px;">
            <div style="font-size:15px;font-weight:600;color:#FFD93D;margin-bottom:12px;">Tu campaña de 30 días</div>
            {campaign_html}
        </div>
    </td></tr>

    <!-- Biases -->
    <tr><td style="padding:0 24px 24px;">
        <div style="background:rgba(255,159,28,0.08);border:1px solid rgba(255,159,28,0.25);border-radius:12px;padding:20px;">
            <div style="font-size:15px;font-weight:600;color:#FF9F1C;margin-bottom:10px;">Tácticas de marketing que funcionan contigo</div>
            {biases_html}
        </div>
    </td></tr>

    <!-- Footer -->
    <tr><td style="padding:20px 24px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
        <div style="font-size:14px;font-weight:600;color:rgba(255,255,255,0.6);margin-bottom:4px;">
            Tu tienes el poder de transformar tu realidad financiera
        </div>
        <div style="font-size:12px;color:rgba(255,255,255,0.3);margin-top:12px;">
            Programa de Finanzas Personales<br>
            Maestria en Marketing
        </div>
        <div style="margin-top:16px;">
            <span style="font-size:16px;font-weight:700;background:linear-gradient(135deg,#4ECDC4,#C77DFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;color:#4ECDC4;">
                FinPulse
            </span>
        </div>
    </td></tr>

</table>
</td></tr>
</table>

</body>
</html>'''
    return html

def send_email_smtp(to_email, subject, body, smtp_server, smtp_port, sender_email, sender_password):
    # Clean ALL inputs of non-breaking spaces and hidden unicode
    def clean(s):
        if isinstance(s, str):
            return s.replace("\xa0", " ").replace("\u00a0", " ").replace("\u200b", "").strip()
        return s

    to_email = clean(to_email)
    smtp_server = clean(smtp_server)
    sender_email = clean(sender_email)
    sender_password = clean(sender_password)

    # Clean subject — remove non-ASCII for header compatibility
    clean_subject = re.sub(r'[^\x00-\x7F]+', '', subject).strip()
    if not clean_subject:
        clean_subject = "Tus Resultados - Diagnostico FinPulse"

    # Build HTML email
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = clean_subject

    # Plain text fallback
    plain_text = re.sub(r'<[^>]+>', '', body)
    plain_text = re.sub(r'\s+', ' ', plain_text).strip()
    msg.attach(MIMEText(plain_text[:500] + "...\n\nPara ver el reporte completo, abre este correo en un cliente que soporte HTML.", "plain", "utf-8"))

    # HTML body
    msg.attach(MIMEText(body, "html", "utf-8"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)

# ──────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────
SURVEY_DEFAULTS = {
    "stage": "welcome", "answers": {}, "current_section": 0, "current_q": 0,
    "student_name": "", "student_email": "", "email_sent": False, "email_status": "",
    "processed": False,
}
for key, default in list(SURVEY_DEFAULTS.items()) + [("admin_ok", False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ──────────────────────────────────────────────
# COMPACT HEADER
# ──────────────────────────────────────────────
hcol1, hcol2, hcol3 = st.columns([2, 6, 2])
with hcol1:
    st.markdown('<div class="finpulse-logo">💰 FinPulse</div>', unsafe_allow_html=True)
with hcol3:
    if st.session_state.stage != "admin":
        if st.button("📊 Admin", width="stretch"):
            st.session_state.stage = "admin"
            st.rerun()
    else:
        if st.button("← Volver", width="stretch"):
            st.session_state.stage = "welcome" if not st.session_state.answers else "results"
            st.rerun()

st.divider()

# ══════════════════════════════════════════════
# WELCOME SCREEN — compact two-column layout
# ══════════════════════════════════════════════
if st.session_state.stage == "welcome":
    left_col, spacer, right_col = st.columns([5, 1, 4])

    with left_col:
        st.markdown('<div class="welcome-emoji">💰</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="welcome-title">¿Qué tan saludable es<br>'
            '<span class="welcome-gradient">tu vida financiera?</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="welcome-sub">'
            "Descubre tu perfil financiero, el arquetipo de marca que define tu relación con el dinero "
            "y qué tácticas de marketing —las mismas que tú diseñas— funcionan contigo. "
            "Responde con honestidad: no hay respuestas correctas, solo tu realidad.</div>",
            unsafe_allow_html=True,
        )
        # Section icons
        sections_html = '<div class="welcome-sections">'
        for s in SECTIONS:
            sections_html += (
                f'<div class="welcome-section-item" style="border-top: 3px solid {s["color"]};">'
                f'<span class="ws-icon">{s["icon"]}</span>'
                f'<span class="ws-label">{s["title"]}</span></div>'
            )
        sections_html += "</div>"
        st.markdown(sections_html, unsafe_allow_html=True)

    with right_col:
        st.markdown(
            '<div class="form-card">'
            '<div class="form-title">🚀 Comienza tu diagnóstico</div>'
            '<div class="form-sub">Completa tus datos para iniciar</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        name = st.text_input("Nombre completo", value=st.session_state.student_name, placeholder="Ej: María López García", label_visibility="collapsed")
        email = st.text_input("Correo electrónico", value=st.session_state.student_email, placeholder="Ej: maria@universidad.edu.co", label_visibility="collapsed")
        email_ok = bool(EMAIL_RE.match(email.strip()))
        if email.strip() and not email_ok:
            st.caption("⚠️ Revisa el correo: parece incompleto (ej: nombre@dominio.com)")

        if st.button("🚀  Comenzar Diagnóstico →", width="stretch", type="primary", disabled=not (name.strip() and email_ok)):
            st.session_state.student_name = name.strip()
            st.session_state.student_email = email.strip()
            st.session_state.stage = "survey"
            st.session_state.answers = {}
            st.session_state.current_section = 0
            st.session_state.current_q = 0
            st.session_state.email_sent = False
            st.session_state.processed = False
            st.rerun()

        st.markdown(
            '<p style="font-size:11px;color:rgba(255,255,255,0.6);text-align:center;margin-top:8px;">'
            f"{get_total_questions()} preguntas · {len(SECTIONS)} secciones · ~6 minutos<br>"
            "Al final: tu arquetipo de marca financiera 🧬</p>",
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════
# SURVEY SCREEN
# ══════════════════════════════════════════════
elif st.session_state.stage == "survey":
    section = SECTIONS[st.session_state.current_section]
    question = section["questions"][st.session_state.current_q]
    total_q = get_total_questions()
    q_num = sum(len(SECTIONS[i]["questions"]) for i in range(st.session_state.current_section)) + st.session_state.current_q + 1

    # Progress bar
    progress_pct = len(st.session_state.answers) / total_q
    st.progress(progress_pct)
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;margin-top:-10px;margin-bottom:12px;">'
        f'<span style="font-size:11px;color:rgba(255,255,255,0.35);">Pregunta {q_num} de {total_q}</span>'
        f'<span style="font-size:11px;color:{section["color"]};font-family:\'Space Mono\',monospace;font-weight:700;">'
        f'{int(progress_pct * 100)}%</span></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        # Section badge
        st.markdown(
            f'<div class="section-badge" style="background:{section["color"]}12;border:1px solid {section["color"]}30;">'
            f'<span class="section-icon">{section["icon"]}</span>'
            f'<div><div class="section-label" style="color:{section["color"]};">{section["title"]}</div>'
            f'<div style="font-size:10px;color:rgba(255,255,255,0.3);margin-top:1px;">'
            f'Sección {st.session_state.current_section + 1} de {len(SECTIONS)}</div></div></div>',
            unsafe_allow_html=True,
        )

        # Question
        # Question text may contain trusted inline HTML (e.g. <s>); only neutralise '$' so it isn't read as LaTeX
        st.markdown(f'<div class="question-text">{question["text"].replace("$", "&#36;")}</div>', unsafe_allow_html=True)

        # Options
        letters = ["A", "B", "C", "D"]
        previous = st.session_state.answers.get(question["id"], {}).get("text")
        for i, opt in enumerate(question["options"]):
            if st.button(
                f"  {letters[i]}   ·   {opt['text'].replace('$', chr(92) + '$')}",
                key=f"opt_{question['id']}_{i}",
                width="stretch",
                type="primary" if opt["text"] == previous else "secondary",
            ):
                st.session_state.answers[question["id"]] = {
                    "score": opt["score"], "tag": opt["tag"], "text": opt["text"], "bias": opt.get("bias"),
                }
                sec = st.session_state.current_section
                q = st.session_state.current_q
                if q < len(SECTIONS[sec]["questions"]) - 1:
                    st.session_state.current_q = q + 1
                elif sec < len(SECTIONS) - 1:
                    st.session_state.current_section = sec + 1
                    st.session_state.current_q = 0
                else:
                    st.session_state.stage = "results"
                st.rerun()

        if q_num > 1 and st.button("← Pregunta anterior", key="prev_q"):
            if st.session_state.current_q > 0:
                st.session_state.current_q -= 1
            else:
                st.session_state.current_section -= 1
                st.session_state.current_q = len(SECTIONS[st.session_state.current_section]["questions"]) - 1
            st.rerun()

        # Dots
        dots_html = '<div class="progress-dots">'
        for si, s in enumerate(SECTIONS):
            for qi, q in enumerate(s["questions"]):
                qId = q["id"]
                is_active = si == st.session_state.current_section and qi == st.session_state.current_q
                is_done = qId in st.session_state.answers
                cls = "dot-active" if is_active else ("dot-done" if is_done else "")
                dots_html += f'<div class="dot {cls}" style="--dot-color:{s["color"]};"></div>'
        dots_html += "</div>"
        st.markdown(dots_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# RESULTS SCREEN
# ══════════════════════════════════════════════
elif st.session_state.stage == "results":
    answers = st.session_state.answers
    section_results, total_score, total_max, total_pct, profile, tags = compute_results(answers)
    archetype = get_archetype(section_results, total_pct)
    biases = get_biases(answers)
    weakest = get_weakest_sections(section_results)
    student_name = st.session_state.student_name
    email_body = build_email_body(student_name, total_pct, profile, section_results, tags, biases)
    email_subject = f"{profile['emoji']} Tus Resultados: {profile['name']} ({total_pct}%) - Diagnóstico FinPulse"

    # ── Send email + register ONCE per completed survey (the lab widgets below trigger many reruns) ──
    if not st.session_state.processed:
        st.session_state.processed = True
        try:
            smtp_server = st.secrets["smtp"]["server"].replace("\xa0", " ").strip()
            smtp_port = int(st.secrets["smtp"]["port"])
            sender_email = st.secrets["smtp"]["sender_email"].replace("\xa0", " ").strip()
            sender_password = st.secrets["smtp"]["sender_password"].replace("\xa0", " ").strip()
            ok, err = send_email_smtp(st.session_state.student_email, email_subject, email_body, smtp_server, smtp_port, sender_email, sender_password)
            if ok:
                st.session_state.email_sent = True
                st.session_state.email_status = "success"
            else:
                st.session_state.email_status = f"error: {err}"
        except Exception:
            st.session_state.email_status = "no_secrets"
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name": student_name, "email": st.session_state.student_email,
            "score": total_pct, "profile": profile["name"], "grade": profile["grade"],
            "archetype": archetype["name"],
            **{f"pct_{r['id']}": r["pct"] for r in section_results},
            "biases": ";".join(biases),
        }
        try:
            save_result(row)
        except Exception as e:
            st.toast(f"No se pudo guardar el resultado: {e}")

    # Hero
    st.markdown(
        f'<div class="result-hero">'
        f'<div class="result-emoji">{profile["emoji"]}</div>'
        f'<div class="grade-badge" style="background:{profile["color"]}20;border:1px solid {profile["color"]}40;color:{profile["color"]};">'
        f'GRADO {profile["grade"]}</div><br>'
        f'<div class="result-name">{esc(student_name)}</div>'
        f'<div class="result-profile" style="color:{profile["color"]};">{profile["name"]}</div>'
        f'<div class="result-summary">{profile["summary"]}</div></div>',
        unsafe_allow_html=True,
    )

    # Archetype
    a = archetype
    st.markdown(
        f'<div class="archetype-card" style="background:{a["color"]}14;border:1px solid {a["color"]}55;">'
        f'<div class="archetype-emoji">{a["emoji"]}</div><div>'
        f'<div class="archetype-kicker">Tu arquetipo de marca financiera</div>'
        f'<div class="archetype-name" style="color:{a["color"]};">{a["name"]}</div>'
        f'<div class="archetype-desc">{esc(a["desc"])}</div>'
        f'<div class="archetype-slogan" style="color:{a["color"]};">Tu slogan: {esc(a["slogan"])}</div>'
        f'<div class="archetype-desc" style="margin-top:8px;"><b>⚠️ Riesgo de marca:</b> {esc(a["riesgo"])}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Charts row
    col_gauge, col_radar = st.columns(2)

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_pct,
            number={"suffix": "%", "font": {"size": 42, "color": profile["color"], "family": "Space Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "rgba(255,255,255,0.15)", "tickfont": {"color": "rgba(255,255,255,0.3)", "size": 9}},
                "bar": {"color": profile["color"], "thickness": 0.3},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 34], "color": "rgba(220,38,38,0.1)"},
                    {"range": [35, 54], "color": "rgba(239,68,68,0.1)"},
                    {"range": [55, 69], "color": "rgba(245,158,11,0.1)"},
                    {"range": [70, 84], "color": "rgba(59,130,246,0.1)"},
                    {"range": [85, 100], "color": "rgba(16,185,129,0.1)"},
                ],
            },
            title={"text": "Score General", "font": {"size": 13, "color": "rgba(255,255,255,0.6)"}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=250, margin=dict(t=50, b=10, l=25, r=25),
            font={"family": "DM Sans"},
        )
        st.plotly_chart(fig_gauge, width="stretch")

    with col_radar:
        categories = [f'{r["icon"]} {r["title"]}' for r in section_results]
        values = [r["pct"] for r in section_results]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(78,205,196,0.15)",
            line=dict(color="#4ECDC4", width=2),
            marker=dict(size=5, color="#4ECDC4"),
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=8, color="rgba(255,255,255,0.3)"), gridcolor="rgba(255,255,255,0.06)"),
                angularaxis=dict(tickfont=dict(size=10, color="rgba(255,255,255,0.7)"), gridcolor="rgba(255,255,255,0.06)"),
            ),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, margin=dict(t=30, b=30, l=90, r=90),
            showlegend=False, font={"family": "DM Sans"},
        )
        st.plotly_chart(fig_radar, width="stretch")

    # Section Bars
    st.markdown("#### 📊 Resultados por Sección")
    for r in section_results:
        st.markdown(
            f'<div class="metric-card">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span class="metric-label">{r["icon"]} {r["title"]}</span>'
            f'<span class="metric-value" style="color:{r["color"]};">{r["pct"]}%</span></div>'
            f'<div class="metric-bar"><div class="metric-fill" style="width:{r["pct"]}%;'
            f'background:linear-gradient(90deg,{r["color"]},{r["color"]}aa);"></div></div></div>',
            unsafe_allow_html=True,
        )

    # ── Marketer's mirror: tactics that work on the student ──
    st.markdown("#### 🧠 Espejo del marketer: tácticas que funcionan contigo")
    st.caption("Como profesional de marketing diseñas estas estrategias. Como consumidor, también caes en ellas.")
    if biases:
        cols = st.columns(2)
        for i, b in enumerate(biases):
            info = BIASES[b]
            with cols[i % 2]:
                st.markdown(
                    f'<div class="bias-card" style="border-left:4px solid #FF9F1C;">'
                    f'<div class="bias-name" style="color:#FF9F1C;">{esc(info["name"])}</div>'
                    f'<div class="bias-row"><b>Cómo funciona:</b> {esc(info["como"])}</div>'
                    f'<div class="bias-row"><b>Cuando tú eres el marketer:</b> {esc(info["marketer"])}</div>'
                    f'<div class="bias-row"><b>🛡️ Antídoto:</b> {esc(info["antidoto"])}</div></div>',
                    unsafe_allow_html=True,
                )
    else:
        st.success("🛡️ No caíste en ninguna de las tácticas evaluadas. ¡Tienes ojo de marketer entrenado!")

    # ── 30-day campaign for the two weakest areas ──
    st.markdown("#### 🎯 Tu campaña de 30 días")
    st.caption("Un brief de marketing… pero el producto eres tú. Enfocado en tus dos áreas con más oportunidad.")
    cols = st.columns(len(weakest))
    for col, r in zip(cols, weakest):
        c = CAMPAIGNS[r["id"]]
        with col:
            st.markdown(
                f'<div class="campaign-card" style="border-top:3px solid {r["color"]};">'
                f'<div class="campaign-head" style="color:{r["color"]};">{r["icon"]} {r["title"]} · {r["pct"]}%</div>'
                f'<div class="bias-row"><b>Objetivo SMART:</b> {esc(c["objetivo"])}</div>'
                f'<div class="campaign-kpi">{esc(c["kpi"])}</div>'
                + "".join(f'<div class="insight-item">▸ {esc(t)}</div>' for t in c["tacticas"])
                + f'<div class="bias-row" style="margin-top:8px;font-style:italic;">💡 {esc(c["insight"])}</div></div>',
                unsafe_allow_html=True,
            )

    # Strengths & Improvements
    st.markdown("")
    col_s, col_i = st.columns(2)
    with col_s:
        st.markdown(
            '<div class="insight-card" style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);">'
            '<div class="insight-title" style="color:#10B981;">✅ Fortalezas</div>' +
            "".join(f'<div class="insight-item">• {s}</div>' for s in profile["strengths"]) +
            "</div>", unsafe_allow_html=True,
        )
    with col_i:
        st.markdown(
            '<div class="insight-card" style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);">'
            '<div class="insight-title" style="color:#EF4444;">🔧 Áreas de Mejora</div>' +
            "".join(f'<div class="insight-item">• {s}</div>' for s in profile["improvements"]) +
            "</div>", unsafe_allow_html=True,
        )

    # Tags
    st.markdown("#### 🏷️ Tu ADN Financiero")
    tags_html = '<div class="tag-cloud">'
    for qid, ans in answers.items():
        c = tag_color(qid)
        tags_html += f'<span class="tag" style="background:{c}15;border:1px solid {c}30;color:{c};">{esc(ans["tag"])}</span>'
    tags_html += "</div>"
    st.markdown(tags_html, unsafe_allow_html=True)

    # ── Financial lab: interactive simulators ──
    st.markdown("#### 🧪 Laboratorio financiero")
    st.caption("Juega con tus propios números. Cifras ilustrativas con fines educativos; no constituyen asesoría financiera.")
    tab_funnel, tab_hormiga, tab_cuotas = st.tabs(["🔻 El embudo de tu dinero", "☕ Gastos hormiga", "💳 Simulador de cuotas"])

    with tab_funnel:
        f1, f2 = st.columns([1, 1.3])
        with f1:
            ingreso = st.number_input("Ingreso mensual (COP)", min_value=0, value=3_000_000, step=100_000, key="lab_ingreso")
            fijos = st.slider("% Gastos fijos (arriendo, servicios, transporte, mercado)", 0, 100, 50, key="lab_fijos")
            variables = st.slider("% Gastos variables (salidas, compras, domicilios)", 0, 100, 30, key="lab_variables")
            deudas = st.slider("% Pago de deudas (tarjetas, créditos)", 0, 100, 10, key="lab_deudas")
        usado = fijos + variables + deudas
        ahorro_pct = max(0, 100 - usado)
        etapas = [ingreso, ingreso * (1 - fijos / 100), ingreso * (1 - (fijos + variables) / 100), ingreso * ahorro_pct / 100]
        etapas = [max(0, v) for v in etapas]
        with f2:
            fig_funnel = go.Figure(go.Funnel(
                y=["Ingreso", "Después de gastos fijos", "Después de gastos variables", "Ahorro (conversión final)"],
                x=etapas,
                text=[fmt_cop(v) for v in etapas], textinfo="text", textposition="auto",
                marker=dict(color=["#4ECDC4", "#FFD93D", "#FF9F1C", "#10B981"]),
                insidetextfont=dict(family="Space Mono", color="#0a0a1a", size=13),
                outsidetextfont=dict(family="Space Mono", color="#E8E8F0", size=13),
            ))
            fig_funnel.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300,
                margin=dict(t=10, b=10, l=10, r=10), font=dict(family="DM Sans", color="rgba(255,255,255,0.8)"),
            )
            st.plotly_chart(fig_funnel, width="stretch")
        if usado > 100:
            st.error(f"⚠️ Estás asignando {usado}% de tu ingreso: gastas más de lo que ganas. Ese faltante normalmente se cubre con deuda.")
        else:
            diag = []
            diag.append("✅ Necesidades dentro del 50%" if fijos <= 50 else f"⚠️ Gastos fijos en {fijos}% (referencia: 50%)")
            diag.append("✅ Deseos dentro del 30%" if variables <= 30 else f"⚠️ Gastos variables en {variables}% (referencia: 30%)")
            diag.append("✅ Ahorro de 20% o más" if ahorro_pct >= 20 else f"⚠️ Ahorro de {ahorro_pct}% (referencia: 20%)")
            st.markdown(
                f'<div class="lab-result">Tu <b>tasa de conversión a ahorro</b> es <b>{ahorro_pct}%</b>: '
                f'de cada {fmt_cop(100_000)} que entran, conviertes <b>{fmt_cop(1000 * ahorro_pct)}</b> en ahorro.<br>'
                f'Comparado con la regla 50/30/20: {" · ".join(diag)}</div>',
                unsafe_allow_html=True,
            )

    with tab_hormiga:
        h1, h2 = st.columns([1, 1.3])
        with h1:
            gasto_dia = st.number_input("Tu gasto hormiga (café, snack, domicilio…) por día (COP)", min_value=0, value=8_000, step=1_000, key="lab_hormiga")
            dias = st.slider("Días por semana", 1, 7, 5, key="lab_dias")
            anos = st.slider("Horizonte (años)", 1, 30, 10, key="lab_anos")
            tasa_inv = st.slider("Rentabilidad anual si lo invirtieras (EA %)", 0.0, 20.0, 9.0, 0.5, key="lab_tasa_inv")
        mensual = gasto_dia * dias * 52 / 12
        i = monthly_rate(tasa_inv)
        meses = list(range(0, anos * 12 + 1))
        aportado = [mensual * m for m in meses]
        invertido = [mensual * ((1 + i) ** m - 1) / i if i > 0 else mensual * m for m in meses]
        with h2:
            fig_h = go.Figure()
            fig_h.add_trace(go.Scatter(x=[m / 12 for m in meses], y=invertido, name="Si lo inviertes", fill="tozeroy",
                                       line=dict(color="#4ECDC4", width=2), fillcolor="rgba(78,205,196,0.15)"))
            fig_h.add_trace(go.Scatter(x=[m / 12 for m in meses], y=aportado, name="Lo que gastas", line=dict(color="#FF6B6B", width=2, dash="dot")))
            fig_h.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300,
                margin=dict(t=10, b=30, l=50, r=10), font=dict(family="DM Sans", color="rgba(255,255,255,0.7)"),
                legend=dict(orientation="h", y=1.1), xaxis=dict(title="Años", gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickformat=",.0f"),
            )
            st.plotly_chart(fig_h, width="stretch")
        st.markdown(
            f'<div class="lab-result">Ese gasto suma <b>{fmt_cop(mensual)}</b> al mes. En {anos} años habrás gastado '
            f'<b>{fmt_cop(aportado[-1])}</b>; invertido al {tasa_inv:.1f}% EA serían <b>{fmt_cop(invertido[-1])}</b>.<br>'
            f'Como diría un marketer: el <i>lifetime value</i> de tu café diario es {fmt_cop(invertido[-1])}.</div>',
            unsafe_allow_html=True,
        )

    with tab_cuotas:
        k1, k2 = st.columns([1, 1.3])
        with k1:
            precio = st.number_input("Precio de la compra (COP)", min_value=0, value=2_000_000, step=100_000, key="lab_precio")
            tasa_tc = st.slider("Tasa de interés de tu tarjeta (EA %) — revisa tu extracto", 0.0, 40.0, 26.0, 0.5, key="lab_tasa_tc")
            n_cuotas = st.select_slider("Número de cuotas", options=[1, 3, 6, 12, 24, 36], value=24, key="lab_cuotas")
        i = monthly_rate(tasa_tc)

        def plan(n):
            # In Colombia, purchases at 1 installment are typically interest-free
            if n == 1 or i == 0:
                return precio / n, 0.0
            cuota = precio * i / (1 - (1 + i) ** -n)
            return cuota, cuota * n - precio

        opciones = [1, 3, 6, 12, 24, 36]
        intereses = [plan(n)[1] for n in opciones]
        with k2:
            fig_c = go.Figure()
            fig_c.add_trace(go.Bar(x=[f"{n} cuota{'s' if n > 1 else ''}" for n in opciones], y=[precio] * len(opciones), name="Precio", marker_color="#4ECDC4"))
            fig_c.add_trace(go.Bar(x=[f"{n} cuota{'s' if n > 1 else ''}" for n in opciones], y=intereses, name="Intereses", marker_color="#FF6B6B",
                                   text=[fmt_cop(v) if v else "" for v in intereses], textposition="outside",
                                   textfont=dict(family="Space Mono", size=10, color="rgba(255,255,255,0.8)")))
            fig_c.update_layout(
                barmode="stack", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300,
                margin=dict(t=30, b=30, l=50, r=10), font=dict(family="DM Sans", color="rgba(255,255,255,0.7)"),
                legend=dict(orientation="h", y=1.15), yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickformat=",.0f"),
            )
            st.plotly_chart(fig_c, width="stretch")
        cuota, interes = plan(n_cuotas)
        st.markdown(
            f'<div class="lab-result">A <b>{n_cuotas}</b> cuota{"s" if n_cuotas > 1 else ""} pagarías <b>{fmt_cop(cuota)}</b> al mes. '
            f'El precio real termina siendo <b>{fmt_cop(precio + interes)}</b>: '
            f'<b>{fmt_cop(interes)}</b> en intereses ({(interes / precio * 100) if precio else 0:.0f}% más caro).<br>'
            f'La cuota es el precio que te comunican; el total es el precio que pagas.</div>',
            unsafe_allow_html=True,
        )

    # Book
    st.markdown("")
    st.info(f"📚 **Lectura recomendada:** {profile['book']}")

    # ── Email Status ──
    st.divider()
    email_status = st.session_state.get("email_status", "")

    if email_status == "success":
        st.markdown(
            f'<div style="padding:20px;border-radius:14px;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);text-align:center;">'
            f'<div style="font-size:28px;margin-bottom:8px;">✅</div>'
            f'<div style="font-size:16px;font-weight:600;color:#10B981;margin-bottom:4px;">¡Correo enviado automáticamente!</div>'
            f'<div style="font-size:13px;color:rgba(255,255,255,0.7);">Revisa tu bandeja en <strong style="color:#4ECDC4;">{esc(st.session_state.student_email)}</strong></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        with st.expander("👀 Ver contenido del correo enviado"):
            components.html(email_body, height=600, scrolling=True)
    elif email_status == "no_secrets":
        st.warning("⚠️ No se detectaron credenciales SMTP en Secrets. El correo no se envió automáticamente.")
        st.markdown("**Para activar el envío automático:** ve a Streamlit Cloud → Settings → Secrets y agrega las credenciales SMTP.")
        manual_tab, copy_tab = st.tabs(["📬 Enviar manualmente", "📋 Copiar correo"])
        with manual_tab:
            c1, c2 = st.columns(2)
            with c1:
                m_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
                m_port = st.number_input("Puerto", value=587)
            with c2:
                m_email = st.text_input("Email remitente")
                m_pass = st.text_input("App Password", type="password")
            if st.button("📬 Enviar Correo", type="primary", width="stretch"):
                if m_email and m_pass:
                    with st.spinner("Enviando..."):
                        ok, err = send_email_smtp(st.session_state.student_email, email_subject, email_body, m_server, int(m_port), m_email, m_pass)
                    if ok:
                        st.success(f"✅ Enviado a {st.session_state.student_email}")
                        st.session_state.email_sent = True
                        st.session_state.email_status = "success"
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {err}")
                else:
                    st.warning("⚠️ Completa email y contraseña")
        with copy_tab:
            st.markdown(f"**Asunto:** {email_subject}")
            st.text_area("Copia este contenido:", email_body, height=350)
    else:
        st.error(f"❌ Error al enviar correo: {email_status}")
        st.markdown("Puedes copiar el correo manualmente:")
        st.text_area("Correo HTML", email_body, height=300, label_visibility="collapsed")

    st.divider()
    if st.button("🔄 Nueva Encuesta", width="stretch"):
        for k, v in SURVEY_DEFAULTS.items():
            st.session_state[k] = v.copy() if isinstance(v, dict) else v
        st.rerun()

# ══════════════════════════════════════════════
# ADMIN PANEL (teacher)
# ══════════════════════════════════════════════
elif st.session_state.stage == "admin":
    st.markdown("#### 📊 Panel del Docente")

    if not st.session_state.admin_ok:
        admin_pw = get_admin_password()
        if not admin_pw:
            st.warning(
                "🔒 El panel está protegido porque contiene nombres y correos de los estudiantes. "
                "Configura una contraseña en Secrets:"
            )
            st.code('[admin]\npassword = "tu-clave-de-docente"', language="toml")
            st.caption("O define la variable de entorno FINPULSE_ADMIN_PASSWORD.")
            st.stop()
        pw = st.text_input("Contraseña de docente", type="password")
        if st.button("Entrar", type="primary"):
            if pw == admin_pw:
                st.session_state.admin_ok = True
                st.rerun()
            st.error("Contraseña incorrecta")
        st.stop()

    st.caption("Resultados acumulados de todos los estudiantes que completaron el diagnóstico")
    df = load_results()

    if df.empty:
        st.markdown(
            '<div style="text-align:center;padding:48px 20px;color:rgba(255,255,255,0.5);">'
            '<div style="font-size:40px;margin-bottom:12px;">📭</div>'
            "<p>Aún no hay estudiantes registrados.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        df["biases"] = df["biases"].fillna("")
        scores = df["score"]
        st.markdown(
            f'<div class="stats-container">'
            f'<div class="stat-item"><div class="stat-value" style="color:#4ECDC4;">{len(df)}</div><div class="stat-label">Total</div></div>'
            f'<div class="stat-item"><div class="stat-value" style="color:#FFD93D;">{round(scores.mean())}%</div><div class="stat-label">Promedio</div></div>'
            f'<div class="stat-item"><div class="stat-value" style="color:#10B981;">{scores.max()}%</div><div class="stat-label">Mejor</div></div>'
            f'<div class="stat-item"><div class="stat-value" style="color:#EF4444;">{scores.min()}%</div><div class="stat-label">Menor</div></div>'
            f"</div>", unsafe_allow_html=True,
        )

        chart_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False,
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="rgba(255,255,255,0.4)"), tickformat=",d"),
            xaxis=dict(tickfont=dict(color="rgba(255,255,255,0.6)", size=11)),
            font={"family": "DM Sans"},
        )

        col_a, col_b = st.columns(2)
        with col_a:
            # Class average per section
            sec_cols = [s for s in SECTIONS if f"pct_{s['id']}" in df.columns]
            avg = [round(df[f"pct_{s['id']}"].mean()) for s in sec_cols]
            cats = [f'{s["icon"]} {s["title"]}' for s in sec_cols]
            fig_cls = go.Figure(go.Scatterpolar(
                r=avg + [avg[0]], theta=cats + [cats[0]], fill="toself",
                fillcolor="rgba(255,217,61,0.15)", line=dict(color="#FFD93D", width=2),
            ))
            fig_cls.update_layout(
                title=dict(text="Promedio del grupo por sección", font=dict(size=13, color="rgba(255,255,255,0.6)")),
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(range=[0, 100], tickfont=dict(size=8, color="rgba(255,255,255,0.3)"), gridcolor="rgba(255,255,255,0.06)"),
                           angularaxis=dict(tickfont=dict(size=10, color="rgba(255,255,255,0.7)"), gridcolor="rgba(255,255,255,0.06)")),
                paper_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(t=50, b=30, l=90, r=90), font={"family": "DM Sans"},
            )
            st.plotly_chart(fig_cls, width="stretch")
        with col_b:
            arch_colors = {a["name"]: a["color"] for a in ARCHETYPES.values()}
            counts = df["archetype"].value_counts()
            fig_arch = go.Figure(go.Bar(
                x=counts.index, y=counts.values, marker_color=[arch_colors.get(n, "#fff") for n in counts.index],
                text=counts.values, textposition="outside", textfont=dict(color="rgba(255,255,255,0.8)", family="Space Mono"),
            ))
            fig_arch.update_layout(title=dict(text="Arquetipos del grupo", font=dict(size=13, color="rgba(255,255,255,0.6)")),
                                   height=320, margin=dict(t=50, b=30, l=35, r=15), **chart_layout)
            st.plotly_chart(fig_arch, width="stretch")

        col_c, col_d = st.columns(2)
        with col_c:
            grade_counts = {g: int((df["grade"] == g).sum()) for g in ["A+", "A", "B", "C", "D"]}
            grade_colors = {"A+": "#10B981", "A": "#3B82F6", "B": "#F59E0B", "C": "#EF4444", "D": "#DC2626"}
            fig_dist = go.Figure(go.Bar(
                x=list(grade_counts), y=list(grade_counts.values()), marker_color=[grade_colors[g] for g in grade_counts],
                text=list(grade_counts.values()), textposition="outside", textfont=dict(color="rgba(255,255,255,0.8)", family="Space Mono"),
            ))
            fig_dist.update_layout(title=dict(text="Distribución por Grado", font=dict(size=13, color="rgba(255,255,255,0.6)")),
                                   height=280, margin=dict(t=50, b=20, l=35, r=15), **chart_layout)
            st.plotly_chart(fig_dist, width="stretch")
        with col_d:
            bias_counts = {BIASES[b]["name"]: int(df["biases"].str.split(";").apply(lambda xs: b in xs).sum()) for b in BIASES}
            fig_bias = go.Figure(go.Bar(
                y=list(bias_counts), x=list(bias_counts.values()), orientation="h", marker_color="#FF9F1C",
                text=list(bias_counts.values()), textposition="outside", textfont=dict(color="rgba(255,255,255,0.8)", family="Space Mono"),
            ))
            fig_bias.update_layout(title=dict(text="Tácticas en las que más cae el grupo", font=dict(size=13, color="rgba(255,255,255,0.6)")),
                                   height=280, margin=dict(t=50, b=20, l=10, r=30), **chart_layout)
            st.plotly_chart(fig_bias, width="stretch")

        # Discussion prompt for class
        top_bias = max(bias_counts, key=bias_counts.get)
        weakest_sec = sec_cols[avg.index(min(avg))] if sec_cols else None
        if weakest_sec:
            pct_bias = round(bias_counts[top_bias] / len(df) * 100)
            st.markdown(
                f'<div class="lab-result">💡 <b>Insight para la clase:</b> el área más débil del grupo es '
                f'<b>{weakest_sec["icon"]} {weakest_sec["title"]}</b> ({min(avg)}%) y la táctica más efectiva sobre el grupo es '
                f'<b>{esc(top_bias)}</b> ({pct_bias}% de los estudiantes).<br>'
                f'Pregunta para debatir: <i>¿qué responsabilidad ética tenemos como marketers al usar esta táctica, '
                f'sabiendo que funciona incluso con nosotros?</i></div>',
                unsafe_allow_html=True,
            )

        st.markdown("")
        show_cols = ["timestamp", "name", "email", "score", "grade", "profile", "archetype"]
        st.dataframe(df[[c for c in show_cols if c in df.columns]].sort_values("timestamp", ascending=False),
                     width="stretch", hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, "finpulse_resultados.csv", "text/csv", width="stretch")
