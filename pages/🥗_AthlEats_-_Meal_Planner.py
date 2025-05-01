import streamlit as st
import requests

# -------------------------------
# Hugging Face Model Config
# -------------------------------
MODEL_OPTIONS = {
    "🧠 Microsoft Phi-2 (small & smart)": "microsoft/phi-2",
    "⚖️ Mistral-7B Instruct (strong general model)": "mistralai/Mistral-7B-Instruct",
    "📚 TinyLlama (lightweight)": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
}

HF_TOKEN = st.secrets.get("HF_TOKEN", "")  # add your Hugging Face token to .streamlit/secrets.toml
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="🥗 AthlEats (Free via HuggingFace)", layout="centered")
st.title("🥗 AthlEats: Free Meal Planner (Hugging Face)")
st.caption("Powered by open-access models on Hugging Face 🤗")
st.markdown("---")

# -------------------------------
# Prompt Construction
# -------------------------------
st.markdown("### 🔧 Model & Athlete Setup")

model_label = st.selectbox("Choose a model to generate meal plan", list(MODEL_OPTIONS.keys()))
model_id = MODEL_OPTIONS[model_label]

col1, col2 = st.columns(2)
with col1:
    position = st.selectbox("Position", ["Outside", "Middle", "Setter", "Libero", "Opposite"])
    weight = st.number_input("Weight (kg)", 45.0, 140.0, step=1.0)
    meals_per_day = st.selectbox("Meals per day", [3, 4, 5, 6])
    goal = st.selectbox("Goal", ["Performance", "Muscle Gain", "Recovery", "Fat Loss", "Maintenance"])

with col2:
    training_type = st.selectbox("Training Type", ["Game", "Practice", "Weights", "Rest"])
    training_intensity = st.selectbox("Intensity", ["Low", "Moderate", "High", "Extreme"])
    energy = st.slider("Current energy level", 1, 10, 7)
    allergies = st.multiselect("Allergies / Restrictions", ["None", "Vegan", "Vegetarian", "Dairy-Free", "Gluten-Free", "Nut-Free"])

generate = st.button("🧠 Generate Meal Plan")

# -------------------------------
# Generate Prompt + Call API
# -------------------------------
if generate:
    st.markdown("---")
    st.info("Generating meal plan using Hugging Face...")

    allergy_text = ", ".join(allergies) if allergies else "None"

    prompt = f"""
You are a performance dietitian. Build a day-long meal plan for a volleyball player with this profile:
- Position: {position}
- Weight: {weight}kg
- Meals per day: {meals_per_day}
- Energy level: {energy}/10
- Goal: {goal}
- Training: {training_type} ({training_intensity} intensity)
- Allergies or restrictions: {allergy_text}

Respond with:
1. A full list of meals and times
2. Nutritional justification for each major item
3. Foods or patterns to avoid today
"""

    # Call Hugging Face Inference API
    HF_API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    with st.spinner("⏳ Querying model..."):
        try:
            response = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": prompt})
            result = response.json()

            if isinstance(result, dict) and "error" in result:
                st.error(f"❌ API Error: {result['error']}")
            elif isinstance(result, list):
                st.success("✅ Meal plan generated!")
                st.markdown("### 📋 Suggested Meal Plan")
                st.markdown(result[0]["generated_text"])
            else:
                st.warning("⚠️ Unexpected response format")
                st.json(result)
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Built for Crandall Chargers • Free AI via HuggingFace • 2025")

