import streamlit as st

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="🏐 Team Meal Plan Assistant", layout="centered")
st.title("🏐 Team Meal Plan Generator")
st.markdown("Answer the following to generate a full-day meal plan for your volleyball athletes.")
st.markdown("---")

# -------------------------------
# Input Fields
# -------------------------------
st.subheader("📋 Athlete Profile")

col1, col2 = st.columns(2)
with col1:
    energy_level = st.slider("How is your energy level today?", 1, 10, 5)
    weight = st.number_input("Current body weight (kg)", min_value=40.0, max_value=160.0, step=0.5)

with col2:
    position = st.selectbox("What is your volleyball position?", ["Outside", "Middle", "Setter", "Libero", "Opposite", "Other"])
    fitness_goal = st.selectbox("Primary fitness goal", ["Performance", "Muscle Gain", "Recovery", "Fat Loss", "Maintenance"])

# -------------------------------
# Training Context
# -------------------------------
st.subheader("🏋️ Training Day Info")

col3, col4 = st.columns(2)
with col3:
    training_type = st.selectbox("What type of activity today?", ["Practice", "Game", "Weights", "Rest"])
    training_level = st.selectbox("Intensity of training", ["Low", "Moderate", "High", "Extreme"])
    training_time = st.time_input("Training start time")

with col4:
    wake_time = st.time_input("Wake-up time")
    sleep_time = st.time_input("Bedtime")
    meals_required = st.selectbox("Number of meals required", [3, 4, 5, 6])
    allergies = st.multiselect("Dietary restrictions", ["None", "Dairy-Free", "Gluten-Free", "Nut-Free", "Vegan", "Vegetarian"])

# -------------------------------
# Submit / Output Placeholder
# -------------------------------
st.markdown("---")
if st.button("🧠 Generate Meal Plan"):
    st.success("Prompt assembled! (Next step: send to GPT or custom logic)")
    st.markdown("##### 🤖 Prompt Summary")

    st.code(f"""
Create a meal plan for a {weight}kg volleyball {position} with an energy level of {energy_level}/10.
Today is a {training_type} day with {training_level} intensity, starting at {training_time}.
The athlete woke up at {wake_time} and will sleep around {sleep_time}.
Their primary goal is {fitness_goal.lower()}, and they require {meals_required} meals today.
They have the following dietary restrictions: {", ".join(allergies) if allergies else "None"}.
""", language="markdown")
else:
    st.info("Fill in the form and click 'Generate Meal Plan' to build your prompt.")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Team Meal Plan Generator • Built with Streamlit for Volleyball Performance")
