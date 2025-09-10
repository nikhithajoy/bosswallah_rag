import streamlit as st
from translate import Translator

# Supported languages mapping
LANGUAGES = {
    "English": "en",
    "Malayalam": "ml",
    "Tamil": "ta",
    "Hindi": "hi",
    "Telugu": "te",
    "Kannada": "kn"
}

st.set_page_config(page_title="Language Translator", page_icon="🌐", layout="centered")

st.title("🌐 English ↔ Regional Language Translator")
st.write("Easily translate between English and Indian regional languages using the `translate` library.")

# Sidebar
st.sidebar.header("⚙️ Settings")
source_lang = st.sidebar.selectbox("Select Source Language", list(LANGUAGES.keys()), index=0)
target_lang = st.sidebar.selectbox("Select Target Language", list(LANGUAGES.keys()), index=1)

# Input text
text_to_translate = st.text_area("✍️ Enter text to translate", height=150)

if st.button("Translate"):
    if not text_to_translate.strip():
        st.warning("⚠️ Please enter some text to translate.")
    elif source_lang == target_lang:
        st.info("✅ Source and target languages are the same. Nothing to translate.")
    else:
        try:
            translator = Translator(from_lang=LANGUAGES[source_lang], to_lang=LANGUAGES[target_lang])
            translation = translator.translate(text_to_translate)
            st.success("🎯 Translation:")
            st.write(f"**{translation}**")
        except Exception as e:
            st.error(f"❌ Translation failed: {str(e)}")

# Footer
st.markdown("---")
st.caption("Powered by [translate](https://pypi.org/project/translate/) library in Python 🚀")
