import streamlit as st
from dotenv import load_dotenv

from app.session import require_login
from db.models import list_flashcard_topics, list_flashcards, save_flashcards
from utils.ai import chat, chat_json, parse_json_response
from utils.prompts import flashcards_prompt, flashcards_image_prompt
from utils.rag import build_index, file_hash, retrieve
from utils.vision import analyze_image

load_dotenv()
user = require_login()

IMAGE_TYPES = ("png", "jpg", "jpeg", "webp")
IMAGE_MIME = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}


@st.cache_resource(show_spinner=False)
def _cached_index(_hash: str, pdf_bytes: bytes):
    return build_index(pdf_bytes)


def _ext(name: str) -> str:
    return (name.rsplit(".", 1)[-1] if "." in name else "").lower()


st.title("🃏 Flashcards")
st.caption("Generate AI flashcards from a topic, a PDF, or a photo.")

tab_generate, tab_study = st.tabs(["Generate", "Study"])

with tab_generate:
    topic = st.text_input("Topic", placeholder="e.g. The French Revolution")
    count = st.slider("How many cards?", min_value=3, max_value=20, value=8)
    uploaded = st.file_uploader(
        "Optional: PDF (RAG), image (Gemini), or TXT",
        type=["pdf", "txt", "md", *IMAGE_TYPES],
        key="fc_upload",
    )

    can_generate = bool(topic.strip()) or uploaded is not None
    if st.button("Generate cards", type="primary", disabled=not can_generate):
        cards: list[dict] = []
        try:
            if uploaded is not None and _ext(uploaded.name) in IMAGE_TYPES:
                ext = _ext(uploaded.name)
                with st.spinner("Reading the image with Gemini..."):
                    raw = analyze_image(
                        uploaded.getvalue(),
                        IMAGE_MIME[ext],
                        flashcards_image_prompt(count),
                    )
                cards = parse_json_response(raw)
                if not topic.strip():
                    topic = uploaded.name.rsplit(".", 1)[0]

            elif uploaded is not None and _ext(uploaded.name) == "pdf":
                if not topic.strip():
                    st.error("Add a topic so I know what to retrieve from the PDF.")
                    st.stop()
                data = uploaded.getvalue()
                with st.spinner("Indexing PDF (first run downloads the embedding model)..."):
                    index = _cached_index(file_hash(data), data)
                with st.spinner("Retrieving relevant passages..."):
                    context = retrieve(index, topic.strip(), k=6)
                system, prompt = flashcards_prompt(topic.strip(), count, context)
                with st.spinner("Generating..."):
                    cards = chat_json(system, prompt, temperature=0.5)

            else:
                context = ""
                if uploaded is not None:
                    context = uploaded.getvalue().decode("utf-8", errors="replace")
                system, prompt = flashcards_prompt(topic.strip(), count, context)
                with st.spinner("Generating..."):
                    cards = chat_json(system, prompt, temperature=0.5)
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
            cards = []

        if cards:
            st.session_state["pending_cards"] = cards
            st.session_state["pending_topic"] = topic.strip() or "Untitled"

    pending = st.session_state.get("pending_cards")
    if pending:
        st.subheader("Preview")
        for i, card in enumerate(pending, 1):
            with st.expander(f"Card {i}: {card.get('question', '')}"):
                st.write(card.get("answer", ""))
        if st.button("💾 Save to my library"):
            save_flashcards(user["id"], st.session_state["pending_topic"], pending)
            st.success(f"Saved {len(pending)} cards.")
            st.session_state.pop("pending_cards", None)
            st.session_state.pop("pending_topic", None)

with tab_study:
    topics = list_flashcard_topics(user["id"])
    if not topics:
        st.info("No saved flashcards yet — generate some on the other tab.")
    else:
        selected = st.selectbox("Pick a topic", topics)
        cards = list_flashcards(user["id"], topic=selected)
        if cards:
            idx_key = f"study_idx::{selected}"
            show_key = f"study_show::{selected}"
            idx = st.session_state.get(idx_key, 0) % len(cards)
            card = cards[idx]

            st.markdown(f"**Card {idx + 1} of {len(cards)}**")
            st.markdown(f"### ❓ {card['question']}")

            if st.session_state.get(show_key):
                st.markdown(f"### 💡 {card['answer']}")

            col1, col2, col3 = st.columns(3)
            if col1.button("⬅️ Prev", use_container_width=True):
                st.session_state[idx_key] = (idx - 1) % len(cards)
                st.session_state[show_key] = False
                st.rerun()
            if col2.button(
                "Hide answer" if st.session_state.get(show_key) else "Show answer",
                use_container_width=True,
            ):
                st.session_state[show_key] = not st.session_state.get(show_key, False)
                st.rerun()
            if col3.button("Next ➡️", use_container_width=True):
                st.session_state[idx_key] = (idx + 1) % len(cards)
                st.session_state[show_key] = False
                st.rerun()
