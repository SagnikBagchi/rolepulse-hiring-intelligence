import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import re
from datetime import datetime, timezone
from collections import Counter

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="RolePulse",
    layout="wide"
)

# =====================================================
# MODERN UI STYLING
# =====================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

h1 {
    font-size: 3rem !important;
    font-weight: 700 !important;
    letter-spacing: -1px;
}

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
    border: 1px solid #374151;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 18px;
}

.stTabs [data-baseweb="tab"] {
    padding: 12px 22px;
    border-radius: 14px;
    background-color: transparent;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
    color: white !important;
}

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid #1f2937;
}

    resume_text = uploaded_resume.read().decode("utf-8")
