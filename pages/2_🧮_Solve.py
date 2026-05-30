import streamlit as st
from dotenv import load_dotenv

from app.session import require_login
from utils.ai import chat
from utils.prompts import solve_prompt, solve_image_prompt
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

st.title("🧮 Solve an Exercise")
st.caption("Paste a problem or upload a photo of one.")

subject = st.selectbox(
    "Subject",
    ["Math", "Physics", "Chemistry", "Biology", "Computer Science", "Logic", "Other"],
)

tab_text, tab_image = st.tabs(["✏️ Type the problem", "📷 Upload a photo"])

with tab_text:
    problem = st.text_area(
        "Problem",
        height=180,
        placeholder="Paste the full question, including any constraints or given values.",
    )
    if st.button("Solve", key="solve_text", type="primary", disabled=not problem.strip()):
        system, user = solve_prompt(problem.strip(), subject)
        with st.spinner("Working through it..."):
            try:
                answer = chat(system, user, temperature=0.2)
            except Exception as exc:
                st.error(f"AI request failed: {exc}")
            else:
                st.markdown(answer)

with tab_image:
    image = st.file_uploader(
        "Upload an image of the problem",
        type=list(IMAGE_TYPES),
        key="solve_image_upload",
    )
    if image is not None:
        st.image(image, caption=image.name, use_container_width=True)

    if st.button("Solve from image", key="solve_image", type="primary", disabled=image is None):
        ext = (image.name.rsplit(".", 1)[-1] or "").lower()
        with st.spinner("Reading the image with OpenAI..."):

            try:
                _system, _prompt = solve_image_prompt(subject)
                answer = analyze_image(
                    image.getvalue(),
                    IMAGE_MIME[ext],
                    _prompt,
                    _system,
                )
            except Exception as exc:
                st.error(f"Vision request failed: {exc}")
            else:
                st.markdown(answer)
