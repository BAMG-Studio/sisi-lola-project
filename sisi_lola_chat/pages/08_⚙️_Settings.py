#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
⚙️ SETTINGS PAGE
═══════════════════════════════════════════════════════════════════════════════
System configuration and settings management.
"""

import os
import sys
import json
import streamlit as st
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

st.set_page_config(page_title="Settings | Sisi Lola", page_icon="⚙️", layout="wide")


def main():
    st.title("⚙️ System Settings")
    st.markdown("**Configure Sisi Lola System**")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔑 API Keys",
        "🎨 Character",
        "🧠 Models",
        "💰 Budgets",
        "🔧 Advanced"
    ])
    
    with tab1:
        st.subheader("🔑 API Configuration")
        
        st.markdown("### Replicate")
        replicate_key = st.text_input("Replicate API Token", type="password", value="****")
        replicate_status = st.checkbox("Replicate Connected", value=True, disabled=True)
        
        st.markdown("---")
        
        st.markdown("### Modal")
        modal_token = st.text_input("Modal Token", type="password", value="****")
        modal_status = st.checkbox("Modal Connected", value=True, disabled=True)
        
        st.markdown("---")
        
        st.markdown("### Cohere")
        cohere_key = st.text_input("Cohere API Key", type="password", value="****")
        cohere_status = st.checkbox("Cohere Connected", value=True, disabled=True)
        
        st.markdown("---")
        
        st.markdown("### Azure")
        
        col1, col2 = st.columns(2)
        
        with col1:
            azure_key = st.text_input("Azure Speech Key", type="password", value="****")
        with col2:
            azure_region = st.text_input("Azure Region", value="eastus")
        
        azure_vi_key = st.text_input("Azure Video Indexer Key", type="password", value="****")
        
        if st.button("💾 Save API Keys", type="primary"):
            st.success("API keys saved securely!")
    
    with tab2:
        st.subheader("🎨 Sisi Lola Character Settings")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Identity")
            
            st.text_input("Character Name", value="Sisi Lola")
            st.number_input("Character Seed (for consistency)", value=45822, disabled=True)
            
            st.text_area(
                "Character Description",
                value="Beautiful Nigerian woman with warm smile, elegant Ankara style, professional and friendly demeanor.",
                height=100
            )
            
            st.markdown("### Voice")
            
            st.selectbox("Default Voice Style", ["Warm & Friendly", "Professional", "Energetic", "Calm"])
            st.selectbox("Default Dialect", ["Pidgin English", "Standard English", "Yoruba-Mix"])
            st.slider("Default Dialect Intensity", 0, 100, 70)
        
        with col2:
            st.markdown("### Preview")
            st.image("https://via.placeholder.com/200x200.png?text=Sisi+Lola", use_container_width=True)
            st.caption("Seed: 45822")
        
        st.markdown("---")
        
        st.markdown("### Visual Style")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.selectbox("Default Outfit", ["Ankara", "Business", "Casual", "Traditional"])
        with col2:
            st.selectbox("Default Background", ["Office", "Living Room", "Outdoor", "Studio"])
        with col3:
            st.selectbox("Default Lighting", ["Natural", "Studio", "Warm", "Cool"])
        
        if st.button("💾 Save Character Settings", type="primary"):
            st.success("Character settings saved!")
    
    with tab3:
        st.subheader("🧠 Model Configuration")
        
        st.markdown("### Brain (Language)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Brain Model", [
                "deepseek-ai/deepseek-r1",
                "meta/llama-3.3-70b-instruct",
                "anthropic/claude-3-sonnet"
            ])
        with col2:
            st.number_input("Max Tokens", value=2048, min_value=256, max_value=8192)
        
        st.slider("Temperature", 0.0, 2.0, 0.7)
        
        st.markdown("---")
        
        st.markdown("### Voice (Audio)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Voice Model", [
                "minimax/speech-01-turbo",
                "azure-speech",
                "custom-voice-lora"
            ])
        with col2:
            st.selectbox("Voice ID", ["Sisi_Lola_v3", "Sisi_Lola_v2", "default"])
        
        st.markdown("---")
        
        st.markdown("### Eyes (Vision)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Image Model", [
                "seedream-3",
                "flux-pro",
                "stable-diffusion-xl"
            ])
        with col2:
            st.selectbox("Video Model", [
                "omnihuman-i2v-01",
                "liveportrait",
                "sadtalker"
            ])
        
        if st.button("💾 Save Model Settings", type="primary"):
            st.success("Model settings saved!")
    
    with tab4:
        st.subheader("💰 Budget & Cost Settings")
        
        st.markdown("### Daily Limits")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.number_input("Daily Budget ($)", value=50, min_value=10, max_value=500)
        with col2:
            st.number_input("Weekly Budget ($)", value=200, min_value=50, max_value=2000)
        with col3:
            st.number_input("Monthly Budget ($)", value=500, min_value=100, max_value=5000)
        
        st.markdown("---")
        
        st.markdown("### Request Limits")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Max requests/minute", value=60, min_value=10, max_value=200)
            st.number_input("Max concurrent requests", value=10, min_value=1, max_value=50)
        
        with col2:
            st.number_input("Max video generations/day", value=50, min_value=10, max_value=500)
            st.number_input("Max training jobs/day", value=5, min_value=1, max_value=20)
        
        st.markdown("---")
        
        st.markdown("### Alerts")
        
        st.checkbox("Email when 80% budget reached", value=True)
        st.checkbox("Email when budget exceeded", value=True)
        st.checkbox("Daily cost summary email", value=False)
        
        st.text_input("Alert Email", value="admin@example.com")
        
        if st.button("💾 Save Budget Settings", type="primary"):
            st.success("Budget settings saved!")
    
    with tab5:
        st.subheader("🔧 Advanced Settings")
        
        st.markdown("### Data Retention")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Keep feedback data (days)", value=90, min_value=7, max_value=365)
            st.number_input("Keep training logs (days)", value=30, min_value=7, max_value=180)
        
        with col2:
            st.number_input("Keep generated content (days)", value=30, min_value=7, max_value=180)
            st.number_input("Keep chat history (days)", value=7, min_value=1, max_value=30)
        
        st.markdown("---")
        
        st.markdown("### Training Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Min samples for trigger", value=1000, min_value=100, max_value=10000)
            st.number_input("Checkpoint interval", value=500, min_value=100, max_value=2000)
        
        with col2:
            st.number_input("Quality threshold", value=70, min_value=50, max_value=100)
            st.number_input("Nigerian content bonus", value=150, min_value=100, max_value=200)
        
        st.markdown("---")
        
        st.markdown("### System Maintenance")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.info("Would clear system cache")
        
        with col2:
            if st.button("🔄 Restart Services", use_container_width=True):
                st.warning("Would restart all services")
        
        with col3:
            if st.button("📊 Export Config", use_container_width=True):
                st.info("Would export configuration")
        
        st.markdown("---")
        
        st.markdown("### Danger Zone")
        
        st.error("⚠️ These actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Reset All Settings", use_container_width=True):
                st.error("Would reset all settings to default")
        
        with col2:
            if st.button("💣 Delete All Data", use_container_width=True):
                st.error("Would delete all generated data")


if __name__ == "__main__":
    main()
