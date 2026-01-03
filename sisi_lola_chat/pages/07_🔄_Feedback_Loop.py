#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🔄 FEEDBACK LOOP MONITORING DASHBOARD
═══════════════════════════════════════════════════════════════════════════════
Streamlit dashboard for monitoring the Replicate → Modal feedback loop.

Features:
- Real-time feedback statistics
- Training job tracking
- Quality metrics visualization
- Nigerian content analytics
- Cost monitoring
- Retraining trigger status

Add to your Streamlit multi-page app in the pages/ directory.
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import sqlite3
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Page configuration
st.set_page_config(
    page_title="Feedback Loop | Sisi Lola",
    page_icon="🔄",
    layout="wide"
)


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_db_path(db_name: str) -> Path:
    """Get path to database file."""
    # Try multiple locations
    candidates = [
        Path(f"09_FEEDBACK_LOOP/{db_name}"),
        Path(f"../{db_name}"),
        Path(db_name)
    ]
    
    for path in candidates:
        if path.exists():
            return path
    
    return Path(f"09_FEEDBACK_LOOP/{db_name}")


def query_feedback_db(query: str, params: tuple = ()) -> pd.DataFrame:
    """Query feedback database."""
    db_path = get_db_path("feedback_data.db")
    
    if not db_path.exists():
        return pd.DataFrame()
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.warning(f"Database query failed: {e}")
        return pd.DataFrame()


def query_trigger_db(query: str, params: tuple = ()) -> pd.DataFrame:
    """Query trigger database."""
    db_path = get_db_path("trigger_history.db")
    
    if not db_path.exists():
        return pd.DataFrame()
    
    try:
        with sqlite3.connect(str(db_path)) as conn:
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.warning(f"Database query failed: {e}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# METRICS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_feedback_stats() -> Dict[str, Any]:
    """Get overall feedback statistics."""
    stats = {
        "total": 0,
        "processed": 0,
        "training_ready": 0,
        "by_category": {},
        "by_source": {},
        "avg_quality": 0.0
    }
    
    # Total feedback
    df = query_feedback_db("SELECT COUNT(*) as count FROM feedback_items")
    if not df.empty:
        stats["total"] = df.iloc[0]["count"]
    
    # Processed
    df = query_feedback_db(
        "SELECT COUNT(*) as count FROM feedback_items WHERE is_processed = 1"
    )
    if not df.empty:
        stats["processed"] = df.iloc[0]["count"]
    
    # Training ready
    df = query_feedback_db(
        "SELECT COUNT(*) as count FROM feedback_items WHERE is_training_ready = 1"
    )
    if not df.empty:
        stats["training_ready"] = df.iloc[0]["count"]
    
    # By category
    df = query_feedback_db("""
        SELECT category, COUNT(*) as count 
        FROM feedback_items 
        GROUP BY category
    """)
    if not df.empty:
        stats["by_category"] = dict(zip(df["category"], df["count"]))
    
    # By source
    df = query_feedback_db("""
        SELECT source, COUNT(*) as count 
        FROM feedback_items 
        GROUP BY source
    """)
    if not df.empty:
        stats["by_source"] = dict(zip(df["source"], df["count"]))
    
    # Average quality
    df = query_feedback_db("""
        SELECT AVG(quality_score) as avg 
        FROM feedback_items 
        WHERE quality_score > 0
    """)
    if not df.empty and df.iloc[0]["avg"] is not None:
        stats["avg_quality"] = df.iloc[0]["avg"]
    
    return stats


def get_training_history() -> pd.DataFrame:
    """Get training run history."""
    return query_trigger_db("""
        SELECT 
            id,
            category,
            trigger_reason,
            started_at,
            completed_at,
            status,
            samples_used,
            estimated_cost_usd,
            actual_cost_usd,
            final_loss
        FROM training_runs
        ORDER BY started_at DESC
        LIMIT 20
    """)


def get_daily_costs() -> pd.DataFrame:
    """Get daily training costs."""
    return query_trigger_db("""
        SELECT 
            date(started_at) as date,
            SUM(COALESCE(actual_cost_usd, estimated_cost_usd)) as cost,
            COUNT(*) as runs
        FROM training_runs
        WHERE started_at > datetime('now', '-30 days')
        GROUP BY date(started_at)
        ORDER BY date DESC
    """)


def get_nigerian_content_stats() -> Dict[str, Any]:
    """Get Nigerian content statistics."""
    stats = {
        "total_nigerian": 0,
        "avg_cultural_relevance": 0.0,
        "by_language": {}
    }
    
    # Total with cultural relevance
    df = query_feedback_db("""
        SELECT COUNT(*) as count 
        FROM feedback_items 
        WHERE cultural_relevance > 0.5
    """)
    if not df.empty:
        stats["total_nigerian"] = df.iloc[0]["count"]
    
    # Average cultural relevance
    df = query_feedback_db("""
        SELECT AVG(cultural_relevance) as avg 
        FROM feedback_items 
        WHERE cultural_relevance > 0
    """)
    if not df.empty and df.iloc[0]["avg"] is not None:
        stats["avg_cultural_relevance"] = df.iloc[0]["avg"]
    
    # By detected language
    df = query_feedback_db("""
        SELECT language_detected, COUNT(*) as count 
        FROM feedback_items 
        WHERE language_detected IS NOT NULL
        GROUP BY language_detected
    """)
    if not df.empty:
        stats["by_language"] = dict(zip(df["language_detected"], df["count"]))
    
    return stats


def get_quality_distribution() -> pd.DataFrame:
    """Get quality score distribution."""
    return query_feedback_db("""
        SELECT 
            CASE 
                WHEN quality_score >= 0.9 THEN '0.9-1.0'
                WHEN quality_score >= 0.8 THEN '0.8-0.9'
                WHEN quality_score >= 0.7 THEN '0.7-0.8'
                WHEN quality_score >= 0.6 THEN '0.6-0.7'
                WHEN quality_score >= 0.5 THEN '0.5-0.6'
                ELSE '< 0.5'
            END as range,
            COUNT(*) as count
        FROM feedback_items
        WHERE quality_score > 0
        GROUP BY range
        ORDER BY range DESC
    """)


def get_recent_feedback(limit: int = 20) -> pd.DataFrame:
    """Get recent feedback items."""
    return query_feedback_db(f"""
        SELECT 
            id,
            category,
            source,
            rating,
            quality_score,
            cultural_relevance,
            is_training_ready,
            created_at
        FROM feedback_items
        ORDER BY created_at DESC
        LIMIT {limit}
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# STREAMLIT UI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    st.title("🔄 Feedback Loop Monitor")
    st.markdown("**Replicate → Modal Training Pipeline**")
    
    # Sidebar
    with st.sidebar:
        st.header("🇳🇬 Sisi Lola")
        st.markdown("---")
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        
        if st.button("📊 Export Training Data"):
            st.info("Export functionality - connect to curator module")
        
        if st.button("🚀 Trigger Training Check"):
            st.info("Would evaluate training triggers")
        
        st.markdown("---")
        st.markdown("### Settings")
        show_raw_data = st.checkbox("Show raw data tables")
    
    # Main content - tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🎯 Quality",
        "🇳🇬 Nigerian Content",
        "🏋️ Training",
        "💰 Costs"
    ])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1: OVERVIEW
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab1:
        st.header("Feedback Overview")
        
        stats = get_feedback_stats()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Feedback",
                value=f"{stats['total']:,}"
            )
        
        with col2:
            st.metric(
                label="Processed",
                value=f"{stats['processed']:,}",
                delta=f"{stats['processed']/max(stats['total'], 1)*100:.1f}%"
            )
        
        with col3:
            st.metric(
                label="Training Ready",
                value=f"{stats['training_ready']:,}",
                delta=f"{stats['training_ready']/max(stats['processed'], 1)*100:.1f}%"
            )
        
        with col4:
            st.metric(
                label="Avg Quality",
                value=f"{stats['avg_quality']:.2f}"
            )
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("By Category")
            if stats["by_category"]:
                df_cat = pd.DataFrame([
                    {"Category": k, "Count": v}
                    for k, v in stats["by_category"].items()
                ])
                st.bar_chart(df_cat.set_index("Category"))
            else:
                st.info("No category data available")
        
        with col2:
            st.subheader("By Source")
            if stats["by_source"]:
                df_src = pd.DataFrame([
                    {"Source": k.replace("_", " ").title(), "Count": v}
                    for k, v in stats["by_source"].items()
                ])
                st.bar_chart(df_src.set_index("Source"))
            else:
                st.info("No source data available")
        
        # Recent feedback
        st.markdown("---")
        st.subheader("Recent Feedback")
        
        recent_df = get_recent_feedback()
        if not recent_df.empty:
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No feedback data available yet")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2: QUALITY
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab2:
        st.header("Quality Metrics")
        
        # Quality distribution
        quality_df = get_quality_distribution()
        
        if not quality_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Quality Score Distribution")
                st.bar_chart(quality_df.set_index("range"))
            
            with col2:
                st.subheader("Quality Thresholds")
                st.markdown("""
                | Threshold | Usage |
                |-----------|-------|
                | ≥ 0.75 | Training Ready |
                | ≥ 0.70 | Voice Training |
                | ≥ 0.65 | Image Training |
                | ≥ 0.60 | Text Training |
                | < 0.60 | Rejected |
                """)
        else:
            st.info("No quality data available yet")
        
        st.markdown("---")
        
        # Quality by category
        st.subheader("Average Quality by Category")
        
        quality_by_cat = query_feedback_db("""
            SELECT 
                category,
                AVG(quality_score) as avg_quality,
                COUNT(*) as count
            FROM feedback_items
            WHERE quality_score > 0
            GROUP BY category
        """)
        
        if not quality_by_cat.empty:
            st.dataframe(quality_by_cat, use_container_width=True)
        
        # Quality signals
        st.markdown("---")
        st.subheader("Quality Signals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Positive Indicators:**
            - Clear, accurate outputs
            - Nigerian cultural markers
            - High engagement (shares)
            - Positive user ratings
            """)
        
        with col2:
            st.markdown("""
            **Negative Indicators:**
            - PII detected
            - Low engagement
            - Negative feedback
            - Quality issues (noise, artifacts)
            """)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3: NIGERIAN CONTENT
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab3:
        st.header("🇳🇬 Nigerian Content Analytics")
        
        ng_stats = get_nigerian_content_stats()
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Nigerian Content Items",
                value=f"{ng_stats['total_nigerian']:,}"
            )
        
        with col2:
            st.metric(
                label="Avg Cultural Relevance",
                value=f"{ng_stats['avg_cultural_relevance']:.2f}"
            )
        
        with col3:
            bonus_items = ng_stats['total_nigerian']
            st.metric(
                label="Training Bonus Applied",
                value=f"+{bonus_items * 0.15:.0f} effective items"
            )
        
        st.markdown("---")
        
        # Languages detected
        st.subheader("Languages Detected")
        
        if ng_stats["by_language"]:
            df_lang = pd.DataFrame([
                {"Language": k.title() if k else "Unknown", "Count": v}
                for k, v in ng_stats["by_language"].items()
            ])
            st.bar_chart(df_lang.set_index("Language"))
        else:
            st.info("No language detection data available")
        
        st.markdown("---")
        
        # Nigerian markers
        st.subheader("Cultural Markers")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            **Pidgin:**
            - how far
            - no wahala
            - wetin dey
            - abeg
            - oya
            """)
        
        with col2:
            st.markdown("""
            **Yoruba:**
            - e kaaro
            - bawo ni
            - o dabiran
            - pele
            """)
        
        with col3:
            st.markdown("""
            **Hausa:**
            - sannu
            - yaya
            - da godiya
            - lafiya
            """)
        
        with col4:
            st.markdown("""
            **Igbo:**
            - kedu
            - nno
            - daalu
            - biko
            """)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 4: TRAINING
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab4:
        st.header("🏋️ Training Runs")
        
        training_df = get_training_history()
        
        if not training_df.empty:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            completed = len(training_df[training_df["status"] == "completed"])
            
            with col1:
                st.metric("Total Runs", len(training_df))
            
            with col2:
                st.metric("Completed", completed)
            
            with col3:
                avg_samples = training_df["samples_used"].mean()
                st.metric("Avg Samples", f"{avg_samples:.0f}")
            
            with col4:
                avg_loss = training_df["final_loss"].dropna().mean()
                st.metric("Avg Final Loss", f"{avg_loss:.3f}" if not pd.isna(avg_loss) else "N/A")
            
            st.markdown("---")
            
            # Training history table
            st.subheader("Training History")
            st.dataframe(training_df, use_container_width=True)
            
            # Trigger reasons
            st.markdown("---")
            st.subheader("Trigger Reasons")
            
            reason_counts = training_df["trigger_reason"].value_counts()
            if not reason_counts.empty:
                st.bar_chart(reason_counts)
        else:
            st.info("No training runs recorded yet")
            
            st.markdown("""
            **Training will be triggered when:**
            - ≥ 50 training-ready voice samples
            - ≥ 30 training-ready video samples  
            - ≥ 100 training-ready image samples
            - 7+ days since last training
            - Nigerian content bonus applies (1.5x weight)
            """)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 5: COSTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab5:
        st.header("💰 Cost Tracking")
        
        costs_df = get_daily_costs()
        
        if not costs_df.empty:
            # Summary
            total_cost = costs_df["cost"].sum()
            avg_daily = costs_df["cost"].mean()
            total_runs = costs_df["runs"].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total (30 days)", f"${total_cost:.2f}")
            
            with col2:
                st.metric("Daily Average", f"${avg_daily:.2f}")
            
            with col3:
                st.metric("Daily Limit", "$50.00")
            
            with col4:
                st.metric("Total Runs", total_runs)
            
            st.markdown("---")
            
            # Daily costs chart
            st.subheader("Daily Training Costs")
            costs_df["date"] = pd.to_datetime(costs_df["date"])
            costs_df = costs_df.set_index("date")
            st.line_chart(costs_df["cost"])
            
            # Cost breakdown
            st.markdown("---")
            st.subheader("Estimated Costs per Hour")
            
            cost_table = pd.DataFrame({
                "Category": ["Voice", "Video", "Image"],
                "Cost/Hour": ["$3.00", "$4.00", "$3.00"],
                "Max Hours": [2, 4, 2],
                "Max Cost": ["$6.00", "$16.00", "$6.00"]
            })
            st.table(cost_table)
        else:
            st.info("No cost data available yet")
            
            st.markdown("""
            **Cost Management:**
            - Daily limit: $50 USD
            - Training paused when limit reached
            - Costs resume next day
            """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🔄 **Feedback Loop** | Replicate → Modal | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


if __name__ == "__main__":
    main()
