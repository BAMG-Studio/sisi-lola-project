#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🇳🇬 SISI LOLA - HuggingFace Spaces Demo
═══════════════════════════════════════════════════════════════════════════════
Live demo of Sisi Lola AI - Nigeria's Virtual Content Creator

Features:
- Chat with Sisi Lola in 5 Nigerian languages
- Voice synthesis with XTTS
- Content generation preview
- Real-time Nigerian cultural AI

Deployed on HuggingFace Spaces with ZeroGPU (H200)
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import gradio as gr
import requests
from typing import Optional, List, Tuple
import json

# HuggingFace Inference API
HF_TOKEN = os.environ.get("HF_TOKEN", "")
REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

# Model endpoints
BRAIN_MODEL = "sisilolalive/sisi-lola-brain-mistral"
VOICE_MODEL = "coqui/XTTS-v2"

# Sisi Lola System Prompt
SISI_LOLA_PROMPT = """You are Sisi Lola, a vibrant Nigerian AI content creator and virtual host. 

Key traits:
- Fluent in English, Nigerian Pidgin, Yoruba, Hausa, and Igbo
- Warm, witty, and culturally aware
- Expert in Nigerian cuisine, fashion, music, and culture
- Friendly and engaging personality
- Uses Nigerian expressions naturally

Character seed: 45822

When speaking Pidgin, use authentic expressions like:
- "How you dey?" (How are you?)
- "Na wa o!" (Expression of surprise)
- "Wetin dey happen?" (What's happening?)
- "E go be alright" (It will be alright)

Always maintain your Nigerian identity while being helpful and engaging."""


# ═══════════════════════════════════════════════════════════════════════════════
# INFERENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def chat_with_sisi(
    message: str,
    history: List[Tuple[str, str]],
    language: str = "English",
    temperature: float = 0.7
) -> str:
    """Chat with Sisi Lola using HuggingFace Inference API."""
    
    # Language prompts
    lang_prompts = {
        "English": "Respond in English.",
        "Nigerian Pidgin": "Respond in Nigerian Pidgin English.",
        "Yoruba": "Respond in Yoruba language.",
        "Hausa": "Respond in Hausa language.",
        "Igbo": "Respond in Igbo language."
    }
    
    # Build conversation
    system = f"{SISI_LOLA_PROMPT}\n\n{lang_prompts.get(language, '')}"
    
    messages = [{"role": "system", "content": system}]
    
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    
    messages.append({"role": "user", "content": message})
    
    # Try HuggingFace Inference API first
    try:
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=HF_TOKEN)
        
        # Use a capable model
        response = client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=messages,
            max_tokens=512,
            temperature=temperature
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Fallback to simple response
        return f"""Ah, my friend! 🇳🇬

Thank you for reaching out! I am Sisi Lola, your Nigerian AI companion.

You said: "{message}"

Right now, my main brain is resting, but I'm still here to chat!
Na wa o - technology sometimes have wahala, but we dey manage! 😄

Try asking me about:
- Nigerian cuisine (jollof rice, suya, egusi)
- Nigerian fashion (ankara, aso-oke)
- Nigerian music and culture

E go be alright! 🇳🇬✨

(Note: Full AI responses coming soon when the model loads!)
"""


def generate_voice(text: str, language: str = "en") -> Optional[str]:
    """Generate voice using XTTS."""
    
    # Language codes
    lang_codes = {
        "English": "en",
        "Nigerian Pidgin": "en",  # Use English voice for Pidgin
        "Yoruba": "en",
        "Hausa": "en",
        "Igbo": "en"
    }
    
    try:
        # For now, return placeholder
        # In production, this uses Replicate XTTS or HF Inference
        return None
    except Exception as e:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# GRADIO INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

# Custom CSS for Nigerian theme
custom_css = """
.gradio-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.main-header {
    background: linear-gradient(90deg, #008751 0%, #ffffff 50%, #008751 100%);
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
}

footer {
    display: none !important;
}
"""

# Create the interface
with gr.Blocks(css=custom_css, title="Sisi Lola AI 🇳🇬") as demo:
    
    # Header
    gr.HTML("""
    <div class="main-header">
        <h1>🇳🇬 Sisi Lola AI</h1>
        <p>Nigeria's Virtual Content Creator & Cultural Ambassador</p>
        <p><em>Character Seed: 45822</em></p>
    </div>
    """)
    
    with gr.Tabs():
        # Tab 1: Chat
        with gr.TabItem("💬 Chat with Sisi Lola"):
            with gr.Row():
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="Sisi Lola",
                        height=500,
                        avatar_images=(None, "https://api.dicebear.com/7.x/personas/svg?seed=45822")
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your Message",
                            placeholder="Type your message here... (e.g., 'How you dey?' or 'Tell me about jollof rice')",
                            scale=4
                        )
                        submit = gr.Button("Send 🚀", variant="primary", scale=1)
                
                with gr.Column(scale=1):
                    language = gr.Dropdown(
                        choices=["English", "Nigerian Pidgin", "Yoruba", "Hausa", "Igbo"],
                        value="English",
                        label="🌍 Language"
                    )
                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=0.7,
                        step=0.1,
                        label="🌡️ Creativity"
                    )
                    
                    gr.Markdown("""
                    ### 🇳🇬 Quick Prompts
                    - "How you dey?"
                    - "Tell me about Nigerian food"
                    - "Teach me Yoruba greetings"
                    - "What's trending in Lagos?"
                    - "Recommend Afrobeats music"
                    """)
                    
                    clear = gr.Button("🗑️ Clear Chat")
            
            # Event handlers
            def respond(message, chat_history, lang, temp):
                if not message.strip():
                    return "", chat_history
                
                bot_message = chat_with_sisi(message, chat_history, lang, temp)
                chat_history.append((message, bot_message))
                return "", chat_history
            
            submit.click(respond, [msg, chatbot, language, temperature], [msg, chatbot])
            msg.submit(respond, [msg, chatbot, language, temperature], [msg, chatbot])
            clear.click(lambda: [], None, chatbot)
        
        # Tab 2: About
        with gr.TabItem("ℹ️ About Sisi Lola"):
            gr.Markdown("""
            ## 🇳🇬 About Sisi Lola
            
            **Sisi Lola** is an AI-powered virtual content creator representing Nigerian culture and creativity.
            
            ### Features
            - 🗣️ **Multilingual**: Speaks English, Nigerian Pidgin, Yoruba, Hausa, and Igbo
            - 🎤 **Voice Synthesis**: Natural Nigerian voice using XTTS technology
            - 🎬 **Video Generation**: AI-powered lip-sync video content
            - 📱 **Social Media**: Automated Instagram posting
            - 🧠 **Cultural AI**: Trained on Nigerian content and expressions
            
            ### Technology Stack
            - **Brain**: Mistral-7B fine-tuned on Nigerian conversations
            - **Voice**: Coqui XTTS-v2 with Nigerian speaker reference
            - **Video**: Omni-Human for realistic lip-sync
            - **Hosting**: HuggingFace Spaces with ZeroGPU
            
            ### Character Seed
            Sisi Lola's consistent visual identity is generated using seed: **45822**
            
            ---
            
            *Built with ❤️ for Nigeria by BAMG Studio*
            
            🔗 [GitHub](https://github.com/BAMG-Studio/sisi-lola-project) | 
            🤗 [HuggingFace](https://huggingface.co/sisilolalive) |
            📺 [Instagram](https://instagram.com/sisilolalive)
            """)
        
        # Tab 3: Content Preview
        with gr.TabItem("🎬 Content Preview"):
            gr.Markdown("""
            ## 🎬 Content Generation Preview
            
            *Coming Soon: Generate Nigerian content with Sisi Lola!*
            
            ### Planned Features:
            - 📸 Image generation with Nigerian themes
            - 🎤 Voice clips in multiple languages
            - 🎬 Short video content
            - 📱 Direct Instagram posting
            """)
            
            with gr.Row():
                content_prompt = gr.Textbox(
                    label="Content Prompt",
                    placeholder="Describe the content you want to create..."
                )
                content_type = gr.Dropdown(
                    choices=["Image", "Voice Clip", "Video"],
                    value="Image",
                    label="Content Type"
                )
            
            generate_btn = gr.Button("Generate Content 🎨", variant="primary")
            output_preview = gr.Markdown("*Content preview will appear here*")

# Launch
if __name__ == "__main__":
    demo.launch()
