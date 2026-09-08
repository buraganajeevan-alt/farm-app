"""agri_chat.py — Agri AI assistant (merged from Krishi Sahayak / LLM_Agri_Bot).
Text + voice + image advisory using the Groq SDK. Requires GROQ_API_KEY in .env.
Gracefully degrades with local agricultural knowledge if the key is missing.
System prompt reused (plain-text, Indian-farmer focused) from the source bot.
"""
import os
import re
import base64
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """<role>
You are AgriAI — a senior AI Agronomist and Agricultural Advisor specialized in Indian agriculture.
Your role is to provide precise, scientific, yet practical and easy-to-understand advice for farmers on crop selection, disease diagnosis, pest control, soil health, fertilizer dosage, and government schemes.
</role>

<guidelines>
1. TONE & STYLE: Professional, respectful, clear, and actionable.
2. FORMATTING RULES:
   - Output clean text with clear spacing and bullet points using dashes (-).
   - Do NOT use heavy markdown headers or code blocks.
   - Use bold highlights naturally for key action items or product names.
3. RESPONSE STRUCTURE:
   - Direct Diagnosis / Executive Summary
   - Step-by-Step Action Plan (numbered or bulleted)
   - Dosage & Safety Precautions (exact kg/acre or ml/L where relevant)
4. LANGUAGE:
   - Auto-detect the user's language. Respond in Telugu (in Telugu script) if asked in Telugu, English if asked in English, Hindi if asked in Hindi.
   - If language is mixed or Telugu by default, provide Telugu script response with clear technical terms.
</guidelines>
"""

_client = None
_available = False


def _get_client():
    global _client, _available
    if _client is not None:
        return _client
    key = os.getenv("GROQ_API_KEY")
    if not key:
        _available = False
        return None
    try:
        import groq
        _client = groq.Groq(api_key=key)
        _available = True
        return _client
    except Exception as e:
        logger.warning("Groq client init failed: %s", e)
        _available = False
        return None


def is_available():
    if _client is not None:
        return True
    return _get_client() is not None


def strip_markdown(text: str) -> str:
    if not text:
        return text
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"(?<!\w)_(?!\w)(.+?)(?<!\w)_(?!\w)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"`([^`\n]+)`", r"\1", text)
    text = re.sub(r"```[\s\S]*?```", "", text)
    return text.strip()


def get_local_fallback_reply(query: str, farm_context: dict = None) -> str:
    """Generates an offline knowledge response from local datasets and RAG index when GROQ_API_KEY is absent."""
    q = (query or "").lower().strip()
    ctx_str = ""
    if farm_context:
        crop = farm_context.get("crop") or farm_context.get("predicted_crop")
        n = farm_context.get("n")
        p = farm_context.get("p")
        k = farm_context.get("k")
        state = farm_context.get("state")
        district = farm_context.get("district")
        details = []
        if crop: details.append(f"Crop: {str(crop).capitalize()}")
        if state or district: details.append(f"Location: {district or ''}, {state or ''}".strip(", "))
        if n is not None and p is not None and k is not None: details.append(f"Soil NPK: N={n}, P={p}, K={k} kg/ha")
        if details:
            ctx_str = f"\n[Farm Context: {'; '.join(details)}]"

    # RAG Hybrid Vector & Live Web Search Fallback
    try:
        import agri_rag
        results, rag_text, source_type = agri_rag.retrieve_hybrid(q, top_k=2)
        if results:
            sources = ", ".join(set(r["source"] for r in results))
            badge = "🌐 (Live Agricultural Web Search Fallback)" if source_type == "web" else f"📚 (RAG Knowledge Engine — Sources: {sources})"
            return (
                f"{badge}{ctx_str}\n\n"
                f"{results[0]['text']}\n\n"
                f"Action Tip: Verify guidelines with your local Krishi Vigyan Kendra (KVK) or agricultural extension officer."
            )
    except Exception as e:
        logger.warning("RAG fallback retrieval error: %s", e)

    try:
        from crop_defaults import CROP_DEFAULTS
    except Exception:
        CROP_DEFAULTS = {}

    matched_crop = None
    for crop in CROP_DEFAULTS:
        if crop in q:
            matched_crop = crop
            break

    if matched_crop:
        data = CROP_DEFAULTS[matched_crop]
        return (
            f"ℹ️ (Offline Knowledge Assistant Mode){ctx_str}\n"
            f"Here are the scientific agronomic guidelines for growing {matched_crop.capitalize()}:\n"
            f"- Typical NPK Balance: Nitrogen {data.get('N')} kg/ha, Phosphorus {data.get('P')} kg/ha, Potassium {data.get('K')} kg/ha\n"
            f"- Ideal Temperature Range: {data.get('temperature')}°C\n"
            f"- Recommended Soil pH: {data.get('ph')}\n"
            f"- Water/Rainfall Requirement: {data.get('rainfall')} mm\n\n"
            f"Action Tip: Ensure proper soil drainage and apply organic compost to maintain balanced NPK ratios."
        )

    if any(kw in q for kw in ["fertilizer", "urea", "npk", "dosage", "potash", "dap"]):
        return (
            f"ℹ️ (Offline Knowledge Assistant Mode){ctx_str}\n"
            f"General Fertilizer & NPK Advisory:\n"
            f"- Nitrogen (Urea): Essential for leafy growth. Apply 50% as basal dose and 50% top-dressing.\n"
            f"- Phosphorus (DAP/SSP): Crucial for root development; apply fully during land preparation.\n"
            f"- Potassium (MOP): Enhances pest resistance and grain quality.\n"
            f"Tip: Conduct a soil test or check your Soil Health Card before heavy fertilizer application."
        )

    if any(kw in q for kw in ["disease", "pest", "leaf", "insect", "fungus", "spray"]):
        return (
            f"ℹ️ (Offline Knowledge Assistant Mode){ctx_str}\n"
            f"General Plant Health & Pest Management:\n"
            f"- Organic Spray: 5% Neem Seed Kernel Extract (NSKE) or Neem oil (5ml/L water) for early sucking pests.\n"
            f"- Fungal Leaf Spots: Ensure proper crop spacing and avoid waterlogging.\n"
            f"Tip: Upload a leaf photo using the diagnose button once GROQ_API_KEY is configured for automated AI visual diagnosis!"
        )

    if any(kw in q for kw in ["weather", "rain", "monsoon", "irrigation"]):
        return (
            f"ℹ️ (Offline Knowledge Assistant Mode){ctx_str}\n"
            f"Irrigation & Rain Guidance:\n"
            f"- Avoid top-dressing fertilizers (like Urea) 24-48 hours before expected heavy rain.\n"
            f"- Use drip irrigation or furrow irrigation to conserve soil moisture in dry spells."
        )

    return (
        f"ℹ️ (Offline Knowledge Assistant Mode){ctx_str}\n"
        f"Hello! I am AgriAI, your farming assistant.\n"
        f"You can ask me about crop selection (e.g. rice, cotton, chilli, groundnut), fertilizer dosages, soil NPK balance, or government schemes (e.g. PM-KISAN, PMFBY).\n"
        f"Tip: Configure GROQ_API_KEY in your .env file to unlock real-time Llama 3.3 70B RAG AI!"
    )


def transcribe(audio_bytes: bytes, filename: str = "audio.webm", lang: str = None):
    """Speech-to-text via Groq Whisper. Returns (text, status)."""
    client = _get_client()
    if client is None:
        return ("", "no_key")
    try:
        model_name = os.getenv("STT_MODEL", "whisper-large-v3-turbo")
        kwargs = {
            "model": model_name,
            "file": (filename, audio_bytes),
        }
        if lang:
            kwargs["language"] = lang
        resp = client.audio.transcriptions.create(**kwargs)
        return (resp.text or "", "ok")
    except Exception as e:
        logger.error("Groq STT error: %s", e)
        return ("", "error")


def speak(text: str, lang: str = "te"):
    """Text-to-speech via gTTS. Returns (audio_base64_mp3, status)."""
    try:
        from gtts import gTTS
        import io
        buf = io.BytesIO()
        valid_lang = lang if lang in ["en", "hi", "te", "ta", "kn"] else "te"
        gTTS(text=text, lang=valid_lang, slow=False).write_to_fp(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return (b64, "ok")
    except Exception as e:
        logger.error("TTS error: %s", e)
        return ("", "error")


def diagnose(image_bytes: bytes, filename: str = "image.jpg"):
    """Image-to-text via Groq vision model (llama-3.2-11b-vision-preview or similar)."""
    client = _get_client()
    if client is None:
        return ("AI assistant is not configured with an API key. Add GROQ_API_KEY to .env for visual disease diagnosis.", "no_key")
    try:
        vision_model = os.getenv("LLM_VISION_MODEL", "llama-3.2-11b-vision-preview")
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        messages = [
            {
                "role": "system",
                "content": "You are AgriAI, an expert agricultural assistant. Analyze the plant leaf image for diseases, pests, or nutrient deficiencies. Provide the diagnosis in plain language with clear advice on treatment. No markdown."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is wrong with this plant leaf? Give diagnosis and remedy."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }
        ]
        resp = client.chat.completions.create(
            model=vision_model,
            messages=messages,
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        )
        text = resp.choices[0].message.content or ""
        return (strip_markdown(text), "ok")
    except Exception as e:
        logger.error("Groq diagnosis error: %s", e)
        return (f"Sorry, the image diagnosis service returned an error: {e}", "error")


def chat(user_message: str, history=None, model=None, speak_lang="te", farm_context=None):
    """Return (reply_text, status, audio_b64). audio_b64 may be ''. """
    client = _get_client()
    if client is None:
        reply = get_local_fallback_reply(user_message, farm_context=farm_context)
        audio, _ = speak(reply, speak_lang)
        return (reply, "ok_fallback", audio)
    try:
        llm_model = model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
        # RAG Hybrid Vector & Live Web Knowledge Retrieval
        rag_passages, rag_context, source_type = [], "", "none"
        try:
            import agri_rag
            rag_passages, rag_context, source_type = agri_rag.retrieve_hybrid(user_message, top_k=2)
        except Exception as e:
            logger.warning("RAG retrieval error: %s", e)

        sys_prompt = SYSTEM_PROMPT
        if rag_context:
            source_label = "live verified agricultural web search" if source_type == "web" else "verified agricultural knowledge documents"
            sys_prompt += f"\n<retrieved_knowledge_context source='{source_type}'>\n{rag_context}\nUse the above {source_label} to provide accurate, grounded answers. If from web search, cite that info comes from recent agricultural web findings.\n</retrieved_knowledge_context>"

        if farm_context:
            ctx_items = [f"{k}: {v}" for k, v in farm_context.items() if v]
            if ctx_items:
                sys_prompt += f"\n<farmer_context>\n{'; '.join(ctx_items)}\nUse this farm context naturally in your advice.\n</farmer_context>"

        messages = [{"role": "system", "content": sys_prompt}]
        if history:
            for turn in history[-6:]:
                messages.append({"role": "user", "content": turn.get("user", "")})
                messages.append({"role": "assistant", "content": turn.get("ai", "")})
        messages.append({"role": "user", "content": user_message})

        resp = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        )
        text = strip_markdown(resp.choices[0].message.content or "")
        audio, _ = speak(text, speak_lang)
        return (text, "ok", audio)
    except Exception as e:
        logger.error("Groq chat error: %s", e)
        reply = get_local_fallback_reply(user_message, farm_context=farm_context)
        audio, _ = speak(reply, speak_lang)
        return (reply, "ok_fallback", audio)