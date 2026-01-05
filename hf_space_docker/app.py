import gradio as gr

def chat(message, history):
    responses = {
        "hello": "E kaabo! Welcome my friend! How you dey today? 🇳🇬",
        "hi": "Hey! Na wa o, good to see you! Wetin dey happen?",
        "how are you": "I dey fine well well! The vibes dey sweet today. How body?",
        "how you dey": "I dey kampe! Body dey inside cloth. You nko?",
        "jollof": "Ah! Jollof rice! Nigerian jollof sweet pass any other one o! No debate! 🍚",
        "music": "Afrobeats don scatter everywhere! Burna Boy, Wizkid, Davido - we dey run things! 🎵",
        "lagos": "Lagos! The city wey never sleep! Hustle dey, but the vibes dey too! Eko for show! 🌆",
        "food": "Naija food sweet die! Jollof, suya, egusi, pounded yam, pepper soup... my mouth dey water! 🍲",
        "yoruba": "Yoruba sweet o! Bawo ni? E ku irole! Omo Naija represent! 🇳🇬",
        "pidgin": "Na we be the realest! Pidgin English na our own language! How far nau?",
    }
    
    msg_lower = message.lower()
    for key, response in responses.items():
        if key in msg_lower:
            return response
    
    return f"""E kaabo! 🇳🇬

You talk say: "{message}"

I be Sisi Lola, your Nigerian AI sister!

Ask me about:
• Nigerian food (jollof, suya, egusi)
• Afrobeats music
• Lagos life
• Yoruba greetings
• Pidgin English

E go be alright! ✨"""

with gr.Blocks(title="Sisi Lola AI") as demo:
    gr.HTML("""
    <div style="text-align:center;padding:20px;background:linear-gradient(90deg,#008751,#fff,#008751);border-radius:10px;margin-bottom:20px;">
        <h1>🇳🇬 Sisi Lola AI</h1>
        <p>Nigeria's Virtual Content Creator</p>
    </div>
    """)
    
    gr.ChatInterface(
        fn=chat,
        examples=["How you dey?", "Tell me about jollof rice", "What is Lagos like?", "Recommend Afrobeats music"],
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
