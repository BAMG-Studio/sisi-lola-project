#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
📊 ANALYTICS DASHBOARD
═══════════════════════════════════════════════════════════════════════════════
Comprehensive analytics for Sisi Lola system performance.
"""

import os
import sys
import json
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

st.set_page_config(page_title="Analytics | Sisi Lola", page_icon="📊", layout="wide")


def generate_mock_data():
    """Generate mock analytics data."""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    return {
        "daily_requests": pd.DataFrame({
            "Date": dates,
            "Requests": [random.randint(500, 2000) for _ in range(30)],
            "Success": [random.randint(450, 1900) for _ in range(30)]
        }),
        "dialect_usage": {
            "Pidgin": 45,
            "Yoruba-Mix": 20,
            "Standard English": 15,
            "Hausa-Mix": 12,
            "Igbo-Mix": 8
        },
        "content_types": {
            "Text Chat": 50,
            "Voice Response": 30,
            "Video Generation": 15,
            "Image Generation": 5
        }
    }


def main():
    st.title("📊 Analytics Dashboard")
    st.markdown("**System Performance & Usage Insights**")
    
    data = generate_mock_data()
    
    # Sidebar
    with st.sidebar:
        st.header("📅 Date Range")
        
        date_range = st.selectbox(
            "Select Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"]
        )
        
        if date_range == "Custom":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        st.markdown("---")
        
        st.markdown("### 📥 Export")
        
        if st.button("📊 Export CSV", use_container_width=True):
            st.info("Would export data to CSV")
        
        if st.button("📄 Export PDF Report", use_container_width=True):
            st.info("Would generate PDF report")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview",
        "💬 Usage Analytics",
        "🎯 Content Performance",
        "💰 Cost Analysis"
    ])
    
    with tab1:
        st.subheader("System Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Requests", "45,234", "+12.5%")
        with col2:
            st.metric("Success Rate", "97.8%", "+0.5%")
        with col3:
            st.metric("Avg. Latency", "1.2s", "-0.3s")
        with col4:
            st.metric("Active Users", "1,234", "+89")
        
        st.markdown("---")
        
        # Daily requests chart
        st.subheader("Daily Requests")
        st.line_chart(data["daily_requests"].set_index("Date")["Requests"])
        
        # System health
        st.subheader("System Health")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🧠 Brain (Language)")
            st.progress(95, text="Healthy: 95%")
            st.caption("Avg. response time: 0.8s")
        
        with col2:
            st.markdown("### 👁️ Eyes (Vision)")
            st.progress(92, text="Healthy: 92%")
            st.caption("Avg. generation time: 3.5s")
        
        with col3:
            st.markdown("### 🗣️ Voice (Audio)")
            st.progress(98, text="Healthy: 98%")
            st.caption("Avg. synthesis time: 1.2s")
    
    with tab2:
        st.subheader("Usage Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Dialect Usage")
            
            dialect_df = pd.DataFrame({
                "Dialect": list(data["dialect_usage"].keys()),
                "Usage %": list(data["dialect_usage"].values())
            })
            
            st.bar_chart(dialect_df.set_index("Dialect"))
        
        with col2:
            st.markdown("### Content Types")
            
            content_df = pd.DataFrame({
                "Type": list(data["content_types"].keys()),
                "Usage %": list(data["content_types"].values())
            })
            
            st.bar_chart(content_df.set_index("Type"))
        
        st.markdown("---")
        
        st.subheader("User Engagement")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg. Session Duration", "8.5 min")
        with col2:
            st.metric("Messages per Session", "12.3")
        with col3:
            st.metric("Return Rate", "68%")
        with col4:
            st.metric("Satisfaction Score", "4.6/5")
        
        # Peak usage times
        st.subheader("Peak Usage Times")
        
        hours = list(range(24))
        usage = [random.randint(50, 500) for _ in range(24)]
        
        peak_df = pd.DataFrame({
            "Hour": hours,
            "Requests": usage
        })
        
        st.bar_chart(peak_df.set_index("Hour"))
    
    with tab3:
        st.subheader("Content Performance")
        
        st.markdown("### Top Performing Content")
        
        top_content = [
            {"Content": "Lagos Lifestyle Reel", "Views": "12,345", "Engagement": "8.5%", "Shares": "234"},
            {"Content": "Pidgin Comedy Skit", "Views": "10,890", "Engagement": "9.2%", "Shares": "345"},
            {"Content": "Tech Review Video", "Views": "8,456", "Engagement": "7.8%", "Shares": "156"},
            {"Content": "Cooking Tutorial", "Views": "7,234", "Engagement": "8.1%", "Shares": "189"},
        ]
        
        st.dataframe(pd.DataFrame(top_content), use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Nigerian Content Bonus Impact")
            
            bonus_data = pd.DataFrame({
                "Category": ["With Bonus", "Without Bonus"],
                "Training Weight": [1.5, 1.0]
            })
            
            st.bar_chart(bonus_data.set_index("Category"))
            
            st.info("Nigerian content receives **1.5x** training weight bonus")
        
        with col2:
            st.markdown("### Content Quality Distribution")
            
            quality_data = pd.DataFrame({
                "Quality": ["High", "Medium", "Low"],
                "Percentage": [65, 28, 7]
            })
            
            st.bar_chart(quality_data.set_index("Quality"))
    
    with tab4:
        st.subheader("Cost Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Today's Cost", "$12.50")
        with col2:
            st.metric("This Week", "$78.25")
        with col3:
            st.metric("This Month", "$245.80")
        with col4:
            st.metric("Avg. Cost/Request", "$0.008")
        
        st.markdown("---")
        
        st.subheader("Cost Breakdown by Service")
        
        cost_breakdown = pd.DataFrame({
            "Service": ["Replicate (Brain)", "Replicate (Voice)", "Replicate (Video)", "Modal (Training)", "Storage"],
            "Cost": [45.50, 38.20, 125.60, 32.50, 4.00]
        })
        
        st.bar_chart(cost_breakdown.set_index("Service"))
        
        st.markdown("---")
        
        st.subheader("Cost Trends")
        
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        costs = [random.uniform(5, 20) for _ in range(30)]
        
        cost_trend = pd.DataFrame({
            "Date": dates,
            "Daily Cost ($)": costs
        })
        
        st.line_chart(cost_trend.set_index("Date"))
        
        # Budget alerts
        st.subheader("Budget Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Daily Budget")
            st.progress(25, text="$12.50 / $50.00 (25%)")
        
        with col2:
            st.markdown("### Monthly Budget")
            st.progress(49, text="$245.80 / $500.00 (49%)")


if __name__ == "__main__":
    main()
