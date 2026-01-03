#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
💬 CHAT WITH SISI LOLA
═══════════════════════════════════════════════════════════════════════════════
Interactive chat interface with voice and video responses.
"""

import os
import sys
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

st.set_page_config(page_title="Chat | Sisi Lola", page_icon="💬", layout="wide")


def main():
    st.title("💬 Chat with Sisi Lola")
    st.markdown("**Your Nigerian AI Assistant - Text, Voice & Video**")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How you dey? I be Sisi Lola, your Nigerian AI assistant! Ask me anything o! 🇳🇬"}
        ]
    
    if "response_mode" not in st.session_state:
        st.session_state.response_mode = "text"
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Chat Settings")
        
        st.markdown("### Response Mode")
        response_mode = st.radio(
            "How should Sisi Lola respond?",
            ["Text Only", "Text + Voice", "Text + Video"],
            index=0
        )
        st.session_state.response_mode = response_mode.lower().replace(" ", "_")
        
        st.markdown("---")
        
        st.markdown("### Dialect Settings")
        dialect = st.selectbox(
            "Preferred Dialect",
            ["Pidgin English", "Standard English", "Yoruba-Mix", "Hausa-Mix", "Igbo-Mix"]
        )
        
        dialect_intensity = st.slider("Dialect Intensity", 0, 100, 70)
        
        st.markdown("---")
        
        st.markdown("### Voice Settings")
        voice_speed = st.slider("Voice Speed", 0.5, 2.0, 1.0)
        voice_pitch = st.slider("Voice Pitch", 0.5, 2.0, 1.0)
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "How you dey? Chat don reset! Wetin you wan discuss? 🇳🇬"}
            ]
            st.rerun()
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show media if available
                if "audio" in message:
                    st.audio(message["audio"])
                if "video" in message:
                    st.video(message["video"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Sisi Lola dey think..."):
                # Simulate response based on mode
                response = generate_response(prompt, st.session_state.response_mode)
                
                st.markdown(response["text"])
                
                if "audio" in response:
                    st.audio(response["audio"])
                
                if "video" in response:
                    st.video(response["video"])
        
        # Add assistant message
        message_data = {"role": "assistant", "content": response["text"]}
        if "audio" in response:
            message_data["audio"] = response["audio"]
        if "video" in response:
            message_data["video"] = response["video"]
        
        st.session_state.messages.append(message_data)
    
    # Voice input option
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🎤 Voice Input")
        audio_file = st.file_uploader("Upload voice message", type=["wav", "mp3", "m4a"], label_visibility="collapsed")
        
        if audio_file:
            st.audio(audio_file)
            if st.button("🎤 Send Voice Message"):
                st.info("Would transcribe and process voice message")
    
    with col2:
        st.markdown("### Quick Prompts")
        
        quick_prompts = [
            "How you dey?",
            "Tell me a joke",
            "What's happening in Lagos?",
            "Explain AI to me"
        ]
        
        for qp in quick_prompts:
            if st.button(qp, key=f"qp_{qp}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": qp})
                st.rerun()


def generate_response(prompt: str, mode: str) -> dict:
    """
    Generate a response from Sisi Lola.
    
    In production, this would call the actual Replicate API.
    """
    # Sample responses in Pidgin
    responses = {
        "how you dey": "I dey fine o! Thank you for asking. How your side dey? Wetin I fit help you with today? 🇳🇬",
        "tell me a joke": "Okay o, hear this one: Why Naija man no dey fear? Because e don already see traffic for Lagos! 😂 You wan hear another one?",
        "default": f"Ah, I hear you o! You talk about '{prompt}'. Make I think small... Na interesting topic be that! You wan know more?"
    }
    
    # Match response
    prompt_lower = prompt.lower()
    
    response_text = responses.get(prompt_lower, responses["default"])
    
    result = {"text": response_text}
    
    # Add media based on mode
    if "voice" in mode:
        # Would generate voice via MiniMax
        result["audio"] = None  # Placeholder
    
    if "video" in mode:
        # Would generate video via Omni-Human
        result["video"] = None  # Placeholder
    
    return result


if __name__ == "__main__":
    main()
