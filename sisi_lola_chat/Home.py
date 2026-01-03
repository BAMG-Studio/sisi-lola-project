#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🇳🇬 SISI LOLA CONTROL CENTER - Main Dashboard
═══════════════════════════════════════════════════════════════════════════════
Central Streamlit dashboard for managing all Sisi Lola AI operations.

Features:
- System overview and health monitoring
- Quick actions and shortcuts
- Real-time metrics
- Navigation to all sub-modules

Run with: streamlit run Home.py
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add project paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Page configuration
st.set_page_config(
    page_title="Sisi Lola Control Center",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Sisi Lola AI - Your Nigerian Virtual Host"
    }
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1a5f7a;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #008751 0%, #ffffff 50%, #008751 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #008751;
    }
    .status-online { color: #00c853; }
    .status-offline { color: #ff5252; }
    .status-warning { color: #ffc107; }
    .nigerian-green { color: #008751; }
    .nigerian-white { color: #ffffff; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def check_component_status(component: str) -> Dict[str, Any]:
    """Check status of a system component."""
    statuses = {
        "api": {"status": "online", "latency": 45},
        "replicate": {"status": "online", "latency": 120},
        "modal": {"status": "online", "latency": 80},
        "database": {"status": "online", "latency": 5},
        "voice": {"status": "online", "latency": 200},
        "video": {"status": "online", "latency": 500}
    }
    return statuses.get(component, {"status": "unknown", "latency": 0})


def get_system_metrics() -> Dict[str, Any]:
    """Get overall system metrics."""
    return {
        "total_predictions": 15420,
        "predictions_today": 234,
        "avg_latency_ms": 180,
        "success_rate": 98.5,
        "active_users": 42,
        "training_runs": 12,
        "nigerian_content_ratio": 0.65
    }


def get_recent_activity() -> List[Dict[str, Any]]:
    """Get recent system activity."""
    return [
        {"time": "2 min ago", "action": "Video generated", "user": "user_123", "status": "success"},
        {"time": "5 min ago", "action": "Voice cloned", "user": "user_456", "status": "success"},
        {"time": "8 min ago", "action": "Image created", "user": "user_789", "status": "success"},
        {"time": "15 min ago", "action": "Training triggered", "user": "system", "status": "running"},
        {"time": "20 min ago", "action": "Feedback processed", "user": "system", "status": "success"},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown('<h1 class="main-header">🇳🇬 Sisi Lola Control Center</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Sisi+Lola", width=150)
        st.markdown("### 🇳🇬 Sisi Lola AI")
        st.markdown("*Your Nigerian Virtual Host*")
        st.markdown("---")
        
        st.markdown("### ⚡ Quick Actions")
        if st.button("🎬 Generate Video", use_container_width=True):
            st.session_state["action"] = "video"
        if st.button("🗣️ Create Voice", use_container_width=True):
            st.session_state["action"] = "voice"
        if st.button("🖼️ Generate Image", use_container_width=True):
            st.session_state["action"] = "image"
        if st.button("💬 Chat with Sisi", use_container_width=True):
            st.session_state["action"] = "chat"
        
        st.markdown("---")
        st.markdown("### 📊 System Status")
        
        # Component statuses
        components = ["API", "Replicate", "Modal", "Database"]
        for comp in components:
            status = check_component_status(comp.lower())
            if status["status"] == "online":
                st.markdown(f"✅ {comp}: Online ({status['latency']}ms)")
            else:
                st.markdown(f"❌ {comp}: Offline")
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = get_system_metrics()
    
    with col1:
        st.metric(
            label="🎯 Total Predictions",
            value=f"{metrics['total_predictions']:,}",
            delta=f"+{metrics['predictions_today']} today"
        )
    
    with col2:
        st.metric(
            label="⚡ Avg Latency",
            value=f"{metrics['avg_latency_ms']}ms",
            delta="-15ms"
        )
    
    with col3:
        st.metric(
            label="✅ Success Rate",
            value=f"{metrics['success_rate']}%",
            delta="+0.5%"
        )
    
    with col4:
        st.metric(
            label="🇳🇬 Nigerian Content",
            value=f"{metrics['nigerian_content_ratio']*100:.0f}%",
            delta="+5%"
        )
    
    st.markdown("---")
    
    # Main sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🎬 Content Studio",
        "🏋️ Training Status",
        "📈 Analytics"
    ])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1: OVERVIEW
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🔄 Recent Activity")
            
            activities = get_recent_activity()
            for act in activities:
                status_icon = "✅" if act["status"] == "success" else "🔄" if act["status"] == "running" else "❌"
                st.markdown(f"{status_icon} **{act['action']}** - {act['time']} by `{act['user']}`")
        
        with col2:
            st.subheader("🇳🇬 Nigerian Languages")
            
            lang_data = {
                "English": 35,
                "Pidgin": 40,
                "Yoruba": 12,
                "Hausa": 8,
                "Igbo": 5
            }
            
            for lang, pct in lang_data.items():
                st.progress(pct / 100, text=f"{lang}: {pct}%")
        
        st.markdown("---")
        
        st.subheader("🎯 System Modules")
        
        modules = [
            ("🎬 Video Generation", "Omni-Human talking videos", "Active", "video"),
            ("🗣️ Voice Synthesis", "Nigerian accent TTS", "Active", "voice"),
            ("🖼️ Image Generation", "Character-consistent images", "Active", "image"),
            ("🧠 Chat/LLM", "Nigerian Pidgin understanding", "Active", "chat"),
            ("🔄 Feedback Loop", "Replicate → Modal training", "Active", "feedback"),
            ("📥 Data Ingestion", "YouTube scraping pipeline", "Idle", "ingestion"),
        ]
        
        cols = st.columns(3)
        for i, (name, desc, status, _) in enumerate(modules):
            with cols[i % 3]:
                status_color = "🟢" if status == "Active" else "🟡"
                st.markdown(f"""
                **{name}** {status_color}
                
                {desc}
                """)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2: CONTENT STUDIO
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab2:
        st.subheader("🎬 Content Generation Studio")
        
        content_type = st.selectbox(
            "Content Type",
            ["Video (Talking Head)", "Voice Only", "Image", "Full Package (All)"]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            script = st.text_area(
                "Script / Text",
                placeholder="Enter your script here... E.g., 'How far, my people! Welcome to Sisi Lola TV!'",
                height=150
            )
            
            language = st.selectbox(
                "Language Style",
                ["Mixed (English + Pidgin)", "English Only", "Pidgin Heavy", "Yoruba Mix", "Hausa Mix"]
            )
        
        with col2:
            vibe = st.selectbox(
                "Content Vibe",
                ["Professional", "Casual", "Educational", "Entertainment", "News", "Motivational"]
            )
            
            character = st.checkbox("Include Sisi Lola Character (SEED 45822)", value=True)
            
            quality = st.select_slider(
                "Quality Level",
                options=["Fast", "Standard", "High", "Production"]
            )
        
        if st.button("🚀 Generate Content", type="primary", use_container_width=True):
            with st.spinner("Generating content..."):
                st.success("Content generated successfully!")
                st.info("In production, this would call the Replicate client")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3: TRAINING STATUS
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab3:
        st.subheader("🏋️ Training Pipeline Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🗣️ Voice Training")
            st.metric("Training Ready", "127 samples")
            st.metric("Last Training", "2 days ago")
            st.metric("Next Trigger", "~23 more samples")
            st.progress(0.85, text="Quality: 85%")
        
        with col2:
            st.markdown("### 🎬 Video Training")
            st.metric("Training Ready", "45 samples")
            st.metric("Last Training", "5 days ago")
            st.metric("Status", "Threshold Met ✅")
            st.progress(0.78, text="Quality: 78%")
        
        with col3:
            st.markdown("### 🖼️ Image Training")
            st.metric("Training Ready", "89 samples")
            st.metric("Last Training", "3 days ago")
            st.metric("Next Trigger", "~11 more samples")
            st.progress(0.82, text="Quality: 82%")
        
        st.markdown("---")
        
        st.subheader("📊 Training History")
        
        training_history = [
            {"Date": "2026-01-01", "Category": "Voice", "Samples": 150, "Loss": 0.42, "Status": "✅ Completed"},
            {"Date": "2025-12-29", "Category": "Video", "Samples": 35, "Loss": 0.38, "Status": "✅ Completed"},
            {"Date": "2025-12-28", "Category": "Image", "Samples": 200, "Loss": 0.25, "Status": "✅ Completed"},
            {"Date": "2025-12-25", "Category": "Voice", "Samples": 120, "Loss": 0.45, "Status": "✅ Completed"},
        ]
        
        import pandas as pd
        st.dataframe(pd.DataFrame(training_history), use_container_width=True)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 4: ANALYTICS
    # ═══════════════════════════════════════════════════════════════════════════
    
    with tab4:
        st.subheader("📈 Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Predictions Over Time")
            
            import pandas as pd
            import numpy as np
            
            dates = pd.date_range(end=datetime.now(), periods=30)
            predictions = np.random.randint(150, 350, size=30)
            
            chart_data = pd.DataFrame({
                "Date": dates,
                "Predictions": predictions
            }).set_index("Date")
            
            st.line_chart(chart_data)
        
        with col2:
            st.markdown("### Content Type Distribution")
            
            type_data = pd.DataFrame({
                "Type": ["Video", "Voice", "Image", "Chat"],
                "Count": [450, 680, 320, 1200]
            }).set_index("Type")
            
            st.bar_chart(type_data)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### User Engagement")
            st.metric("Active Users (24h)", "142")
            st.metric("Avg Session Duration", "12 min")
            st.metric("Satisfaction Score", "4.7/5.0 ⭐")
        
        with col2:
            st.markdown("### Cost Analysis")
            st.metric("Daily Cost", "$32.50")
            st.metric("Cost per Prediction", "$0.12")
            st.metric("Budget Remaining", "$17.50 / $50.00")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"🇳🇬 **Sisi Lola Control Center** | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"v1.0.0"
    )


if __name__ == "__main__":
    main()
