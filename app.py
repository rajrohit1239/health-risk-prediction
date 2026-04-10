import streamlit as st
import pickle
import numpy as np
import plotly.express as px
import pandas as pd
import time
import random
from fpdf import FPDF
import io

st.set_page_config(page_title="Health Risk Prediction", layout="wide", page_icon="🏥")

def generate_pdf(res, suggestion, precautions):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(46, 16, 101) 
    pdf.cell(200, 20, "Health Risk Analysis Report", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, f"Predicted Risk Level: {res['label'].upper()}", ln=True, align='C', fill=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(46, 16, 101)
    pdf.cell(0, 10, "Patient Profile Data:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    
    for key, value in res['metrics'].items():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 8, f"{key}:", border=0)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f"{value}", border=0, ln=True)
    
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(46, 16, 101)
    pdf.cell(0, 10, "Summary & Suggestion:", ln=True)
    pdf.set_font("Arial", 'I', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 8, suggestion)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(46, 16, 101)
    pdf.cell(200, 10, "Health Maintenance & Precautions:", ln=True, align='L')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) 
    pdf.ln(4)
    
    pdf.set_font("Arial", '', 11)
    for p in precautions:
        pdf.multi_cell(0, 8, f" - {p}")
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.multi_cell(0, 8, "General Guidance: To maintain a high health index, ensure you stay hydrated, maintain a consistent sleep cycle, and engage in regular physical activity.")

    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 5, "LEGAL DISCLAIMER: Informational purposes only. Not a medical diagnosis.", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'prediction_results' not in st.session_state:
    st.session_state.prediction_results = None

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #2e1065 0%, #0c4a6e 100%);
        color: #ffffff !important;
    }
    
    .stButton>button, .stDownloadButton>button {
        position: relative;
        background: linear-gradient(180deg, #a855f7 0%, #7e22ce 100%) !important;
        color: white !important;
        border-radius: 30px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 12px 35px !important;
        font-weight: bold !important;
        overflow: hidden !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.4) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button::after, .stDownloadButton>button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -60%;
        width: 20%;
        height: 200%;
        background: rgba(255, 255, 255, 0.4);
        transform: rotate(30deg);
        transition: all 0.6s ease;
        z-index: 1;
    }

    .stButton>button:hover::after, .stDownloadButton>button:hover::after {
        left: 120%;
    }

    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 20px rgba(168, 85, 247, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.6) !important;
    }

    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(168, 85, 247, 0); }
        100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0); }
    }
    .stButton>button { animation: pulse-glow 2s infinite !important; }

    .loading-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(15, 23, 42, 0.9); 
        backdrop-filter: blur(25px);
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        z-index: 10000;
        color: white;
    }
    .scanner-container {
        position: relative; width: 150px; height: 150px;
        display: flex; justify-content: center; align-items: center;
    }
    .scanner-ring {
        position: absolute; border-radius: 50%; border: 2px solid transparent;
        border-top-color: #a855f7; border-bottom-color: #7e22ce;
        animation: spin 2s linear infinite;
    }
    .ring-1 { width: 100%; height: 100%; opacity: 0.8; }
    .ring-2 { width: 80%; height: 80%; animation-duration: 1.5s; animation-direction: reverse; opacity: 0.5; }
    .scanner-core {
        width: 40px; height: 40px; background-color: white;
        clip-path: polygon(10% 40%, 40% 40%, 40% 10%, 60% 10%, 60% 40%, 90% 40%, 90% 60%, 60% 60%, 60% 90%, 40% 90%, 40% 60%, 10% 60%);
        animation: pulse-core 1.5s ease-in-out infinite;
    }
    .scan-line {
        position: absolute; top: 0; left: 0; width: 100%; height: 4px;
        background: linear-gradient(90deg, transparent, rgba(168, 85, 247, 1), transparent);
        box-shadow: 0 0 15px #a855f7; animation: scan-sweep 3s ease-in-out infinite;
    }

    .dots::after {
        content: '.';
        animation: dot-loading 1.5s infinite;
    }
    @keyframes dot-loading {
        0% { content: '.'; }
        33% { content: '..'; }
        66% { content: '...'; }
        100% { content: '.'; }
    }

    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse-core { 
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.8; }
    }
    @keyframes scan-sweep {
        0%, 100% { top: 0%; opacity: 0; }
        10%, 90% { opacity: 1; }
        50% { top: 100%; opacity: 0.5; }
    }

    .result-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        padding: 50px 30px;
        border-radius: 30px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 400px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-top: 20px;
    }

    .main .block-container { animation: pageEntrance 1s ease-out; padding-bottom: 180px; }
    @keyframes pageEntrance {
        0% { opacity: 0; filter: blur(15px); transform: translateY(20px); }
        100% { opacity: 1; filter: blur(0); transform: translateY(0); }
    }
    .footer-container {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: rgba(0, 0, 0, 0.8); overflow: hidden; z-index: 9999;
        border-top: 1px solid rgba(255, 255, 255, 0.2); padding: 12px 0;
    }
    .scrolling-text {
        display: inline-block; white-space: nowrap;
        animation: scrollText 30s linear infinite; font-size: 0.9rem; color: #cbd5e1 !important;
    }
    @keyframes scrollText { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #1e293b !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }
    div.stSelectbox, div.stSlider, div.stNumberInput {
        background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 15px; padding: 10px 15px;
    }
    .bmi-status-container { display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 25px; }
    .bmi-badge { padding: 15px 25px; border-radius: 15px; font-weight: bold; text-align: center; width: 100%; border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def load_assets():
    try:
        model = pickle.load(open("Health_risk_prediction.pkl", "rb"))
        encoders = pickle.load(open("label_encoders.pkl", "rb"))
        return model, encoders
    except: return None, None

model, encoders = load_assets()

if st.session_state.page == 'input':
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem;'>🏥 Health Risk Prediction</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; opacity: 0.8;'>Using Machine Learning</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("### 👤 Personal Metrics")
        gender = st.selectbox("🚻 Gender", ["Male", "Female", "Other"])
        age = st.slider("🎂 Age", 18, 80, 22)
        weight = st.number_input("⚖️ Weight (kg)", 30.0, 200.0, 70.0)
        height_cm = st.slider("📏 Height (cm)", 100, 220, 170)
        height_m = height_cm / 100
        bmi_calc = round(weight / (height_m ** 2), 2)
        
        bmi_col, status_col = st.columns([2, 1])
        with bmi_col: bmi = st.number_input("📉 Calculated BMI Index", value=bmi_calc, disabled=True)
        with status_col:
            if bmi_calc < 24.6: status_text, status_color = "GOOD", "#4ade80"
            elif 24.6 <= bmi_calc <= 35: status_text, status_color = "MEDIUM", "#fbbf24"
            else: status_text, status_color = "HIGH", "#f87171"
            st.markdown(f'<div class="bmi-status-container"><div class="bmi-badge" style="background-color: {status_color}22; color: {status_color}; border-color: {status_color};">{status_text}</div></div>', unsafe_allow_html=True)

        family_history = st.selectbox("🧬 Family History of Disease", ['No', 'Yes'])
    
    with col2:
        st.markdown("### 🏃 Lifestyle & Habits")
        smoking = st.selectbox("🚬 Smoking Habit", ['No', 'Yes'])
        diet = st.selectbox("🥗 Diet Quality", ['Poor', 'Average', 'Good'])
        exercise = st.slider("🏋️ Exercise Days per Week", 0, 7, 3)
        sleep = st.slider("😴 Sleep Hours per Night", 3, 12, 7)
        stress = st.selectbox("🧘 Stress Level", ['Low', 'Medium', 'High'])
        alcohol = st.selectbox("🍷 Alcohol Consumption (**Low**: 0% Consumption)", ['Low', 'Medium', 'High'])

    if st.button("🔍 ANALYZE PATIENT PROFILE"):
        placeholder = st.empty()
        with placeholder.container():
            st.markdown("""
                <div class="loading-overlay">
                    <div class="scanner-container">
                        <div class="scanner-ring ring-1"></div>
                        <div class="scanner-ring ring-2"></div>
                        <div class="scanner-core"></div>
                        <div class="scan-line"></div>
                    </div>
                    <h2 style="margin-top:40px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">
                        Scanning Health Patterns<span class="dots"></span>
                    </h2>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(3.5) 
        
        if model and encoders:
            data = np.array([[age, encoders['diet'].transform([diet])[0], exercise, sleep, encoders['stress'].transform([stress])[0], bmi, encoders['smoking'].transform([smoking])[0], encoders['alcohol'].transform([alcohol])[0], encoders['family_history'].transform([family_history])[0]]])
            pred = model.predict(data)
            res_key = 'risk_level' if 'risk_level' in encoders else 'risk_label'
            label = encoders[res_key].inverse_transform([pred[0]])[0]
            
            try: importances = model.feature_importances_
            except: importances = [0.1, 0.15, 0.05, 0.05, 0.2, 0.25, 0.05, 0.1, 0.05]
            impact_df = pd.DataFrame({'Factor': ["Age", "Diet", "Exercise", "Sleep", "Stress", "BMI", "Smoking", "Alcohol", "Family History"], 'Impact (%)': [(x/sum(importances))*100 for x in importances]}).sort_values(by='Impact (%)', ascending=True)

            st.session_state.prediction_results = {
                'label': label,
                'metrics': {
                    "Age": age, "Gender": gender, "Weight": f"{weight} kg", "Height": f"{height_cm} cm",
                    "BMI Index": bmi, "Exercise": f"{exercise} days/week", "Sleep": f"{sleep} hours",
                    "Stress": stress, "Diet": diet, "Smoking": smoking, "Alcohol": alcohol, "Family History": family_history
                },
                'impact': impact_df
            }
            st.session_state.page = 'result'
            st.rerun()

else:
    res = st.session_state.prediction_results
    precautions = []
    m = res['metrics']
    if float(str(m['BMI Index'])) > 25: precautions.append("Monitor caloric intake and weight management.")
    if int(str(m['Exercise']).split()[0]) < 3: precautions.append("Increase activity: aim for 150 mins weekly.")
    if int(str(m['Sleep']).split()[0]) < 7: precautions.append("Prioritize sleep hygiene for 7-8 hours.")
    if m['Smoking'] == 'Yes': precautions.append("Quit smoking to reduce heart/lung risks.")
    if m['Stress'] == 'High': precautions.append("Incorporate meditation or stress-relief daily.")
    if not precautions: precautions.append("Maintain current healthy routines and annual check-ups.")

    st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
    head_col, btn_col = st.columns([2.5, 1])
    with head_col: st.markdown("<h1 style='margin:0;'>📋 Predicted Report</h1>", unsafe_allow_html=True)
    with btn_col:
        suggestion = "Great job! Maintain your current lifestyle, stay active, and keep a balanced diet." if "Low" in res['label'] else "Take care! Consider improving physical activity and managing stress levels." if "Medium" in res['label'] else "Action required! Please consult a healthcare professional immediately."
        pdf_data = generate_pdf(res, suggestion, precautions)
        st.download_button(label="📥 Download Report", data=pdf_data, file_name="Health_Risk_Report.pdf", mime="application/pdf", use_container_width=True)

    color = "#4ade80" if "Low" in res['label'] else "#fbbf24" if "Medium" in res['label'] else "#f87171"
    st.write("---")
    
    col1, col2 = st.columns([1, 1.3], gap="large")
    with col1:
        st.markdown(f"""
            <div class="result-card" style="border-top: 12px solid {color};">
                <p style="text-transform: uppercase; letter-spacing: 2px; opacity: 0.6;">Predicted Risk Status</p>
                <h1 style="color: {color} !important; font-size: 4.5rem; margin: 10px 0;">{res["label"]}</h1>
                <p style="font-size: 1.1rem; opacity: 0.9; padding: 0 20px;">{suggestion}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        df_p = pd.DataFrame([{"Factor": k, "Value": float(str(v).split()[0])} for k, v in res['metrics'].items() if any(char.isdigit() for char in str(v))])
        fig = px.bar(df_p, x='Factor', y='Value', color='Value', color_continuous_scale='Purples', title="Input Metrics Overview")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    st.markdown("### 📊 Prediction Factor Analysis")
    fig_i = px.bar(res['impact'], x='Impact (%)', y='Factor', orientation='h', color='Impact (%)', color_continuous_scale='RdYlGn_r', text_auto='.1f')
    fig_i.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=450)
    st.plotly_chart(fig_i, use_container_width=True)

    if st.button("⬅️ START NEW ANALYSIS"):
        st.session_state.page = 'input'
        st.rerun()

st.markdown('<div class="footer-container"><div class="scrolling-text"><b>LEGAL DISCLAIMER:</b> Informational only. Not a medical diagnosis. &nbsp;&nbsp; | &nbsp;&nbsp; © 2026 Health Risk Prediction &nbsp;&nbsp; | &nbsp;&nbsp; Consult a professional.</div></div>', unsafe_allow_html=True)
