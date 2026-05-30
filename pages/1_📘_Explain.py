import streamlit as st
from dotenv import load_dotenv

from app.session import require_login
from utils.ai import chat
from utils.prompts import explain_prompt, explain_image_prompt
from utils.rag import build_index, file_hash, retrieve
from utils.vision import analyze_image

load_dotenv()
require_login()

IMAGE_TYPES = ("png", "jpg", "jpeg", "webp")
IMAGE_MIME = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}

st.title("📘 Explain a Topic")
st.caption("Type a topic, paste notes, attach a PDF for RAG, or upload a photo.")

topic = st.text_input("What do you want explained?", placeholder="e.g. Photosynthesis")
level = st.selectbox("Audience level", ["beginner", "intermediate", "advanced"], index=0)

uploaded = st.file_uploader(
    "Optional: attach a PDF (RAG), image (Gemini), or TXT",
    type=["pdf", "txt", "md", *IMAGE_TYPES],
)


@st.cache_resource(show_spinner=False)
def _cached_index(_hash: str, pdf_bytes: bytes):
    return build_index(pdf_bytes)


def _ext(name: str) -> str:
    return (name.rsplit(".", 1)[-1] if "." in name else "").lower()


if st.button("Explain", type="primary", disabled=uploaded is None and not topic.strip()):
    try:
        if uploaded is not None and _ext(uploaded.name) in IMAGE_TYPES:
            ext = _ext(uploaded.name)
            with st.spinner("Reading the image with Gemini..."):
                answer = analyze_image(
                    uploaded.getvalue(),
                    IMAGE_MIME[ext],
                    explain_image_prompt(level, hint=topic.strip()),
                )

        elif uploaded is not None and _ext(uploaded.name) == "pdf":
            if not topic.strip():
                st.error("Add a topic so I know what to retrieve from the PDF.")
                st.stop()
            data = uploaded.getvalue()
            with st.spinner("Indexing PDF (first run downloads the embedding model)..."):
                index = _cached_index(file_hash(data), data)
            with st.spinner("Retrieving relevant passages..."):
                context = retrieve(index, topic.strip(), k=5)
            system, user = explain_prompt(topic.strip(), level, context)
            with st.spinner("Thinking..."):
                answer = chat(system, user, temperature=0.3)

        else:
            context = ""
            if uploaded is not None:
                context = uploaded.getvalue().decode("utf-8", errors="replace")
            system, user = explain_prompt(topic.strip(), level, context)
            with st.spinner("Thinking..."):
                answer = chat(system, user, temperature=0.3)
    except Exception as exc:
        st.error(f"Request failed: {exc}")
    else:
        st.markdown(answer)
