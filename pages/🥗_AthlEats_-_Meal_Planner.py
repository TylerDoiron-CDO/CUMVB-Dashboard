import streamlit as st
import openai
import os
from datetime import datetime

# Secure API key
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="🥗 AthlEats: Smart Meal Planner", layout="centered")
st.title("🥗 AthlEats: Smart Meal Planner")
st.caption("Designed for high-performance volleyball athletes.")
st.markdown("---")

# -------------------------------
# Input Form
# -------------------------------
with st.form("meal_plan_form"):
    st.markdown("### 👤 Athlete Profile")
    col1, col2 = st.columns(2)
    with col1:
        energy_level = st.slider("Energy level today", 1, 10, 7)
        weight = st.number_input("Weight (kg)", 40.0, 160.0, step=0.5)
        wake_time = st.time_input("Wake-up time", value=datetime.strptime("07:00", "%H:%M").time())
        sleep_time = st.time_input("Bedtime", value=datetime.strptime("22:30", "%H:%M").time())
    with col2:
        position = st.selectbox("Position", ["Outside", "Middle", "Setter", "Libero", "Opposite", "Other"])
        goal = st.selectbox("Primary goal", ["Performance", "Muscle Gain", "Recovery", "Fat Loss", "Maintenance"])
        meals_per_day = st.selectbox("Meals per day", [3, 4, 5, 6])
        allergies = st.multiselect("Dietary restrictions", ["None", "Dairy-Free", "Gluten-Free", "Nut-Free", "Vegan", "Vegetarian"])

    st.markdown("---")
    st.markdown("### 🏋️ Game / Training Day Info")
    col3, col4 = st.columns(2)
    with col3:
        training_type = st.selectbox("Activity type", ["Practice", "Game", "Weights", "Rest"])
        training_level = st.selectbox("Intensity", ["Low", "Moderate", "High", "Extreme"])
    with col4:
        training_time = st.time_input("Activity start time", value=datetime.strptime("10:00", "%H:%M").time())

    submitted = st.form_submit_button("🧠 Generate Meal Plan", type="primary")

# -------------------------------
# Generate Prompt + GPT Response
# -------------------------------
if submitted:
    st.markdown("---")
    st.info("🔄 Generating personalized meal plan...")
    try:
        prompt = f"""
You are a performance nutritionist.

Build a meal plan for a {weight}kg volleyball {position} with an energy level of {energy_level}/10.
Today's activity is a {training_type} session at {training_level} intensity, starting at {training_time}.
Wake-up: {wake_time}, Bedtime: {sleep_time}, {meals_per_day} meals per day.
Dietary restrictions: {', '.join(allergies) if allergies else "None"}.
Primary goal: {goal.lower()}.

Respond with:
1. 🥗 A complete meal plan — include timing, exact foods, and why each is recommended.
2. 🔬 Optimize nutrient timing around metabolic outcomes (recovery, energy, digestion).
3. ❌ List what foods/habits this athlete should avoid today based on their profile.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional sports dietitian."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        plan = response.choices[0].message.content
        st.success("✅ Meal plan generated successfully!")
        st.markdown("### 📋 Personalized Meal Plan")
        st.markdown(plan)

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Built for Crandall Chargers Volleyball • Powered by OpenAI • © 2025")
