import streamlit as st
import pandas as pd
import httpx
import os

# === Optional Imports ===
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


# === Function: Get Response ===
def stream_response(prompt, api_key=None):
    response_text = ""

    # --- Try Ollama first (local model) ---
    if HAS_OLLAMA:
        try:
            stream = ollama.chat(model="llama3.1:8b",
                                 messages=[{"role": "user", "content": prompt}],
                                 stream=True)
            for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    response_text += chunk["message"]["content"]
            st.success("✅ Response generated using **Ollama (local)**.")
            return response_text
        except httpx.ConnectError:
            st.warning("⚠️ Could not connect to Ollama. Falling back to OpenAI.")
        except Exception as e:
            st.error(f"❌ Ollama error: {e}")
    
    # --- Fallback: OpenAI (Cloud model) ---
    if HAS_OPENAI and api_key:
        try:
            client = OpenAI(api_key=api_key)
            response_text = ""
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            response_container = st.empty()
            for chunk in stream:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    response_text += delta.content
                    response_container.write(response_text)
            st.success("✅ Response generated using **OpenAI GPT-4o-mini (cloud)**.")
            return response_text
        except Exception as e:
            st.error(f"❌ OpenAI error: {e}")
            return ""
    
    # --- If nothing works ---
    st.error("❌ No model available. Please run Ollama locally or enter a valid OpenAI API key.")
    return ""


# === Streamlit UI ===
st.set_page_config(page_title="Essay Scoring App", page_icon="🧠", layout="wide")

st.title("🧠 Automated Essay Scoring and Feedback System")
st.caption("Analyze your essay and get instant feedback using AI (Ollama or OpenAI).")

# --- User Inputs ---
essay_text = st.text_area("✍️ Enter your essay below:", height=300)
user_level = st.selectbox("🎓 Select your academic level:",
                          ["High School", "Undergraduate", "Graduate"])

# Automatically detect API key (from input or environment)
api_key = st.text_input("🔑 Enter your OpenAI API Key (optional for cloud):", type="password") or os.getenv("OPENAI_API_KEY")

# --- Button Action ---
if st.button("Submit"):
    if not essay_text.strip():
        st.warning("Please enter your essay before submitting.")
        st.stop()

    st.info("⏳ Analyzing your essay... please wait.")

    # Build prompt
    prompt = f"""
    You are an automated essay scoring assistant.
    Essay Level: {user_level}
    Essay Text: {essay_text}

    Please:
    1. Provide an overall score (out of 100).
    2. Give 4–5 sentences of detailed feedback.
    3. Rate these aspects (0–100): Grammar, Coherence, Organization, Content Relevance.
    """

    # Get model response
    response = stream_response(prompt, api_key=api_key)

    # Display results
    if response:
        st.subheader("🧾 Score and Feedback")
        st.write(response)

        # Mockup strengths chart
        st.subheader("📊 Essay Strength Overview")
        strengths = {"Grammar": 85, "Coherence": 90, "Organization": 80, "Content Relevance": 75}
        st.bar_chart(strengths)

        cols = st.columns(len(strengths))
        for i, (skill, score) in enumerate(strengths.items()):
            cols[i].metric(skill, f"{score}/100")

        st.success("✨ Analysis complete!")
