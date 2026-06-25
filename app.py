"""
AI Image Analyzer
==================
Google Gemini Vision API yordamida rasmlarni tahlil qiluvchi Streamlit ilovasi.
Barcha tahlil natijalari o'zbek tilida ko'rsatiladi.

Muallif: AI Image Analyzer Team
Litsenziya: MIT
"""

import io
import json
import logging

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

# ---------------------------------------------------------------------------
# Logging sozlamalari
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ilova konfiguratsiyasi
# ---------------------------------------------------------------------------
APP_TITLE = "AI Image Analyzer"
PAGE_ICON = "🖼️"
SUPPORTED_TYPES = ["jpg", "jpeg", "png", "webp"]
MAX_FILE_SIZE_MB = 15
GEMINI_MODEL = "gemini-2.5-flash"  # Vision imkoniyatiga ega tezkor model

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Maxsus CSS — zamonaviy va professional ko'rinish uchun
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Umumiy fon va shrift */
    .main {
        background-color: #0e1117;
    }

    /* Sarlavha bloki */
    .app-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .app-header h1 {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .app-header p {
        color: #9CA3AF;
        font-size: 1.05rem;
    }

    /* Natija kartalari */
    .result-card {
        background-color: #1a1d24;
        border: 1px solid #2d3139;
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
    }
    .result-card h3 {
        margin-top: 0;
        color: #06B6D4;
        font-size: 1.15rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .result-card p, .result-card li {
        color: #E5E7EB;
        line-height: 1.65;
        font-size: 0.97rem;
    }

    /* Rang palitrasi katakchalari */
    .color-swatch {
        display: inline-block;
        width: 28px;
        height: 28px;
        border-radius: 6px;
        margin-right: 6px;
        border: 1px solid rgba(255,255,255,0.15);
        vertical-align: middle;
    }

    /* Tugma uslubi */
    div.stButton > button {
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        border: none;
        width: 100%;
        transition: opacity 0.2s ease;
    }
    div.stButton > button:hover {
        opacity: 0.88;
    }

    /* Footer */
    .footer-note {
        text-align: center;
        color: #6B7280;
        font-size: 0.85rem;
        margin-top: 2rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Yordamchi funksiyalar
# ---------------------------------------------------------------------------
def get_api_key() -> str | None:
    """
    Gemini API kalitini Streamlit secrets'dan oladi.
    Agar topilmasa None qaytaradi.
    """
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None


def validate_image_file(uploaded_file) -> tuple[bool, str]:
    """
    Yuklangan faylni tekshiradi: hajmi va formati to'g'riligini aniqlaydi.
    Qaytaradi: (amal_qiladi: bool, xabar: str)
    """
    if uploaded_file is None:
        return False, "Fayl tanlanmagan."

    # Hajmni tekshirish
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"Fayl hajmi {MAX_FILE_SIZE_MB} MB dan oshmasligi kerak. Yuklangan fayl: {size_mb:.1f} MB."

    # Rasm sifatida ochib ko'rish (buzilgan fayllarni aniqlash uchun)
    try:
        img = Image.open(uploaded_file)
        img.verify()
    except Exception:
        return False, "Fayl yaroqsiz yoki buzilgan rasm. Iltimos, boshqa fayl tanlang."

    uploaded_file.seek(0)  # Pointer'ni boshiga qaytarish
    return True, ""


def build_analysis_prompt() -> str:
    """
    Gemini modeliga yuboriladigan, struktura asosida JSON javob talab qiladigan
    promptni shakllantiradi. Javoblar o'zbek tilida bo'lishi so'raladi.
    """
    return """
Siz professional kompyuter ko'rish (computer vision) tahlilchisisiz.
Quyidagi rasmni chuqur tahlil qiling va natijani FAQAT quyidagi JSON formatida,
HECH QANDAY qo'shimcha matn, izoh yoki markdown belgilarisiz qaytaring.
Barcha matnli qiymatlar O'ZBEK TILIDA bo'lishi SHART.

JSON struktura:
{
  "tafsilotli_tasvir": "Rasmning batafsil, ravon va tabiiy tildagi tasviri (3-5 jumla)",
  "aniqlangan_obyektlar": [
    {"nomi": "obyekt nomi o'zbekcha", "ishonchlilik": "yuqori/o'rta/past", "joylashuvi": "rasmda qayerda joylashgani"}
  ],
  "sahna_tahlili": {
    "joy_turi": "ichkari/tashqari/aniqlanmadi",
    "muhit": "sahna haqida umumiy tavsif (shahar, tabiat, xona va h.k.)",
    "yoritilganlik": "yorug'lik sharoiti tavsifi",
    "kayfiyat": "rasmning umumiy kayfiyati/uslubi"
  },
  "rang_tahlili": {
    "asosiy_ranglar": [
      {"nomi": "rang nomi o'zbekcha", "hex": "#RRGGBB"}
    ],
    "umumiy_palitra": "rang palitrasi haqida umumiy tavsif (issiq/sovuq, kontrast va h.k.)"
  },
  "matn_ajratish": {
    "matn_mavjud": true/false,
    "ajratilgan_matn": "Agar rasmda matn bo'lsa, uni aniq ko'chiring. Bo'lmasa bo'sh qoldiring.",
    "izoh": "Matn haqida qisqa izoh (qayerda joylashgani, qaysi tilda va h.k.)"
  },
  "xavfsizlik_tahlili": {
    "xavfsiz": true/false,
    "tavsif": "Rasm tarkibida zararli, nomaqbul yoki xavfli unsurlar bor-yo'qligi haqida xulosa",
    "ogohlantirishlar": ["agar mavjud bo'lsa, ogohlantirishlar ro'yxati"]
  },
  "xulosa": "Rasmning umumiy mazmuni va asosiy xususiyatlarini jamlovchi qisqa xulosa (2-3 jumla)"
}

Eslatma: agar biror maydon uchun ma'lumot topilmasa, mos bo'sh qiymat
(bo'sh massiv, bo'sh satr yoki false) qaytaring, lekin maydonni o'chirmang.
"""


def call_gemini_vision(api_key: str, image_bytes: bytes, mime_type: str) -> dict:
    """
    Gemini Vision API'ga so'rov yuboradi va JSON natijani dict ko'rinishida qaytaradi.
    Xatolik yuzaga kelsa, mos Exception ko'taradi (yuqorida ushlanadi).
    """
    client = genai.Client(api_key=api_key)

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    prompt = build_analysis_prompt()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[image_part, prompt],
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    raw_text = response.text.strip()

    # Ba'zan model JSON'ni ```json ... ``` ichida qaytarishi mumkin — tozalaymiz
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    return json.loads(raw_text)


# ---------------------------------------------------------------------------
# Natijalarni ko'rsatish funksiyalari
# ---------------------------------------------------------------------------
def render_description(data: dict):
    st.markdown(
        f"""
        <div class="result-card">
            <h3>📝 Tafsilotli tasvir</h3>
            <p>{data.get("tafsilotli_tasvir", "Ma'lumot topilmadi.")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_objects(data: dict):
    objects = data.get("aniqlangan_obyektlar", [])
    if objects:
        rows = ""
        for obj in objects:
            rows += (
                f"<li><strong>{obj.get('nomi', 'N/A')}</strong> — "
                f"ishonchlilik: {obj.get('ishonchlilik', 'N/A')}, "
                f"joylashuvi: {obj.get('joylashuvi', 'N/A')}</li>"
            )
        content = f"<ul>{rows}</ul>"
    else:
        content = "<p>Obyektlar aniqlanmadi.</p>"

    st.markdown(
        f"""
        <div class="result-card">
            <h3>🔍 Aniqlangan obyektlar</h3>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scene(data: dict):
    scene = data.get("sahna_tahlili", {})
    st.markdown(
        f"""
        <div class="result-card">
            <h3>🌆 Sahna tahlili</h3>
            <p><strong>Joy turi:</strong> {scene.get("joy_turi", "N/A")}</p>
            <p><strong>Muhit:</strong> {scene.get("muhit", "N/A")}</p>
            <p><strong>Yoritilganlik:</strong> {scene.get("yoritilganlik", "N/A")}</p>
            <p><strong>Kayfiyat:</strong> {scene.get("kayfiyat", "N/A")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_colors(data: dict):
    colors = data.get("rang_tahlili", {})
    main_colors = colors.get("asosiy_ranglar", [])

    swatches = ""
    for c in main_colors:
        hex_code = c.get("hex", "#888888")
        name = c.get("nomi", "")
        swatches += (
            f'<span class="color-swatch" style="background-color:{hex_code};" '
            f'title="{name} ({hex_code})"></span>'
        )

    st.markdown(
        f"""
        <div class="result-card">
            <h3>🎨 Rang tahlili</h3>
            <div style="margin-bottom: 0.7rem;">{swatches or "Ranglar aniqlanmadi."}</div>
            <p>{colors.get("umumiy_palitra", "")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ocr(data: dict):
    ocr = data.get("matn_ajratish", {})
    has_text = ocr.get("matn_mavjud", False)

    if has_text:
        body = (
            f'<p><strong>Ajratilgan matn:</strong></p>'
            f'<p style="background:#0e1117; padding:0.7rem; border-radius:8px; '
            f'white-space:pre-wrap;">{ocr.get("ajratilgan_matn", "")}</p>'
            f'<p><strong>Izoh:</strong> {ocr.get("izoh", "")}</p>'
        )
    else:
        body = "<p>Rasmda matn aniqlanmadi.</p>"

    st.markdown(
        f"""
        <div class="result-card">
            <h3>📄 Matn ajratish (OCR)</h3>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_safety(data: dict):
    safety = data.get("xavfsizlik_tahlili", {})
    is_safe = safety.get("xavfsiz", True)
    badge = "✅ Xavfsiz" if is_safe else "⚠️ Diqqat talab qiladi"
    badge_color = "#10B981" if is_safe else "#F59E0B"

    warnings = safety.get("ogohlantirishlar", [])
    warnings_html = ""
    if warnings:
        items = "".join(f"<li>{w}</li>" for w in warnings)
        warnings_html = f"<ul>{items}</ul>"

    st.markdown(
        f"""
        <div class="result-card">
            <h3>🛡️ Xavfsizlik / mazmun tahlili</h3>
            <p style="color:{badge_color}; font-weight:700;">{badge}</p>
            <p>{safety.get("tavsif", "")}</p>
            {warnings_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary(data: dict):
    st.markdown(
        f"""
        <div class="result-card">
            <h3>✅ Xulosa</h3>
            <p>{data.get("xulosa", "Xulosa topilmadi.")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Asosiy ilova
# ---------------------------------------------------------------------------
def main():
    # --- Sarlavha ---
    st.markdown(
        f"""
        <div class="app-header">
            <h1>{PAGE_ICON} {APP_TITLE}</h1>
            <p>Gemini AI yordamida rasmlaringizni chuqur tahlil qiling — natijalar o'zbek tilida</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- API kalitni tekshirish ---
    api_key = get_api_key()
    if not api_key:
        st.error(
            "⚠️ Gemini API kaliti topilmadi. Iltimos, `.streamlit/secrets.toml` "
            "faylida `GEMINI_API_KEY` qiymatini sozlang yoki Streamlit Cloud "
            "sozlamalarida 'Secrets' bo'limiga qo'shing."
        )
        st.info(
            "Mahalliy ishga tushirish uchun loyiha papkasida `.streamlit/secrets.toml` "
            "faylini yarating va quyidagicha yozing:\n\n"
            '```toml\nGEMINI_API_KEY = "sizning_api_kalitingiz"\n```'
        )
        st.stop()

    # --- Sidebar: qo'shimcha ma'lumot ---
    with st.sidebar:
        st.header("ℹ️ Ilova haqida")
        st.write(
            "Bu ilova Google Gemini Vision modeli yordamida yuklangan rasmni "
            "tahlil qiladi: obyektlarni aniqlaydi, sahnani tushuntiradi, rang "
            "palitrasini chiqaradi, matnni ajratadi (OCR) va mazmun xavfsizligini "
            "tekshiradi."
        )
        st.divider()
        st.write("**Qo'llab-quvvatlanadigan formatlar:**")
        st.write(", ".join(t.upper() for t in SUPPORTED_TYPES))
        st.write(f"**Maksimal fayl hajmi:** {MAX_FILE_SIZE_MB} MB")
        st.divider()
        st.caption(f"Model: `{GEMINI_MODEL}`")

    # --- Fayl yuklash ---
    uploaded_file = st.file_uploader(
        "Rasm faylini yuklang",
        type=SUPPORTED_TYPES,
        help=f"Qo'llab-quvvatlanadigan formatlar: {', '.join(SUPPORTED_TYPES)}",
    )

    if uploaded_file is not None:
        is_valid, error_message = validate_image_file(uploaded_file)

        if not is_valid:
            st.error(f"❌ {error_message}")
            return

        # --- Rasm oldindan ko'rish ---
        col1, col2 = st.columns([1, 1.4])
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Yuklangan rasm", use_container_width=True)
            st.caption(
                f"📐 O'lcham: {image.width}×{image.height} px | "
                f"📦 Format: {image.format} | "
                f"💾 Hajm: {uploaded_file.size / 1024:.1f} KB"
            )

            analyze_clicked = st.button("🔬 Rasmni tahlil qilish", type="primary")

        with col2:
            results_placeholder = st.empty()

            if analyze_clicked:
                with st.spinner("🤖 Gemini AI rasmni tahlil qilmoqda, biroz kuting..."):
                    try:
                        uploaded_file.seek(0)
                        image_bytes = uploaded_file.read()

                        # MIME turini aniqlash
                        mime_map = {
                            "jpg": "image/jpeg",
                            "jpeg": "image/jpeg",
                            "png": "image/png",
                            "webp": "image/webp",
                        }
                        ext = uploaded_file.name.split(".")[-1].lower()
                        mime_type = mime_map.get(ext, "image/jpeg")

                        result_data = call_gemini_vision(api_key, image_bytes, mime_type)
                        st.session_state["analysis_result"] = result_data

                    except json.JSONDecodeError:
                        st.error(
                            "❌ AI javobini qayta ishlashda xatolik yuz berdi. "
                            "Iltimos, qaytadan urinib ko'ring."
                        )
                        logger.exception("JSON decode error")
                        st.session_state.pop("analysis_result", None)

                    except genai_errors.APIError as e:
                        st.error(f"❌ Gemini API xatoligi: {e}")
                        logger.exception("Gemini API error")
                        st.session_state.pop("analysis_result", None)

                    except Exception as e:
                        st.error(f"❌ Kutilmagan xatolik yuz berdi: {e}")
                        logger.exception("Unexpected error")
                        st.session_state.pop("analysis_result", None)

            # Natijalarni ko'rsatish (agar mavjud bo'lsa)
            if "analysis_result" in st.session_state:
                with results_placeholder.container():
                    data = st.session_state["analysis_result"]
                    render_description(data)
                    render_objects(data)
                    render_scene(data)
                    render_colors(data)
                    render_ocr(data)
                    render_safety(data)
                    render_summary(data)
            elif not analyze_clicked:
                results_placeholder.info(
                    "👈 Tahlil natijalarini ko'rish uchun 'Rasmni tahlil qilish' "
                    "tugmasini bosing."
                )

    else:
        st.info("📤 Boshlash uchun yuqoridagi maydonga rasm yuklang.")
        # Tozalash: yangi sessiyada eski natijalar ko'rsatilmasligi uchun
        st.session_state.pop("analysis_result", None)

    # --- Footer ---
    st.markdown(
        """
        <div class="footer-note">
            Ishlab chiqilgan ❤️ bilan • Streamlit & Google Gemini AI asosida
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
