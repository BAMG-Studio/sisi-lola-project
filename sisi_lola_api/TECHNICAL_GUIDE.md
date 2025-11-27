# Sisi Lola Technical Implementation Guide

## 1. Overview (The "Layman's" View)

Think of this system as building a **Digital Human**. To make her believable, she needs three main components working together:

1.  **The DNA (Configuration)**: This is her "soul" and "body". It's a set of strict rules that say "She always looks like *this*" and "She always acts like *that*". We hardcoded this so she doesn't have an identity crisis.
2.  **The Brain (API)**: This is the software we just built. It acts as a traffic controller. When you want an image, a video, or a chat response, you ask the Brain. The Brain checks the DNA rules first, then sends the order to the AI tools.
3.  **The Tools (External APIs)**: These are the muscles.
    *   **ChatGPT**: Her voice and wit.
    *   **Perplexity**: Her knowledge of current events.
    *   **Midjourney/DALL-E**: Her photographer.
    *   **ElevenLabs**: Her vocal cords.

---

## 2. Where We Use the APIs

### **ChatGPT API (OpenAI)**
*   **Role**: The Conversational Engine.
*   **Where it lives**: `app/routers/chat.py`
*   **Why we need it**: Sisi Lola needs to talk to users. We don't just want generic robot answers; we want *her* personality.
*   **How it works**: We send the user's message + `SisiLolaDNA.SYSTEM_PERSONA` (the instructions to "be sassy, Nigerian, and tech-savvy") to ChatGPT. It returns a response in her voice.

### **Perplexity API**
*   **Role**: The "Brain" and "Visual Director".
*   **Where it lives**: `app/routers/agent.py` and `app/utils/perplexity.py`
*   **Why we need it**: 
    1.  **Research**: Fetches real-time data for the Chat Agent.
    2.  **Visual DNA Enforcement**: Generates all image/video prompts. It takes a simple scenario and expands it into a detailed, photorealistic prompt that strictly adheres to Sisi Lola's visual DNA (lighting, texture, outfit).
*   **How it works**: 
    *   **For Chat**: Before answering, the system asks Perplexity to "Search the web for Lagos Tech Summit". Perplexity returns the facts. Then, we feed those facts to ChatGPT and say "Rewrite this as Sisi Lola".
    *   **For Images**: The system sends your simple scenario to Perplexity with strict instructions to act as Sisi Lola's "Visual Director". It returns a highly detailed prompt optimized for KlingAI/DALL-E.

---

## 3. Technical Architecture (The "Under the Hood" View)

### **File Structure**
*   `app/main.py`: The front door. All requests come here first.
*   `app/config.py`: The **Source of Truth**. Contains the `SisiLolaDNA` class. **Do not edit this unless you want to change who she is fundamentally.**
*   `app/routers/`: Specialized departments.
    *   `images.py`: Handles image generation requests. Injects visual prompts automatically.
    *   `chat.py`: Handles conversation. Injects personality prompts automatically.
    *   `agent.py`: Handles research and complex tasks.

### **The "DNA Injection" Pattern**
This is the secret sauce of this project.
Instead of typing "A picture of a black woman hosting a show" into Midjourney every time (which yields inconsistent results), the system does this:

1.  **You send**: "Sisi at a market."
2.  **System reads DNA**: Retrieves `VISUAL_PROMPT_CORE` ("Voluptuous, mature, Yoruba...") + `OUTFIT_DNA`.
3.  **System combines**: "Portrait of Sisi Lola... [DNA Description]... She is at a market... Wearing [Outfit DNA]."
4.  **System sends to AI**: The AI receives a highly specific, consistent prompt.

---

## 4. Next Steps Roadmap

### **Phase 1: Brain Activation (Current)**
- [x] Build API Structure.
- [x] Hardcode DNA.
- [ ] **Action**: Add your API Keys to `.env` file (OpenAI, Perplexity).
- [ ] **Action**: Test the Chat endpoint to hear her voice.

### **Phase 2: Asset Factory**
- [ ] **Action**: Use the `images.py` router to generate the 200+ static assets defined in your CSV manifest.
- [ ] **Action**: Validate that the "DNA" images (`sisi_dna_v1.png`) are influencing the output correctly.

### **Phase 3: Voice & Video**
- [ ] **Action**: Clone her voice in ElevenLabs.
- [ ] **Action**: Connect the Audio Router to ElevenLabs API.
- [ ] **Action**: Generate video scripts using the Chat Router (with Perplexity for trending topics).
