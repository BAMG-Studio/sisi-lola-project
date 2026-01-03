"""
═══════════════════════════════════════════════════════════════════════════════
SISI LOLA - TRAINING METRICS DASHBOARD
═══════════════════════════════════════════════════════════════════════════════
Streamlit dashboard for monitoring training, ingestion, and cost metrics.

Run: streamlit run metrics_dashboard.py
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    print("Missing dependencies. Run: pip install streamlit pandas plotly")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Database paths
INGESTION_DB = DATA_DIR / "ingestion_tracking.db"
PIPELINE_DB = Path(os.getenv("PROJECT_DB_PATH", "sisi_lola_data_pipeline.db"))

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Sisi Lola Training Metrics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .success-text { color: #00C853; }
    .warning-text { color: #FFD600; }
    .error-text { color: #FF5252; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_ingestion_stats(days: int = 30) -> Dict[str, Any]:
    """Get ingestion statistics from database"""
    if not INGESTION_DB.exists():
        return {"error": "No ingestion database found"}
    
    conn = sqlite3.connect(INGESTION_DB)
    
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Total items
    df_items = pd.read_sql_query(f"""
        SELECT * FROM ingested_items 
        WHERE ingested_at >= '{cutoff}'
    """, conn)
    
    # Run stats
    df_runs = pd.read_sql_query(f"""
        SELECT * FROM ingestion_runs 
        WHERE started_at >= '{cutoff}'
        ORDER BY started_at DESC
    """, conn)
    
    conn.close()
    
    return {
        "items": df_items,
        "runs": df_runs,
        "total_items": len(df_items),
        "total_runs": len(df_runs),
    }


def get_generation_metrics(days: int = 30) -> Dict[str, Any]:
    """Get generation metrics from pipeline database"""
    if not PIPELINE_DB.exists():
        return {"error": "No pipeline database found"}
    
    try:
        conn = sqlite3.connect(PIPELINE_DB)
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        df = pd.read_sql_query(f"""
            SELECT * FROM generation_metrics 
            WHERE end_time >= '{cutoff}'
        """, conn)
        
        conn.close()
        
        return {
            "data": df,
            "total": len(df),
            "total_cost": df["cost_usd"].sum() if "cost_usd" in df.columns else 0,
        }
    except Exception as e:
        return {"error": str(e)}


def get_training_runs(days: int = 90) -> pd.DataFrame:
    """Get training run history"""
    if not PIPELINE_DB.exists():
        return pd.DataFrame()
    
    try:
        conn = sqlite3.connect(PIPELINE_DB)
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        df = pd.read_sql_query(f"""
            SELECT * FROM training_runs 
            WHERE start_time >= '{cutoff}'
            ORDER BY start_time DESC
        """, conn)
        
        conn.close()
        return df
    except:
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image("https://via.placeholder.com/200x80?text=Sisi+Lola", width=200)
    st.title("🤖 Training Metrics")
    
    st.divider()
    
    # Time range selector
    time_range = st.selectbox(
        "Time Range",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days"
    )
    
    st.divider()
    
    # Quick stats
    st.subheader("Quick Stats")
    
    ingestion_stats = get_ingestion_stats(time_range)
    if "error" not in ingestion_stats:
        st.metric("Total Ingested", ingestion_stats["total_items"])
        st.metric("Ingestion Runs", ingestion_stats["total_runs"])
    
    gen_metrics = get_generation_metrics(time_range)
    if "error" not in gen_metrics:
        st.metric("Generations", gen_metrics["total"])
        st.metric("Total Cost", f"${gen_metrics['total_cost']:.2f}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown('<h1 class="main-header">🤖 Sisi Lola Training Dashboard</h1>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📥 Data Ingestion", 
    "🎯 Training Runs",
    "💰 Cost Tracking",
    "🔧 Quality Metrics"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

with tab1:
    st.header("System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎤 Voice Samples",
            value=ingestion_stats.get("items", pd.DataFrame()).query("data_type == 'voice'").shape[0] if "error" not in ingestion_stats else 0,
            delta="↑ Active"
        )
    
    with col2:
        st.metric(
            label="🎬 Video Clips",
            value=ingestion_stats.get("items", pd.DataFrame()).query("data_type == 'video'").shape[0] if "error" not in ingestion_stats else 0,
            delta="↑ Active"
        )
    
    with col3:
        st.metric(
            label="📝 Text Items",
            value=ingestion_stats.get("items", pd.DataFrame()).query("data_type == 'text'").shape[0] if "error" not in ingestion_stats else 0,
            delta="↑ Active"
        )
    
    with col4:
        training_runs = get_training_runs(time_range)
        st.metric(
            label="🚀 Training Runs",
            value=len(training_runs),
            delta="Active"
        )
    
    st.divider()
    
    # Data sources chart
    st.subheader("Data Sources Distribution")
    
    if "error" not in ingestion_stats and not ingestion_stats.get("items", pd.DataFrame()).empty:
        df = ingestion_stats["items"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # By data type
            fig = px.pie(
                df, 
                names="data_type", 
                title="By Data Type",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # By source type
            fig = px.pie(
                df, 
                names="source_type", 
                title="By Source",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No ingestion data available yet. Run the nightly ingestion pipeline.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: DATA INGESTION
# ═══════════════════════════════════════════════════════════════════════════════

with tab2:
    st.header("📥 Data Ingestion Pipeline")
    
    if "error" not in ingestion_stats:
        # Recent runs
        st.subheader("Recent Ingestion Runs")
        
        if not ingestion_stats.get("runs", pd.DataFrame()).empty:
            df_runs = ingestion_stats["runs"]
            st.dataframe(
                df_runs[["run_id", "started_at", "sources_processed", "items_ingested", "bytes_downloaded"]].head(10),
                use_container_width=True
            )
        
        # Ingestion over time
        st.subheader("Ingestion Trend")
        
        if not ingestion_stats.get("items", pd.DataFrame()).empty:
            df = ingestion_stats["items"].copy()
            df["date"] = pd.to_datetime(df["ingested_at"]).dt.date
            daily = df.groupby("date").size().reset_index(name="count")
            
            fig = px.line(
                daily, 
                x="date", 
                y="count",
                title="Items Ingested Per Day",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # By language
        st.subheader("Language Distribution")
        
        if not ingestion_stats.get("items", pd.DataFrame()).empty:
            df = ingestion_stats["items"]
            lang_counts = df["language"].value_counts()
            
            fig = px.bar(
                x=lang_counts.index, 
                y=lang_counts.values,
                title="Items by Language",
                labels={"x": "Language", "y": "Count"}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(ingestion_stats.get("error", "No data available"))
        st.info("Run: `python ml_training/scripts/nightly_ingestion.py --sources all`")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: TRAINING RUNS
# ═══════════════════════════════════════════════════════════════════════════════

with tab3:
    st.header("🎯 Training Runs")
    
    training_df = get_training_runs(time_range)
    
    if not training_df.empty:
        # Status overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            completed = len(training_df[training_df["status"] == "completed"])
            st.metric("Completed", completed, delta="✓")
        
        with col2:
            running = len(training_df[training_df["status"] == "running"])
            st.metric("Running", running)
        
        with col3:
            failed = len(training_df[training_df["status"] == "failed"])
            st.metric("Failed", failed, delta="!" if failed > 0 else None)
        
        st.divider()
        
        # Training history table
        st.subheader("Training History")
        st.dataframe(
            training_df[["run_id", "model_type", "samples_count", "epochs", "status", "validation_score"]],
            use_container_width=True
        )
        
        # Validation scores over time
        if "validation_score" in training_df.columns:
            completed_runs = training_df[training_df["status"] == "completed"]
            if not completed_runs.empty:
                fig = px.line(
                    completed_runs,
                    x="start_time",
                    y="validation_score",
                    color="model_type",
                    title="Validation Scores Over Time",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No training runs recorded yet.")
        st.code("""
# Start a training run:
python ml_training/scripts/train_unified.py --config ml_training/configs/training_config.yaml
        """)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: COST TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

with tab4:
    st.header("💰 Cost Tracking")
    
    gen_data = get_generation_metrics(time_range)
    
    if "error" not in gen_data and not gen_data.get("data", pd.DataFrame()).empty:
        df = gen_data["data"]
        
        # Total cost overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_cost = df["cost_usd"].sum()
            st.metric("Total Cost", f"${total_cost:.2f}")
        
        with col2:
            avg_cost = df["cost_usd"].mean()
            st.metric("Avg per Generation", f"${avg_cost:.4f}")
        
        with col3:
            cache_hits = df["cache_hit"].sum() if "cache_hit" in df.columns else 0
            total = len(df)
            cache_rate = (cache_hits / total * 100) if total > 0 else 0
            st.metric("Cache Hit Rate", f"{cache_rate:.1f}%")
        
        with col4:
            savings = cache_hits * avg_cost if cache_hits > 0 else 0
            st.metric("Cache Savings", f"${savings:.2f}")
        
        st.divider()
        
        # Cost by platform
        st.subheader("Cost by Platform")
        
        if "platform" in df.columns:
            platform_costs = df.groupby("platform")["cost_usd"].sum().reset_index()
            
            fig = px.bar(
                platform_costs,
                x="platform",
                y="cost_usd",
                title="Total Cost by Platform",
                color="platform"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost by model
        st.subheader("Cost by Model")
        
        if "model_name" in df.columns:
            model_costs = df.groupby("model_name")["cost_usd"].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=model_costs.index,
                y=model_costs.values,
                title="Top 10 Models by Cost",
                labels={"x": "Model", "y": "Cost ($)"}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Daily cost trend
        st.subheader("Daily Cost Trend")
        
        df["date"] = pd.to_datetime(df["end_time"]).dt.date
        daily_cost = df.groupby("date")["cost_usd"].sum().reset_index()
        
        fig = px.area(
            daily_cost,
            x="date",
            y="cost_usd",
            title="Daily Spending",
            labels={"cost_usd": "Cost ($)", "date": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No generation cost data available yet.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: QUALITY METRICS
# ═══════════════════════════════════════════════════════════════════════════════

with tab5:
    st.header("🔧 Quality Metrics")
    
    if "error" not in ingestion_stats and not ingestion_stats.get("items", pd.DataFrame()).empty:
        df = ingestion_stats["items"]
        
        # Quality distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Quality Score Distribution")
            
            if "quality_score" in df.columns:
                fig = px.histogram(
                    df,
                    x="quality_score",
                    nbins=20,
                    title="Quality Score Distribution",
                    color_discrete_sequence=["#667eea"]
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Quality Tier Breakdown")
            
            if "quality_tier" in df.columns:
                tier_counts = df["quality_tier"].value_counts()
                
                fig = px.pie(
                    names=tier_counts.index,
                    values=tier_counts.values,
                    title="Items by Quality Tier",
                    color_discrete_map={
                        "excellent": "#00C853",
                        "good": "#64DD17",
                        "acceptable": "#FFD600",
                        "poor": "#FF5252",
                        "unscored": "#9E9E9E"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Quality by source
        st.subheader("Average Quality by Source")
        
        if "quality_score" in df.columns and "source_id" in df.columns:
            source_quality = df.groupby("source_id")["quality_score"].mean().sort_values(ascending=False)
            
            fig = px.bar(
                x=source_quality.index[:15],
                y=source_quality.values[:15],
                title="Top 15 Sources by Quality",
                labels={"x": "Source", "y": "Avg Quality Score"}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No quality data available yet.")


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

st.divider()
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Sisi Lola Training Dashboard v2.0 | 
    <a href='https://github.com/BAMG-Studio/sisi-lola-project'>GitHub</a> | 
    <a href='https://huggingface.co/sisilolalive'>HuggingFace</a>
    </p>
</div>
""", unsafe_allow_html=True)
