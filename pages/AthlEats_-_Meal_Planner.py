import streamlit as st
import os
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a professional sports dietitian."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)

plan = response.choices[0].message.content

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="🏐 Team Meal Plan Assistant", layout="centered")
st.title("🏐 Team Meal Plan Generator")
st.markdown("Answer the questions below to receive a personalized, metabolically-optimized meal plan for your volleyball athletes.")
st.markdown("---")

# -------------------------------
# Input Section
# -------------------------------
st.subheader("📋 Athlete Profile")
col1, col2 = st.columns(2)
with col1:
    energy_level = st.slider("Energy level today?", 1, 10, 5)
    weight = st.number_input("Body weight (kg)", 40.0, 160.0, step=0.5)
with col2:
    position = st.selectbox("Volleyball position", ["Outside", "Middle", "Setter", "Libero", "Opposite", "Other"])
    fitness_goal = st.selectbox("Primary goal", ["Performance", "Muscle Gain", "Recovery", "Fat Loss", "Maintenance"])

# -------------------------------
# Training Context
# -------------------------------
st.subheader("🏋️ Game / Training Day Info")

col3, col4 = st.columns(2)
with col3:
    training_type = st.selectbox("Type of day", ["Practice", "Game", "Weights", "Rest"])
    training_level = st.selectbox("Intensity", ["Low", "Moderate", "High", "Extreme"])
    training_time = st.time_input("Activity start time")
with col4:
    wake_time = st.time_input("Wake-up time")
    sleep_time = st.time_input("Bedtime")
    meals_required = st.selectbox("Meals per day", [3, 4, 5, 6])
    allergies = st.multiselect("Dietary restrictions", ["None", "Dairy-Free", "Gluten-Free", "Nut-Free", "Vegan", "Vegetarian"])

# -------------------------------
# Prompt Construction
# -------------------------------
prompt = f"""
You are a performance nutritionist for volleyball athletes.

Please create a full-day meal plan for a {weight}kg volleyball {position}.
Energy level: {energy_level}/10.
Goal: {fitness_goal.lower()}.

Today is a {training_type.lower()} day with {training_level.lower()} intensity, starting at {training_time}.
The athlete wakes at {wake_time} and goes to bed at {sleep_time}, and eats {meals_required} meals per day.
Their dietary restrictions are: {', '.join(allergies) if allergies else 'None'}.

Structure the results by:
1. 📅 **Meal plan with timing** — list specific foods at each meal (with time), aligned with best metabolic and performance outcomes based on training and recovery windows.
2. 🚫 **What to avoid** — list specific foods or habits this athlete should avoid today based on their profile.

Be specific and consider carbohydrate timing, hydration, digestion, and recovery needs.
"""

# -------------------------------
# Generate Meal Plan
# -------------------------------
st.markdown("---")
if st.button("🧠 Generate Meal Plan with ChatGPT"):
    with st.spinner("Generating meal plan..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a performance dietitian for elite volleyball athletes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            reply = response.choices[0].message.content
            st.success("✅ Meal plan generated!")
            st.markdown("### 🥗 Meal Plan + Guidelines")
            st.markdown(reply)
        except Exception as e:
            st.error(f"⚠️ Failed to generate meal plan: {e}")
else:
    st.info("Fill out the form and click 'Generate Meal Plan' to get started.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Built for high-performance athletes • Crandall Chargers Volleyball © 2025")
