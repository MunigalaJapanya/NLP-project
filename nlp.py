import streamlit as st
import pandas as pd
import httpx
import os

# Optional imports
try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# Function to get response
def stream_response(prompt, use_ollama=True, api_key=None):
    response_text = ""

    if use_ollama and HAS_OLLAMA:
        try:
            stream = ollama.chat(model="llama3.1:8b",
                                 messages=[{"role": "user", "content": prompt}],
                                 stream=True)
            for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    content = chunk["message"]["content"]
                    response_text += content
            return response_text
        except httpx.ConnectError:
            st.warning("⚠️ Could not connect to Ollama. Falling back to OpenAI.")
            use_ollama = False

    if not use_ollama and HAS_OPENAI:
        if not api_key:
            st.error("❌ OpenAI API key missing. Please provide it.")
            return ""
        client = OpenAI(api_key=api_key)
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                response_text += delta.content
        return response_text

    return "⚠️ No model available. Install Ollama or enter OpenAI API key."


# === Streamlit UI ===
st.set_page_config(page_title="Essay Scoring App", layout="wide")

st.title("🧠 Automated Essay Scoring and Feedback System")

essay_text = st.text_area("✍️ Enter your essay below:", height=300)
user_level = st.selectbox("🎓 Select your academic level:",
                          ["High School", "Undergraduate", "Graduate"])
api_key = st.text_input("🔑 (Optional) Enter OpenAI API Key:", type="password")

if st.button("Submit"):
    if essay_text.strip() == "":
        st.warning("Please enter your essay before submitting.")
        st.stop()

    st.info("Analyzing your essay... please wait ⏳")

    prompt = f"""
    Essay Level: {user_level}
    Essay Text: {essay_text}

    Please:
    1. Provide a score (out of 100)
    2. Give 4–5 sentences of detailed feedback
    3. Rate the following (0–100): Grammar, Coherence, Organization, Content Relevance.
    """

    response = stream_response(prompt, use_ollama=True, api_key=api_key)

    st.subheader("🧾 Score and Feedback")
    st.write(response)

    # Simple visualization (placeholder)
    st.subheader("📊 Essay Strength Overview")
    strengths = {"Grammar": 85, "Coherence": 90, "Organization": 80, "Content Relevance": 75}
    st.bar_chart(strengths)

    cols = st.columns(len(strengths))
    for i, (skill, score) in enumerate(strengths.items()):
        cols[i].metric(skill, f"{score}/100")

    st.success("✨ Analysis complete!")
