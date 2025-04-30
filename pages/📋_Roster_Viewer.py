import streamlit as st
import pandas as pd
import os
from PIL import Image

# Set title
st.title("📋 2024–25 Team Roster Viewer")

# File paths
roster_csv = "roster 24-25/team info.csv"
headshot_dir = "roster 24-25"

# Load data
try:
    df = pd.read_csv(roster_csv)
except FileNotFoundError:
    st.error("Could not find 'team info.csv'. Make sure it is in the 'roster 24-25' folder.")
    st.stop()

# Sort by jersey number extracted from headshot filenames
headshots = {
    f.split(" - ")[1].replace(".jpg", "").strip(): f
    for f in os.listdir(headshot_dir)
    if f.endswith(".jpg") and " - " in f
}

# Display player cards
for _, row in df.iterrows():
    name = row["name"]
    st.markdown("----")

    # Layout in two columns
    col1, col2 = st.columns([1, 3])
    
    # Headshot
    image_file = headshots.get(name)
    if image_file:
        img_path = os.path.join(headshot_dir, image_file)
        img = Image.open(img_path)
        col1.image(img, width=150, caption=name)
    else:
        col1.warning("No image found")

    # Info
    col2.markdown(f"**Name:** {name}")
    col2.markdown(f"**Position:** {row['position']}")
    col2.markdown(f"**Height:** {row['height']}")
    col2.markdown(f"**Year of Eligibility:** {row['year of eligibility']}")
    col2.markdown(f"**Hometown:** {row['hometown']}")
