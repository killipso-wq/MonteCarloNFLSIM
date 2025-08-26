import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import io

st.set_page_config(page_title="NFL EPA Monte Carlo Sim", page_icon="🏈", layout="wide")

# Header with methodology reference
st.title("🏈 NFL EPA Monte Carlo Simulator")
st.markdown("**Based on Expected Points Added (EPA) Methodology**")
st.markdown("*Implements variance-based Monte Carlo simulations for NFL GPP DFS*")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'correlations' not in st.session_state:
    st.session_state.correlations = None

# EPA-based variance by position (from typical NFL data)
POSITION_VARIANCE = {
    'QB': 0.35,
    'RB': 0.45,
    'WR': 0.40,
    'TE': 0.38,
    'DST': 0.42,
    'K': 0.30,
    'FLEX': 0.40
}

# Correlation matrix for stacks (QB-WR, etc)
STACK_CORRELATIONS = {
    'QB-WR1': 0.45,
    'QB-WR2': 0.32,
    'QB-TE': 0.28,
    'RB-DST': -0.25,
    'QB-OppDST': -0.15,
    'WR1-WR2': 0.18
}

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Simulation Settings")
    
    n_sims = st.number_input(
        "Number of Simulations", 
        min_value=1000, 
        max_value=100000, 
        value=10000, 
        step=1000,
        help="More simulations = more accurate EPA distributions"
    )
    
    st.markdown("---")
    st.subheader("📊 EPA Adjustments")
    
    home_boost = st.slider(
        "Home Field EPA Boost",
        min_value=0.0,
        max_value=0.2,
        value=0.05,
        step=0.01,
        help="EPA adjustment for home teams"
    )
    
    weather_impact = st.checkbox(
        "Apply Weather Adjustments",
        value=True,
        help="Reduce passing EPA in bad weather"
    )
    
    use_correlations = st.checkbox(
        "Use Player Correlations",
        value=True,
        help="Apply QB-WR stack correlations"
    )
    
    st.markdown("---")
    st.markdown("### 📖 EPA Methodology")
    st.markdown("""
    - **EPA**: Expected Points Added per play
    - **Variance**: Position-specific volatility
    - **Correlations**: Stack relationships
    - **Monte Carlo**: Simulate thousands of outcomes
    """)

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📁 Upload DFS Export")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your DraftKings/FanDuel CSV",
        type=['csv'],
        help="Export player pool from DFS site"
    )
    
    if uploaded_file is not None:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} players")
        
        # Data preview
        with st.expander("👀 Data Preview"):
            st.dataframe(df.head(20))
        
        # Detect columns
        st.info(f"**Columns found:** {', '.join(df.columns.tolist())}")
        
        # Column mapping
        st.subheader("🔧 Column Mapping")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            name_col = st.selectbox("Player Name", df.columns.tolist(), index=0)
            pos_col = st.selectbox("Position", df.columns.tolist(), index=1 if len(df.columns) > 1 else 0)
        
        with col_b:
            proj_col = st.selectbox("Projection/Points", df.columns.tolist(), index=2 if len(df.columns) > 2 else 0)
            salary_col = st.selectbox("Salary", df.columns.tolist(), index=3 if len(df.columns) > 3 else 0)
        
        with col_c:
            team_col = st.selectbox("Team (optional)", ['None'] + df.columns.tolist())
            opp_col = st.selectbox("Opponent (optional)", ['None'] + df.columns.tolist())
        
        # Run EPA Monte Carlo
        if st.button("🚀 Run EPA Monte Carlo Simulation", type="primary",

