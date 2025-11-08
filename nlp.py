import streamlit as st
import pandas as pd
import os

# Try optional imports
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


# === AI Response Function ===
def get_ai_feedback(prompt, api_key=None):
    """Try Ollama first; fallback to OpenAI. If neither available, show info message."""
    response_text = ""

    # --- Try Ollama ---
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
        except Exception:
            st.info("⚠️ Ollama not available. Using OpenAI instead...")

    # --- Try OpenAI ---
    if HAS_OPENAI and api_key:
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.success("✅ Response generated using **OpenAI GPT-4o-mini (cloud)**.")
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"❌ OpenAI error: {e}")
            return ""

    # --- If both fail ---
    st.warning("""
    ⚠️ No AI model available.

    To fix this:
    1. Either **install and run Ollama** locally  
       → https://ollama.ai/download  
       (Then run: `ollama serve`)
    2. Or **enter your OpenAI API key** below.
    """)
    return ""


# === Streamlit UI ===
st.set_page_config(page_title="Essay Scoring App", page_icon="🧠", layout="wide")

st.title("🧠 Automated Essay Scoring and Feedback System")
st.caption("Analyze your essay and get instant AI feedback.")

essay_text = st.text_area("✍️ Enter your essay below:", height=300)
user_level = st.selectbox("🎓 Select your academic level:", ["High School", "Undergraduate", "Graduate"])

# Optional OpenAI API key
api_key = st.text_input("🔑 OpenAI API Key (optional):", type="password") or os.getenv("OPENAI_API_KEY")

if st.button("Submit"):
    if not essay_text.strip():
        st.warning("Please enter your essay before submitting.")
        st.stop()

    st.info("⏳ Analyzing your essay... please wait.")

    prompt = f"""
    You are an automated essay evaluator.
    Academic Level: {user_level}
    Essay:
    {essay_text}

    Please:
    1. Give a score out of 100.
    2. Write 3–5 sentences of feedback.
    3. Rate these (0–100): Grammar, Coherence, Organization, Content Relevance.
    """

    result = get_ai_feedback(prompt, api_key)

    if result:
        st.subheader("🧾 Feedback and Score")
        st.write(result)

        # Sample mockup strengths chart
        st.subheader("📊 Essay Strength Overview (Sample)")
        strengths = {"Grammar": 85, "Coherence": 90, "Organization": 80, "Content Relevance": 75}
        st.bar_chart(strengths)
        st.success("✨ Analysis complete!")
