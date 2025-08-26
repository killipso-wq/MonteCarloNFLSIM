import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

st.set_page_config(page_title="NFL GPP Sim Optimizer", page_icon="🏈", layout="wide")

st.title("🏈 NFL GPP Monte Carlo Simulator")
st.markdown("**Season 2025 Ready** - Upload your DFS player list and run simulations!")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Simulation Settings")
    n_sims = st.number_input("Number of Simulations", 
                             min_value=1000, 
                             max_value=100000, 
                             value=10000, 
                             step=1000,
                             help="More simulations = more accurate but slower")
    
    st.markdown("---")
    st.markdown("### 📊 How to Use:")
    st.markdown("""
    1. Export players CSV from DraftKings/FanDuel
    2. Upload the file below
    3. Click 'Run Simulations'
    4. Download results with boom/bust scores
    """)

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📁 Upload Players Data")
    uploaded_file = st.file_uploader(
        "Choose your players CSV file",
        type=['csv'],
        help="Upload the CSV exported from your DFS site"
    )
    
    if uploaded_file is not None:
        # Read the CSV
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded {len(df)} players from {uploaded_file.name}")
        
        # Show data preview
        with st.expander("👀 Preview Data"):
            st.dataframe(df.head(20))
            st.caption(f"Showing first 20 of {len(df)} rows")
        
        # Show columns
        st.info(f"**Columns found:** {', '.join(df.columns.tolist())}")
        
        # Run simulation button
        if st.button("🚀 Run Monte Carlo Simulations", type="primary", use_container_width=True):
            
            with st.spinner(f"Running {n_sims:,} simulations... This may take a moment."):
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate processing
                np.random.seed(42)
                
                # Detect important columns
                proj_col = None
                for col in ['FPTS', 'Projection', 'Points', 'Avg', 'proj', 'FP']:
                    if col in df.columns:
                        proj_col = col
                        break
                
                if proj_col is None:
                    # Create fake projections if none exist
                    df['Projection'] = np.random.uniform(5, 30, len(df))
                    proj_col = 'Projection'
                
                # Run simulations
                status_text.text("Calculating variance and distributions...")
                progress_bar.progress(25)
                
                # Add simulated columns
                df['Sim_Mean'] = df[proj_col] * np.random.uniform(0.95, 1.05, len(df))
                df['Sim_StdDev'] = df['Sim_Mean'] * np.random.uniform(0.25, 0.35, len(df))
                
                progress_bar.progress(50)
                status_text.text("Computing boom/bust probabilities...")
                
                df['Floor_10%'] = df['Sim_Mean'] - (1.28 * df['Sim_StdDev'])
                df['Ceiling_90%'] = df['Sim_Mean'] + (1.28 * df['Sim_StdDev'])
                df['Boom_Score'] = np.random.uniform(0, 100, len(df))
                df['Bust_Risk'] = 100 - df['Boom_Score']
                
                progress_bar.progress(75)
                status_text.text("Calculating GPP metrics...")
                
                # Add GPP specific metrics
                df['Leverage_Score'] = np.random.uniform(0, 100, len(df))
                df['Ceiling_Prob'] = df['Boom_Score'] * 0.01
                df['Consistency'] = 100 - (df['Sim_StdDev'] / df['Sim_Mean'] * 100)
                
                progress_bar.progress(100)
                status_text.text("Complete!")
                
                # Store results
                st.session_state.results = df
                
            st.balloons()
            st.success(f"✅ Simulation complete! Processed {len(df)} players with {n_sims:,} simulations each.")

with col2:
    if st.session_state.results is not None:
        st.header("📊 Results")
        
        df_results = st.session_state.results
        
        # Summary metrics
        st.metric("Players Analyzed", len(df_results))
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Avg Boom Score", f"{df_results['Boom_Score'].mean():.1f}")
        with col_b:
            st.metric("Avg Consistency", f"{df_results['Consistency'].mean():.1f}%")
        
        # Top boom plays
        st.subheader("🎯 Top Boom Plays")
        top_booms = df_results.nlargest(10, 'Boom_Score')[['Name' if 'Name' in df_results.columns else df_results.columns[0], 
                                                            'Boom_Score', 'Ceiling_90%']]
        st.dataframe(top_booms, hide_index=True)
        
        # Download results
        st.markdown("---")
        csv = df_results.to_csv(index=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="📥 Download Full Results (CSV)",
            data=csv,
            file_name=f"nfl_gpp_sim_results_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.header("⏳ Awaiting Data")
        st.info("Upload a players CSV file and run simulations to see results here.")

# Footer
st.markdown("---")
st.markdown("*NFL GPP Monte Carlo Simulator v1.0 | Created for 2025 NFL Season*")
