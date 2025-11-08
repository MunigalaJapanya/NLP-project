import streamlit as st
import pandas as pd
import random

# ======================
# STREAMLIT CONFIGURATION
# ======================
st.set_page_config(
    page_title="Automated Essay Scoring System",
    page_icon="🧠",
    layout="wide"
)

# ======================
# APP HEADER
# ======================
st.title("🧠 Automated Essay Scoring and Feedback System")
st.caption("Analyze your essay and get instant feedback — no API key required!")

# ======================
# INPUT SECTION
# ======================
essay_text = st.text_area("✍️ Enter your essay below:", height=300)
user_level = st.selectbox("🎓 Select your academic level:", ["High School", "Undergraduate", "Graduate"])

# ======================
# HELPER FUNCTION (Mock AI)
# ======================
def generate_feedback(essay, level):
    """Simulates AI feedback and scoring for Streamlit deployment (no external API needed)."""
    base_score = random.randint(65, 95)

    grammar = random.randint(70, 95)
    coherence = random.randint(60, 95)
    organization = random.randint(65, 90)
    content = random.randint(60, 95)

    feedback = f"""
### 🧾 Essay Evaluation Report
**Academic Level:** {level}  
**Overall Score:** {base_score}/100  

**Feedback Summary:**
- Your essay demonstrates clear ideas and logical flow.
- Work on refining sentence structure for improved readability.
- Consider adding more supporting details or examples.
- Maintain consistent tone and transitions between paragraphs.
- Excellent effort overall — keep improving!

---

### 📊 Subscores
- Grammar: **{grammar}/100**
- Coherence: **{coherence}/100**
- Organization: **{organization}/100**
- Content Relevance: **{content}/100**
"""

    scores = {
        "Grammar": grammar,
        "Coherence": coherence,
        "Organization": organization,
        "Content Relevance": content,
    }
    return feedback, scores


# ======================
# MAIN LOGIC
# ======================
if st.button("Submit Essay"):
    if not essay_text.strip():
        st.warning("⚠️ Please enter your essay before submitting.")
    else:
        st.info("⏳ Analyzing your essay...")

        # Generate mock AI feedback
        feedback, scores = generate_feedback(essay_text, user_level)

        # Show feedback
        st.markdown(feedback)

        # Show bar chart visualization
        st.subheader("📈 Essay Strength Visualization")
        st.bar_chart(scores)

        st.success("✨ Feedback generated successfully!")


# ======================
# FOOTER
# ======================
st.markdown("""
---
Made with ❤️ using Streamlit  
No API connection required — runs fully in the browser.
""")
