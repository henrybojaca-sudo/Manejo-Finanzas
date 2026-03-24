import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import smtplib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

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
# CUSTOM CSS
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

    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stDecoration"] {display: none;}

    /* ── Custom Header ── */
    .finpulse-header {
        padding: 16px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .finpulse-logo {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #4ECDC4, #C77DFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Welcome ── */
    .welcome-title {
        font-size: 40px;
        font-weight: 700;
        letter-spacing: -1.5px;
        line-height: 1.15;
        text-align: center;
        color: #E8E8F0;
        margin-bottom: 4px;
    }
    .welcome-gradient {
        background: linear-gradient(135deg, #4ECDC4, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .welcome-sub {
        text-align: center;
        color: rgba(255,255,255,0.45);
        font-size: 15px;
        max-width: 460px;
        margin: 0 auto 36px;
        line-height: 1.6;
    }
    .emoji-float {
        text-align: center;
        font-size: 60px;
        animation: floater 3s ease-in-out infinite;
        margin-bottom: 20px;
    }
    @keyframes floater {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-12px); }
    }

    /* ── Section Badge ── */
    .section-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 16px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .section-icon {
        font-size: 28px;
    }
    .section-label {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* ── Question Card ── */
    .question-text {
        font-size: 22px;
        font-weight: 600;
        color: #E8E8F0;
        line-height: 1.4;
        letter-spacing: -0.3px;
        margin-bottom: 28px;
    }

    /* ── Option Buttons ── */
    .option-btn {
        display: flex;
        align-items: center;
        gap: 14px;
        width: 100%;
        padding: 16px 20px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
        color: #E8E8F0;
        font-size: 14px;
        line-height: 1.5;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 10px;
        text-align: left;
    }
    .option-btn:hover {
        background: rgba(255,255,255,0.07);
        border-color: rgba(255,255,255,0.18);
        transform: translateX(4px);
    }
    .option-letter {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        border: 1.5px solid rgba(255,255,255,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        color: rgba(255,255,255,0.35);
        flex-shrink: 0;
    }

    /* ── Progress dots ── */
    .progress-dots {
        display: flex;
        justify-content: center;
        gap: 5px;
        margin-top: 32px;
        flex-wrap: wrap;
    }
    .dot {
        width: 7px;
        height: 7px;
        border-radius: 4px;
        background: rgba(255,255,255,0.1);
        transition: all 0.3s;
    }
    .dot-active {
        width: 22px;
        background: var(--dot-color, #4ECDC4);
    }
    .dot-done {
        background: var(--dot-color, #4ECDC4);
        opacity: 0.5;
    }

    /* ── Result Cards ── */
    .result-hero {
        text-align: center;
        padding: 32px 20px;
        margin-bottom: 32px;
    }
    .result-emoji {
        font-size: 60px;
        animation: floater 3s ease-in-out infinite;
        margin-bottom: 12px;
    }
    .grade-badge {
        display: inline-block;
        padding: 4px 18px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
    }
    .result-name {
        font-size: 30px;
        font-weight: 700;
        color: #E8E8F0;
        letter-spacing: -1px;
        margin-bottom: 4px;
    }
    .result-profile {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .result-summary {
        color: rgba(255,255,255,0.5);
        font-size: 14px;
        max-width: 520px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Metric Card ── */
    .metric-card {
        padding: 16px 20px;
        border-radius: 14px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #E8E8F0;
    }
    .metric-value {
        font-size: 14px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
    }
    .metric-bar {
        height: 10px;
        border-radius: 5px;
        background: rgba(255,255,255,0.06);
        margin-top: 8px;
        overflow: hidden;
    }
    .metric-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 1s ease;
    }

    /* ── Tags ── */
    .tag-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }
    .tag {
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }

    /* ── Strengths / Improvements ── */
    .insight-card {
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 12px;
    }
    .insight-title {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .insight-item {
        font-size: 13px;
        color: rgba(255,255,255,0.6);
        line-height: 1.6;
        margin-bottom: 4px;
    }

    /* ── Admin table ── */
    .admin-row {
        display: grid;
        grid-template-columns: 2fr 2fr 1fr 1fr 1.5fr;
        padding: 12px 16px;
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 8px;
        font-size: 13px;
        align-items: center;
    }
    .admin-header {
        display: grid;
        grid-template-columns: 2fr 2fr 1fr 1fr 1.5fr;
        padding: 8px 16px;
        font-size: 11px;
        font-weight: 600;
        color: rgba(255,255,255,0.35);
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 8px;
    }

    /* ── Streamlit overrides ── */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600;
        border-radius: 14px;
        padding: 12px 28px;
        transition: all 0.2s;
    }
    .stTextInput > div > div > input {
        font-family: 'DM Sans', sans-serif !important;
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: #fff !important;
        padding: 14px 18px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(78,205,196,0.5) !important;
        box-shadow: 0 0 0 1px rgba(78,205,196,0.2) !important;
    }
    .stTextInput label {
        color: rgba(255,255,255,0.5) !important;
        font-size: 13px !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 8px;
    }

    /* ── Plotly chart bg ── */
    .js-plotly-plot .plotly .bg {
        fill: transparent !important;
    }

    /* ── Email section ── */
    .email-section {
        padding: 24px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(78,205,196,0.08), rgba(199,125,255,0.08));
        border: 1px solid rgba(78,205,196,0.2);
        text-align: center;
        margin-top: 32px;
    }

    /* ── Stats card ── */
    .stats-container {
        display: flex;
        justify-content: space-around;
        padding: 20px;
        border-radius: 14px;
        background: rgba(78,205,196,0.06);
        border: 1px solid rgba(78,205,196,0.12);
        margin-top: 20px;
    }
    .stat-item {
        text-align: center;
    }
    .stat-value {
        font-size: 28px;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
    }
    .stat-label {
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        margin-top: 2px;
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
]

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
        "summary": "Tienes fundamentos pero hay oportunidades significativas de mejora. La buena noticia: estás en el camino correcto.",
        "strengths": ["Consciencia de la importancia del ahorro", "Disposición para mejorar", "Algunos hábitos positivos"],
        "improvements": ["Crea un presupuesto mensual detallado", "Construye un fondo de emergencia de 3 meses", "Comienza a invertir con montos pequeños", "Edúcate activamente en finanzas personales"],
        "book": "📖 'El hombre más rico de Babilonia' de George S. Clason",
    },
    {
        "min": 35, "max": 54, "name": "En Zona de Riesgo", "emoji": "⚠️", "grade": "C",
        "color": "#EF4444",
        "summary": "Tus hábitos financieros necesitan atención urgente. Pero reconocerlo es el primer paso para transformar tu realidad.",
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

def build_email_body(name, total_pct, profile, section_results, tags):
    sections_text = "\n".join(
        f"   {r['icon']} {r['title']}: {'█' * (r['pct'] // 10)}{'░' * (10 - r['pct'] // 10)} {r['pct']}%"
        for r in section_results
    )
    strengths_text = "\n".join(f"   ✅ {s}" for s in profile["strengths"])
    improvements_text = "\n".join(f"   🔧 {s}" for s in profile["improvements"])
    tags_text = ", ".join(tags)

    body = f"""¡Hola {name}! 👋

Gracias por completar el diagnóstico FinPulse de Finanzas Personales. Aquí tienes tus resultados detallados:

{'═' * 50}
{profile['emoji']}  TU PERFIL: {profile['name'].upper()} ({profile['grade']})
   Puntuación General: {total_pct}%
{'═' * 50}

{profile['summary']}

📊 RESULTADOS POR ÁREA:
{sections_text}

💪 TUS FORTALEZAS:
{strengths_text}

📋 PLAN DE ACCIÓN - ÁREAS DE MEJORA:
{improvements_text}

🏷️ TU ADN FINANCIERO:
   {tags_text}

📚 LECTURA RECOMENDADA:
   {profile['book']}

{'─' * 50}

💡 TIPS RÁPIDOS PARA EMPEZAR HOY:

1. Descarga una app de finanzas personales (Fintonic, Wallet, o un Excel simple)
2. Registra TODOS tus gastos durante los próximos 30 días
3. Establece una meta de ahorro específica para este mes
4. Dedica 15 minutos diarios a educación financiera

Recuerda: La salud financiera no se construye de la noche a la mañana, pero cada pequeña decisión cuenta. ¡Tú tienes el poder de transformar tu realidad financiera! 💪🚀

Con aprecio,
Programa de Finanzas Personales
Maestría en Marketing
"""
    return body

def send_email_smtp(to_email, subject, body, smtp_server, smtp_port, sender_email, sender_password):
    """Send email via SMTP."""
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, ""
    except Exception as e:
        return False, str(e)

# ──────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────
if "stage" not in st.session_state:
    st.session_state.stage = "welcome"
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_section" not in st.session_state:
    st.session_state.current_section = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "student_email" not in st.session_state:
    st.session_state.student_email = ""
if "all_students" not in st.session_state:
    st.session_state.all_students = []
if "email_sent" not in st.session_state:
    st.session_state.email_sent = False

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
col_logo, col_nav = st.columns([3, 1])
with col_logo:
    st.markdown('<div class="finpulse-logo">💰 FinPulse</div>', unsafe_allow_html=True)
with col_nav:
    if st.session_state.stage != "admin":
        if st.button("📊 Panel Admin", use_container_width=True):
            st.session_state.stage = "admin"
            st.rerun()
    else:
        if st.button("← Volver", use_container_width=True):
            st.session_state.stage = "welcome" if not st.session_state.answers else "results"
            st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════
# WELCOME SCREEN
# ══════════════════════════════════════════════
if st.session_state.stage == "welcome":
    st.markdown("&nbsp;", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="emoji-float">💰</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="welcome-title">¿Qué tan saludable es<br>'
            '<span class="welcome-gradient">tu vida financiera?</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="welcome-sub">'
            "Descubre tu perfil financiero en 5 minutos. Responde con honestidad "
            "— no hay respuestas correctas, solo tu realidad."
            "</div>",
            unsafe_allow_html=True,
        )

        name = st.text_input("👤 Tu nombre completo", value=st.session_state.student_name, placeholder="Ej: María López García")
        email = st.text_input("📧 Tu correo electrónico", value=st.session_state.student_email, placeholder="Ej: maria@universidad.edu.co")

        st.markdown("&nbsp;", unsafe_allow_html=True)

        if st.button("🚀  Comenzar Diagnóstico", use_container_width=True, type="primary", disabled=not (name.strip() and email.strip())):
            st.session_state.student_name = name.strip()
            st.session_state.student_email = email.strip()
            st.session_state.stage = "survey"
            st.session_state.answers = {}
            st.session_state.current_section = 0
            st.session_state.current_q = 0
            st.session_state.email_sent = False
            st.rerun()

        # Section icons preview
        st.markdown("&nbsp;", unsafe_allow_html=True)
        icon_cols = st.columns(5)
        for i, s in enumerate(SECTIONS):
            with icon_cols[i]:
                st.markdown(
                    f'<div style="text-align:center;opacity:0.45;">'
                    f'<div style="font-size:28px;">{s["icon"]}</div>'
                    f'<div style="font-size:10px;color:rgba(255,255,255,0.35);margin-top:4px;">{s["title"]}</div>'
                    f"</div>",
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
        f'<div style="display:flex;justify-content:space-between;margin-top:-8px;margin-bottom:20px;">'
        f'<span style="font-size:12px;color:rgba(255,255,255,0.35);">Pregunta {q_num} de {total_q}</span>'
        f'<span style="font-size:12px;color:{section["color"]};font-family:\'Space Mono\',monospace;font-weight:700;">'
        f'{int(progress_pct * 100)}%</span></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:
        # Section badge
        st.markdown(
            f'<div class="section-badge" style="background:{section["color"]}12;border:1px solid {section["color"]}30;">'
            f'<span class="section-icon">{section["icon"]}</span>'
            f'<div><div class="section-label" style="color:{section["color"]};">{section["title"]}</div>'
            f'<div style="font-size:11px;color:rgba(255,255,255,0.3);margin-top:2px;">'
            f'Sección {st.session_state.current_section + 1} de {len(SECTIONS)}</div></div></div>',
            unsafe_allow_html=True,
        )

        # Question
        st.markdown(f'<div class="question-text">{question["text"]}</div>', unsafe_allow_html=True)

        # Options
        letters = ["A", "B", "C", "D"]
        for i, opt in enumerate(question["options"]):
            if st.button(
                f"  {letters[i]}   ·   {opt['text']}",
                key=f"opt_{question['id']}_{i}",
                use_container_width=True,
            ):
                st.session_state.answers[question["id"]] = {"score": opt["score"], "tag": opt["tag"], "text": opt["text"]}

                # Advance
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

        # Dots
        dots_html = '<div class="progress-dots">'
        for si, s in enumerate(SECTIONS):
            for qi, q in enumerate(s["questions"]):
                is_active = si == st.session_state.current_section and qi == st.session_state.current_q
                is_done = q["id"] in st.session_state.answers
                cls = "dot-active" if is_active else ("dot-done" if is_done else "")
                dots_html += f'<div class="dot {cls}" style="--dot-color:{s["color"]};"></div>'
        dots_html += "</div>"
        st.markdown(dots_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# RESULTS SCREEN
# ══════════════════════════════════════════════
elif st.session_state.stage == "results":
    section_results, total_score, total_max, total_pct, profile, tags = compute_results(st.session_state.answers)

    # ── Hero ──
    st.markdown(
        f'<div class="result-hero">'
        f'<div class="result-emoji">{profile["emoji"]}</div>'
        f'<div class="grade-badge" style="background:{profile["color"]}20;border:1px solid {profile["color"]}40;color:{profile["color"]};">'
        f'GRADO {profile["grade"]}</div><br>'
        f'<div class="result-name">{st.session_state.student_name}</div>'
        f'<div class="result-profile" style="color:{profile["color"]};">{profile["name"]}</div>'
        f'<div class="result-summary">{profile["summary"]}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Charts row ──
    col_gauge, col_radar = st.columns(2)

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_pct,
            number={"suffix": "%", "font": {"size": 48, "color": profile["color"], "family": "Space Mono"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "rgba(255,255,255,0.15)", "tickfont": {"color": "rgba(255,255,255,0.3)", "size": 10}},
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
            title={"text": "Score General", "font": {"size": 14, "color": "rgba(255,255,255,0.5)"}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, margin=dict(t=60, b=20, l=30, r=30),
            font={"family": "DM Sans"},
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_radar:
        categories = [f'{r["icon"]} {r["title"]}' for r in section_results]
        values = [r["pct"] for r in section_results]
        colors = [r["color"] for r in section_results]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(78,205,196,0.15)",
            line=dict(color="#4ECDC4", width=2),
            marker=dict(size=6, color="#4ECDC4"),
            name="Tu perfil",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=True, tickfont=dict(size=9, color="rgba(255,255,255,0.3)"), gridcolor="rgba(255,255,255,0.06)"),
                angularaxis=dict(tickfont=dict(size=11, color="rgba(255,255,255,0.6)"), gridcolor="rgba(255,255,255,0.06)"),
            ),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(t=40, b=40, l=60, r=60),
            showlegend=False,
            font={"family": "DM Sans"},
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Section Bars ──
    st.markdown("### 📊 Resultados por Sección")
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

    # ── Bar chart comparison ──
    st.markdown("&nbsp;", unsafe_allow_html=True)
    fig_bar = go.Figure()
    for r in section_results:
        fig_bar.add_trace(go.Bar(
            x=[r["title"]], y=[r["pct"]],
            marker_color=r["color"], name=r["title"],
            text=[f'{r["pct"]}%'], textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.7)", size=13, family="Space Mono"),
        ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=320, showlegend=False,
        yaxis=dict(range=[0, 110], gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="rgba(255,255,255,0.3)")),
        xaxis=dict(tickfont=dict(color="rgba(255,255,255,0.5)", size=11)),
        margin=dict(t=20, b=40, l=40, r=20),
        font={"family": "DM Sans"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Strengths & Improvements ──
    col_s, col_i = st.columns(2)
    with col_s:
        st.markdown(
            '<div class="insight-card" style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);">'
            '<div class="insight-title" style="color:#10B981;">✅ Fortalezas</div>' +
            "".join(f'<div class="insight-item">• {s}</div>' for s in profile["strengths"]) +
            "</div>",
            unsafe_allow_html=True,
        )
    with col_i:
        st.markdown(
            '<div class="insight-card" style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);">'
            '<div class="insight-title" style="color:#EF4444;">🔧 Áreas de Mejora</div>' +
            "".join(f'<div class="insight-item">• {s}</div>' for s in profile["improvements"]) +
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Tags ──
    st.markdown("### 🏷️ Tu ADN Financiero")
    tags_html = '<div class="tag-cloud">'
    for i, t in enumerate(tags):
        c = SECTIONS[min(i // 4, len(SECTIONS) - 1)]["color"]
        tags_html += f'<span class="tag" style="background:{c}15;border:1px solid {c}30;color:{c};">{t}</span>'
    tags_html += "</div>"
    st.markdown(tags_html, unsafe_allow_html=True)

    # ── Book ──
    st.markdown("&nbsp;", unsafe_allow_html=True)
    st.info(f"📚 **Lectura recomendada para tu nivel:** {profile['book']}")

    # ── Email Section ──
    st.markdown("---")
    st.markdown("### 📧 Enviar Resultados por Correo")
    st.markdown(
        f"Se generará un correo personalizado con tus resultados y recomendaciones para "
        f"**{st.session_state.student_email}**"
    )

    email_method = st.radio(
        "Método de envío:",
        ["📋 Generar correo (copiar y pegar)", "📬 Enviar por SMTP (requiere configuración)"],
        horizontal=True,
    )

    if "📋" in email_method:
        if st.button("📋 Generar Correo Personalizado", type="primary", use_container_width=True):
            body = build_email_body(st.session_state.student_name, total_pct, profile, section_results, tags)
            st.session_state.generated_email = body
            st.session_state.email_sent = True
            # Save student record
            st.session_state.all_students.append({
                "name": st.session_state.student_name,
                "email": st.session_state.student_email,
                "score": total_pct,
                "profile": profile["name"],
                "grade": profile["grade"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })

        if st.session_state.email_sent and "generated_email" in st.session_state:
            st.success("✅ ¡Correo generado exitosamente!")
            st.markdown(f"**Asunto:** {profile['emoji']} Tus Resultados: {profile['name']} ({total_pct}%) - Diagnóstico FinPulse")
            st.text_area("Cuerpo del correo:", st.session_state.generated_email, height=400)

    else:
        with st.expander("⚙️ Configuración SMTP", expanded=True):
            st.caption("Configura estas credenciales en `secrets.toml` para producción")
            smtp_col1, smtp_col2 = st.columns(2)
            with smtp_col1:
                smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
                smtp_port = st.number_input("Puerto", value=587)
            with smtp_col2:
                sender_email = st.text_input("Email remitente", placeholder="finpulse@universidad.edu.co")
                sender_password = st.text_input("Contraseña / App Password", type="password")

        if st.button("📬 Enviar Correo Ahora", type="primary", use_container_width=True):
            if sender_email and sender_password:
                body = build_email_body(st.session_state.student_name, total_pct, profile, section_results, tags)
                subject = f"{profile['emoji']} Tus Resultados: {profile['name']} ({total_pct}%) - Diagnóstico FinPulse"
                with st.spinner("Enviando correo..."):
                    success, error = send_email_smtp(
                        st.session_state.student_email, subject, body,
                        smtp_server, int(smtp_port), sender_email, sender_password,
                    )
                if success:
                    st.success(f"✅ ¡Correo enviado exitosamente a {st.session_state.student_email}!")
                    st.session_state.all_students.append({
                        "name": st.session_state.student_name,
                        "email": st.session_state.student_email,
                        "score": total_pct,
                        "profile": profile["name"],
                        "grade": profile["grade"],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })
                    st.session_state.email_sent = True
                else:
                    st.error(f"❌ Error al enviar: {error}")
            else:
                st.warning("⚠️ Completa la configuración SMTP para enviar el correo.")

    # ── New survey button ──
    st.markdown("---")
    if st.button("🔄 Nueva Encuesta", use_container_width=True):
        st.session_state.stage = "welcome"
        st.session_state.answers = {}
        st.session_state.current_section = 0
        st.session_state.current_q = 0
        st.session_state.student_name = ""
        st.session_state.student_email = ""
        st.session_state.email_sent = False
        if "generated_email" in st.session_state:
            del st.session_state.generated_email
        st.rerun()

# ══════════════════════════════════════════════
# ADMIN PANEL
# ══════════════════════════════════════════════
elif st.session_state.stage == "admin":
    st.markdown("## 📊 Panel de Administración")
    st.markdown('<p style="color:rgba(255,255,255,0.4);font-size:14px;">Registro de estudiantes que han completado la encuesta</p>', unsafe_allow_html=True)

    students = st.session_state.all_students

    if not students:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;color:rgba(255,255,255,0.3);">'
            '<div style="font-size:48px;margin-bottom:16px;">📭</div>'
            "<p>Aún no hay estudiantes registrados en esta sesión.</p>"
            '<p style="font-size:12px;margin-top:8px;">Los registros se acumularán a medida que los estudiantes completen la encuesta.</p>'
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # Stats
        scores = [s["score"] for s in students]
        avg_score = round(sum(scores) / len(scores))
        max_score = max(scores)
        min_score = min(scores)

        st.markdown(
            f'<div class="stats-container">'
            f'<div class="stat-item"><div class="stat-value" style="color:#4ECDC4;">{len(students)}</div><div class="stat-label">Total</div></div>'
            f'<div class="stat-item"><div class="stat-value" style="color:#FFD93D;">{avg_score}%</div><div class="stat-label">Promedio</div></div>'
            f'<div class="stat-item"><div class="stat-value" style="color:#10B981;">{max_score}%</div><div class="stat-label">Mejor</div></div>'
            f'<div class="stat-item"><div class="stat-value" style="color:#EF4444;">{min_score}%</div><div class="stat-label">Menor</div></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("&nbsp;", unsafe_allow_html=True)

        # Distribution chart
        fig_dist = go.Figure()
        grade_counts = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        grade_colors = {"A+": "#10B981", "A": "#3B82F6", "B": "#F59E0B", "C": "#EF4444", "D": "#DC2626"}
        for s in students:
            grade_counts[s["grade"]] = grade_counts.get(s["grade"], 0) + 1
        for grade, count in grade_counts.items():
            fig_dist.add_trace(go.Bar(
                x=[grade], y=[count], marker_color=grade_colors.get(grade, "#fff"),
                name=grade, text=[count], textposition="outside",
                textfont=dict(color="rgba(255,255,255,0.7)", size=14, family="Space Mono"),
            ))
        fig_dist.update_layout(
            title=dict(text="Distribución por Grado", font=dict(size=14, color="rgba(255,255,255,0.6)")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, showlegend=False,
            yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(color="rgba(255,255,255,0.3)")),
            xaxis=dict(tickfont=dict(color="rgba(255,255,255,0.5)", size=14)),
            margin=dict(t=50, b=30, l=40, r=20),
            font={"family": "DM Sans"},
        )
        st.plotly_chart(fig_dist, use_container_width=True)

        # Table
        st.markdown(
            '<div class="admin-header">'
            "<span>Nombre</span><span>Correo</span><span>Score</span><span>Grado</span><span>Fecha</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        for s in students:
            p = get_profile(s["score"])
            st.markdown(
                f'<div class="admin-row">'
                f'<span style="font-weight:600;">{s["name"]}</span>'
                f'<span style="color:rgba(255,255,255,0.5);font-size:12px;">{s["email"]}</span>'
                f'<span style="color:{p["color"]};font-family:\'Space Mono\',monospace;font-weight:700;">{s["score"]}%</span>'
                f'<span><span style="padding:2px 10px;border-radius:6px;background:{p["color"]}20;color:{p["color"]};'
                f'font-size:12px;font-weight:600;">{s["grade"]}</span></span>'
                f'<span style="color:rgba(255,255,255,0.3);font-size:11px;">{s["timestamp"]}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

        # Download CSV
        st.markdown("&nbsp;", unsafe_allow_html=True)
        df = pd.DataFrame(students)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar Resultados (CSV)", csv, "finpulse_resultados.csv", "text/csv", use_container_width=True)
