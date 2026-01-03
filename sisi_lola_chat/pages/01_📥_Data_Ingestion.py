#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
📥 DATA INGESTION DASHBOARD
═══════════════════════════════════════════════════════════════════════════════
Monitor and manage the YouTube data ingestion pipeline.
"""

import os
import sys
import json
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

st.set_page_config(page_title="Data Ingestion | Sisi Lola", page_icon="📥", layout="wide")


def main():
    st.title("📥 Data Ingestion Pipeline")
    st.markdown("**YouTube Content Scraping & Processing**")
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Quick Actions")
        
        if st.button("🔄 Start Ingestion", use_container_width=True):
            st.info("Would trigger ingestion pipeline")
        
        if st.button("⏹️ Stop Ingestion", use_container_width=True):
            st.warning("Would stop ingestion")
        
        st.markdown("---")
        
        st.markdown("### 📊 Current Stats")
        st.metric("Videos Ingested", "1,234")
        st.metric("Audio Extracted", "1,180")
        st.metric("Transcripts", "1,150")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🔍 Content Discovery",
        "📁 Ingested Data",
        "⚙️ Settings"
    ])
    
    with tab1:
        st.subheader("Pipeline Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Videos", "1,234", "+45 today")
        with col2:
            st.metric("Nigerian Content", "892", "+38 today")
        with col3:
            st.metric("Processing Queue", "23")
        with col4:
            st.metric("Failed", "12", "-3 from yesterday")
        
        st.markdown("---")
        
        st.subheader("Recent Ingestion")
        
        recent_data = [
            {"Video": "Lagos Tech Talk EP 15", "Channel": "TechNaija", "Status": "✅ Complete", "Time": "5 min ago"},
            {"Video": "How to Cook Jollof Rice", "Channel": "Naija Kitchen", "Status": "✅ Complete", "Time": "12 min ago"},
            {"Video": "Pidgin Comedy Skit", "Channel": "NaijaComedy", "Status": "🔄 Processing", "Time": "15 min ago"},
            {"Video": "Afrobeats Mix 2026", "Channel": "AfroBeatsFM", "Status": "✅ Complete", "Time": "22 min ago"},
        ]
        
        st.dataframe(pd.DataFrame(recent_data), use_container_width=True)
    
    with tab2:
        st.subheader("🔍 Content Discovery")
        
        st.markdown("### Nigerian Content Queries")
        
        queries = [
            "Nigerian tech reviews", "Lagos lifestyle vlog", "Pidgin comedy skits",
            "Yoruba movie trailers", "Hausa music videos", "Igbo culture",
            "Naija news updates", "African business tips"
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Active Queries:**")
            for q in queries[:4]:
                st.checkbox(q, value=True)
        
        with col2:
            st.markdown("**Inactive Queries:**")
            for q in queries[4:]:
                st.checkbox(q, value=False)
        
        st.markdown("---")
        
        new_query = st.text_input("Add New Query")
        if st.button("➕ Add Query"):
            st.success(f"Added query: {new_query}")
    
    with tab3:
        st.subheader("📁 Ingested Content")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            content_type = st.selectbox("Content Type", ["All", "Video", "Audio", "Transcript"])
        with col2:
            language = st.selectbox("Language", ["All", "English", "Pidgin", "Yoruba", "Hausa", "Igbo"])
        with col3:
            quality = st.selectbox("Quality", ["All", "High", "Medium", "Low"])
        
        # Sample data
        ingested = [
            {"ID": "vid_001", "Title": "Lagos Tech Talk", "Type": "Video", "Language": "Pidgin", "Quality": "High", "Size": "150 MB"},
            {"ID": "vid_002", "Title": "Jollof Recipe", "Type": "Video", "Language": "English", "Quality": "High", "Size": "85 MB"},
            {"ID": "aud_003", "Title": "Pidgin Podcast", "Type": "Audio", "Language": "Pidgin", "Quality": "Medium", "Size": "25 MB"},
        ]
        
        st.dataframe(pd.DataFrame(ingested), use_container_width=True)
    
    with tab4:
        st.subheader("⚙️ Pipeline Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Download Settings")
            st.number_input("Max concurrent downloads", value=3, min_value=1, max_value=10)
            st.number_input("Rate limit (requests/min)", value=30, min_value=10, max_value=100)
            st.selectbox("Video quality", ["1080p", "720p", "480p", "360p"])
        
        with col2:
            st.markdown("### Processing Settings")
            st.checkbox("Extract audio", value=True)
            st.checkbox("Generate transcript", value=True)
            st.checkbox("Detect language", value=True)
            st.checkbox("Extract key frames", value=False)
        
        if st.button("💾 Save Settings", type="primary"):
            st.success("Settings saved!")


if __name__ == "__main__":
    main()
