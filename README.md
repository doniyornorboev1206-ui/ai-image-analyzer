# 🖼️ AI Image Analyzer

Google **Gemini Vision API** asosida ishlaydigan, rasmlarni chuqur tahlil qiluvchi va natijalarni **o'zbek tilida** taqdim etuvchi Streamlit veb-ilovasi.

## ✨ Imkoniyatlar

- 📤 JPG, JPEG, PNG, WEBP formatidagi rasmlarni yuklash
- 🖼️ Yuklangan rasmni oldindan ko'rish
- 🔬 Bir tugma bosish bilan to'liq AI tahlili
- 📝 Rasmning batafsil tasviri
- 🔍 Obyektlarni aniqlash va identifikatsiya qilish
- 🌆 Sahna tahlili (joy turi, muhit, yoritilganlik, kayfiyat)
- 🎨 Rang tahlili (asosiy ranglar va palitra)
- 📄 Matnni ajratib olish (OCR)
- 🛡️ Xavfsizlik / mazmun tahlili
- ✅ Umumiy xulosa
- ⚡ Zamonaviy, professional va responsive dizayn
- 🛑 To'liq xatoliklarni boshqarish (error handling)

---

## 📁 Loyiha tuzilishi

```
ai-image-analyzer/
├── app.py                          # Asosiy Streamlit ilovasi
├── requirements.txt                # Python bog'liqliklari
├── README.md                       # Ushbu fayl
├── .gitignore                      # Git uchun e'tiborsiz qoldiriladigan fayllar
└── .streamlit/
    └── secrets.toml.example        # API kalit uchun namuna fayl
```

---

## 🔑 1-qadam: Gemini API kalitini olish

1. [Google AI Studio](https://aistudio.google.com/app/apikey) saytiga kiring
2. Google hisobingiz bilan tizimga kiring
3. **"Create API Key"** tugmasini bosing
4. Yaratilgan API kalitni nusxalab oling (keyinroq kerak bo'ladi)

---

## 💻 2-qadam: Loyihani mahalliy (local) ishga tushirish

### Talablar

- Python 3.10 yoki undan yuqori versiya
- pip (Python paket menejeri)

### O'rnatish

1. **Loyihani yuklab oling** (yoki GitHub'dan klonlang):

```bash
git clone https://github.com/SIZNING_USERNAME/ai-image-analyzer.git
cd ai-image-analyzer
```

2. **Virtual muhit yaratish (tavsiya etiladi):**

```bash
python -m venv venv

# Windows uchun:
venv\Scripts\activate

# macOS / Linux uchun:
source venv/bin/activate
```

3. **Kerakli kutubxonalarni o'rnatish:**

```bash
pip install -r requirements.txt
```

4. **API kalitni sozlash:**

`.streamlit` papkasi ichida `secrets.toml` nomli fayl yarating (namunadan nusxa oling):

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

So'ngra `.streamlit/secrets.toml` faylini ochib, o'z API kalitingizni kiriting:

```toml
GEMINI_API_KEY = "sizning_haqiqiy_api_kalitingiz"
```

> ⚠️ **Diqqat:** `secrets.toml` faylini hech qachon GitHub'ga yuklamang! Bu fayl `.gitignore` orqali avtomatik tarzda e'tiborsiz qoldiriladi.

5. **Ilovani ishga tushirish:**

```bash
streamlit run app.py
```

Ilova brauzerda avtomatik ochiladi (odatda `http://localhost:8501` manzilida).

---

## 🐙 3-qadam: Loyihani GitHub'ga yuklash

1. GitHub'da yangi repository yarating (masalan: `ai-image-analyzer`)

2. Loyiha papkasida Git'ni ishga tushiring:

```bash
git init
git add .
git commit -m "Birinchi commit: AI Image Analyzer"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/ai-image-analyzer.git
git push -u origin main
```

> ✅ `.gitignore` fayli tufayli `secrets.toml` faylingiz GitHub'ga yuklanmaydi — API kalitingiz xavfsiz qoladi.

3. GitHub'dagi repository'ni tekshirib, barcha fayllar (`app.py`, `requirements.txt`, `README.md`, `.streamlit/secrets.toml.example`) joylashganiga ishonch hosil qiling.

---

## ☁️ 4-qadam: Streamlit Community Cloud'ga deploy qilish

1. [share.streamlit.io](https://share.streamlit.io) saytiga kiring va GitHub hisobingiz orqali tizimga kiring

2. **"Create app"** (yoki **"New app"**) tugmasini bosing

3. Quyidagi ma'lumotlarni kiriting:
   - **Repository:** `SIZNING_USERNAME/ai-image-analyzer`
   - **Branch:** `main`
   - **Main file path:** `app.py`

4. **"Advanced settings"** bo'limini oching va **Secrets** qismiga quyidagini kiriting:

```toml
GEMINI_API_KEY = "sizning_haqiqiy_api_kalitingiz"
```

5. **"Deploy!"** tugmasini bosing

6. Bir necha daqiqadan so'ng ilovangiz tayyor bo'ladi va ommaviy URL orqali (masalan, `https://ai-image-analyzer.streamlit.app`) ishlaydi.

### Secrets'ni keyinroq o'zgartirish

Agar API kalitni keyinroq qo'shish yoki o'zgartirish kerak bo'lsa:
1. Streamlit Cloud dashboard'ida ilovangizni tanlang
2. **"⋮" (uch nuqta) → Settings → Secrets** bo'limiga o'ting
3. `GEMINI_API_KEY` qiymatini kiritib saqlang
4. Ilova avtomatik qayta ishga tushadi

---

## 🛠️ Texnologiyalar

| Texnologiya | Maqsad |
|---|---|
| [Streamlit](https://streamlit.io) | Veb-interfeys yaratish |
| [Google Gen AI SDK](https://ai.google.dev/gemini-api/docs) | Gemini Vision modeliga ulanish |
| [Pillow (PIL)](https://python-pillow.org) | Rasmlarni qayta ishlash va tekshirish |

---

## ❗ Xatoliklarni bartaraf etish

| Muammo | Yechim |
|---|---|
| `GEMINI_API_KEY topilmadi` xatosi | `.streamlit/secrets.toml` faylini to'g'ri joylashtirganingizni va kalit nomini aniq yozganingizni tekshiring |
| `API xatoligi` xabari | API kalitingiz amal qilishini va Google AI Studio'da limitlar tugamaganini tekshiring |
| Fayl yuklanmayapti | Fayl hajmi 15 MB dan oshmasligi va formati JPG/JPEG/PNG/WEBP bo'lishi kerak |
| Tahlil natijasi noto'g'ri formatda | Qaytadan urinib ko'ring — ba'zida AI javobi formatlashda vaqtinchalik xatolik bo'lishi mumkin |

---

## 📄 Litsenziya

Bu loyiha ochiq manba (open-source) sifatida MIT litsenziyasi asosida taqdim etiladi — erkin foydalanishingiz, o'zgartirishingiz va tarqatishingiz mumkin.

---

## 🤝 Hissa qo'shish

Pull request va takliflar mamnuniyat bilan qabul qilinadi! Loyihani fork qiling, o'zgartirishlar kiritib, PR yuboring.
