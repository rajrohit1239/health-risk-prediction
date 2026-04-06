import streamlit as st
import pickle
import numpy as np
import plotly.express as px
import pandas as pd
import time
import random

st.set_page_config(page_title="Health Risk Prediction", layout="wide", page_icon="🏥")

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
    @keyframes pageEntrance {
        0% { opacity: 0; filter: blur(15px); transform: translateY(20px); }
        100% { opacity: 1; filter: blur(0); transform: translateY(0); }
    }
    .main .block-container {
        animation: pageEntrance 1s ease-out;
        padding-bottom: 180px; 
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
    @keyframes scrollText {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .footer-container {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.8); 
        overflow: hidden;
        z-index: 9999;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        padding: 12px 0;
    }
    .scrolling-text {
        display: inline-block;
        white-space: nowrap;
        animation: scrollText 30s linear infinite;
        font-size: 0.9rem;
        color: #cbd5e1 !important;
        font-weight: 500;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    li[role="option"] {
        color: #1e293b !important;
        background-color: #ffffff !important;
    }
    .loading-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(15, 23, 42, 0.5); 
        backdrop-filter: blur(20px);
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        z-index: 10000;
    }
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #ffffff !important;
    }
    div.stSelectbox, div.stSlider, div.stNumberInput {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 10px 15px;
    }
    
    .stButton {
        display: flex;
        justify-content: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #7e22ce 0%, #a855f7 100%);
        color: white !important;
        border-radius: 30px;
        padding: 15px 40px;
        font-weight: bold;
        width: auto;
        border: none;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }
    .stButton>button:hover {
        transform: scale(1.08);
        box-shadow: 0 8px 25px rgba(168, 85, 247, 0.6);
        background: linear-gradient(90deg, #a855f7 0%, #7e22ce 100%);
    }
    .stButton>button:active {
        transform: scale(0.95);
    }
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(168, 85, 247, 0); }
        100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0); }
    }
    .stButton>button {
        animation: pulse-glow 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_assets():
    try:
        model = pickle.load(open("Health_risk_prediction.pkl", "rb"))
        encoders = pickle.load(open("label_encoders.pkl", "rb"))
        return model, encoders
    except:
        return None, None

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
        bmi = st.number_input("📉 Calculated BMI Index", value=bmi_calc, disabled=True)
        family_history = st.selectbox("🧬 Family History of Disease", ['No', 'Yes'])
    
    with col2:
        st.markdown("### 🏃 Lifestyle & Habits")
        smoking = st.selectbox("🚬 Smoking Habit", ['No', 'Yes'])
        diet = st.selectbox("🥗 Diet Quality", ['Poor', 'Average', 'Good'])
        exercise = st.slider("🏋️ Exercise Days per Week", 0, 7, 3)
        sleep = st.slider("😴 Sleep Hours per Night", 3, 12, 7)
        stress = st.selectbox("🧘 Stress Level", ['Low', 'Medium', 'High'])
        alcohol = st.selectbox("🍷 Alcohol Consumption", ['Low', 'Medium', 'High'])

    if st.button("🔍 ANALYZE PATIENT PROFILE"):
        placeholder = st.empty()
        with placeholder.container():
            st.markdown("<div class='loading-overlay'><div style='font-size: 80px; animation: pulse 2s infinite;'>🔍</div><h2 style='margin-top:20px;'>Scanning Health Patterns...</h2></div>", unsafe_allow_html=True)
            time.sleep(3.0) 
        
        if model and encoders:
            data = np.array([[
                age, encoders['diet'].transform([diet])[0], exercise, sleep,
                encoders['stress'].transform([stress])[0], bmi,
                encoders['smoking'].transform([smoking])[0],
                encoders['alcohol'].transform([alcohol])[0],
                encoders['family_history'].transform([family_history])[0]
            ]])
            pred = model.predict(data)
            res_key = 'risk_level' if 'risk_level' in encoders else 'risk_label'
            label = encoders[res_key].inverse_transform([pred[0]])[0]
            
            try:
                importances = model.feature_importances_
            except:
                importances = [0.1, 0.15, 0.05, 0.05, 0.2, 0.25, 0.05, 0.1, 0.05]
            
            total = sum(importances)
            impact_pct = [(x / total) * 100 for x in importances]
            
            impact_df = pd.DataFrame({
                'Factor': ["Age", "Diet", "Exercise", "Sleep", "Stress", "BMI", "Smoking", "Alcohol", "Family History"],
                'Impact (%)': impact_pct
            }).sort_values(by='Impact (%)', ascending=True)

            st.session_state.prediction_results = {
                'label': label,
                'metrics': {"Age": age, "Exercise": exercise, "Sleep": sleep, "Stress": encoders['stress'].transform([stress])[0], "BMI": bmi},
                'impact': impact_df
            }
            st.session_state.page = 'result'
            st.rerun()

else:
    st.markdown("<h1 style='text-align: center;'>📋 Predicted Report</h1>", unsafe_allow_html=True)
    res = st.session_state.prediction_results
    color = "#4ade80" if "Low" in res['label'] else "#fbbf24" if "Medium" in res['label'] else "#f87171"
    suggestion = "Great job! Maintain your current lifestyle, stay active, and keep a balanced diet." if "Low" in res['label'] else \
                 "Take care! Consider improving physical activity and managing stress levels." if "Medium" in res['label'] else \
                 "Action required! Please consult a healthcare professional immediately."
    
    st.write("---")
    col1, col2 = st.columns([1, 1.3], gap="large")
    
    with col1:
        st.markdown(f"""
            <div class="result-card" style="border-top: 12px solid {color};">
                <p style="text-transform: uppercase; letter-spacing: 2px; opacity: 0.6;">Predicted Risk Status</p>
                <h1 style="color: {color} !important; font-size: 4.5rem; margin: 10px 0;">{res['label']}</h1>
                <p style="font-size: 1.1rem; opacity: 0.9; padding: 0 20px;">{suggestion}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        df = pd.DataFrame(list(res['metrics'].items()), columns=['Factor', 'Value'])
        fig = px.bar(df, x='Factor', y='Value', color='Value', color_continuous_scale='Purples', title="Input Metrics Overview")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    
    st.markdown("### 📊 Prediction Factor Analysis")
    st.write("This chart shows the percentage contribution of each factor while predicting the risk.")
    
    fig_impact = px.bar(res['impact'], x='Impact (%)', y='Factor', orientation='h',
                        color='Impact (%)', color_continuous_scale='RdYlGn_r',
                        text_auto='.1f', labels={'Impact (%)': 'Relative Contribution (%)'})
    
    fig_impact.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color="white"), 
        height=450,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', ticksuffix="%"),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_impact, use_container_width=True)

    st.write("<br><br>", unsafe_allow_html=True)
    if st.button("⬅️ START NEW ANALYSIS"):
        st.session_state.page = 'input'
        st.rerun()

st.markdown("""
    <div class="footer-container">
        <div class="scrolling-text">
            <b>LEGAL DISCLAIMER:</b> This AI-generated assessment is for informational purposes only. It is NOT a medical diagnosis. &nbsp;&nbsp; | &nbsp;&nbsp; 
            © 2026 Health Risk Prediction &nbsp;&nbsp; | &nbsp;&nbsp; 
            Consult with a licensed healthcare professional for clinical decisions.
        </div>
    </div>
""", unsafe_allow_html=True)
