"""agri_chat.py — Agri AI assistant (merged from Krishi Sahayak / LLM_Agri_Bot).
Text + voice + image advisory using the Groq SDK. Requires GROQ_API_KEY in .env.
Gracefully degrades with a clear message if the key is missing.
System prompt reused (plain-text, Indian-farmer focused) from the source bot.
"""
import os
import re
import base64
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """<role>
You are AgriAI — an expert agricultural assistant for Indian farmers.
Your purpose is to provide accurate, practical, and region-specific farming advice.
</role>
<personality>
CRITICAL RULE — FORMATTING:
- You MUST output ONLY plain text. Absolutely NO markdown formatting.
- DO NOT use ** (bold), * (italic), _ (underserscore), # (headings), or ` (code).
- If you need a list, use dashes like "- First item".
- Write emphasis as "Important: ..." or "Note: ..." in plain text.
</personality>
<thinking>
Before answering: identify the crop, season, region, and language if mentioned.
Prioritize sustainable, low-cost solutions for smallholding farmers.
If the query lacks crop name or region, ask politely.
</thinking>
Answer in the farmer's language when possible. Default to Telugu (Telugu script) for replies;
if the user writes in English/Hindi or asks for another language, respond in that language.
Keep it short, practical, and actionable.
"""

_client = None
_available = False


def _get_client():
    global _client, _available
    if _client is not None or _available is False and _client is None:
        pass
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


def transcribe(audio_bytes: bytes, filename: str = "audio.webm"):
    """Speech-to-text via Groq Whisper. Returns (text, status)."""
    client = _get_client()
    if client is None:
        return ("", "no_key")
    try:
        import io
        # Groq whisper accepts (filename, bytes) tuple
        resp = client.audio.transcriptions.create(
            model=os.getenv("STT_MODEL", "whisper-large-v3-turbo"),
            file=(filename, audio_bytes),
            language="te",  # Telugu
        )
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
        gTTS(text=text, lang=lang, slow=False).write_to_fp(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return (b64, "ok")
    except Exception as e:
        logger.error("TTS error: %s", e)
        return ("", "error")


def diagnose(image_bytes: bytes, filename: str = "image.jpg"):
    """Image-to-text via Groq vision model (llama-4-scout or similar)."""
    client = _get_client()
    if client is None:
        return ("AI assistant is not configured. Add GROQ_API_KEY to .env to enable diagnosis.", "no_key")
    try:
        # Use the vision model from env or default
        vision_model = os.getenv("LLM_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
        # Encode image as base64
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        # Build messages with image
        messages = [
            {
                "role": "system",
                "content": "You are AgriAI, an expert agricultural assistant. Analyze the plant leaf image for diseases, pests, or nutrient deficiencies. Provide the diagnosis in plain Telugu (if user likely Telugu) or English, with clear advice on treatment. No markdown."
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
        # Strip markdown
        import re
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"(?<!\*)\*(?!*)(.+?)(?<!\*)\*(?!*)", r"\1", text)
        text = re.sub(r"__(.+?)__", r"\1", text)
        text = re.sub(r"(?<!\w)_(?!\w)(.+?)(?<!\w)_(?!\w)", r"\1", text)
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"`([^`\n]+)`", r"\1", text)
        text = re.sub(r"```[\s\S]*?```", "", text)
        return (text.strip(), "ok")
    except Exception as e:
        logger.error("Groq diagnosis error: %s", e)
        return (f"Sorry, the image diagnosis service returned an error: {e}", "error")


def chat(user_message: str, history=None, model=None, speak_lang="te"):
    """Return (reply_text, status, audio_b64). audio_b64 may be ''. """
    client = _get_client()
    if client is None:
        return ("AI assistant is not configured. Add GROQ_API_KEY to .env to enable chat.", "no_key", "")
    try:
        llm_model = model or os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
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
        return (f"Sorry, the AI service returned an error: {e}", "error", "")