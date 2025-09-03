import streamlit as st
import requests
from PIL import Image
import io

# Page config
st.set_page_config(page_title="Smart Waste Classifier", page_icon="🌍", layout="centered")

# Header
st.markdown("<h1 style='text-align: center;'>🌍 Smart Waste Classifier</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>AI-powered eco-helper to guide waste disposal</p>", unsafe_allow_html=True)

# Azure secrets
subscription_key = st.secrets["AZURE_KEY"]
endpoint = st.secrets["AZURE_ENDPOINT"] + "/vision/v3.2/analyze"

headers = {
    "Ocp-Apim-Subscription-Key": subscription_key,
    "Content-Type": "application/octet-stream"
}
params = {"visualFeatures": "Tags,Description"}

# Waste classification logic
def classify_waste(tags):
    recyclable = {"plastic", "glass", "metal", "paper", "cardboard"}
    compost = {"food", "fruit", "vegetable", "organic"}

    tag_set = set([t['name'].lower() for t in tags])
    if tag_set & recyclable:
        return "♻️ Recyclable", "Dispose in recycle bin. Rinse if needed.", "#4CAF50"
    elif tag_set & compost:
        return "🌱 Compost", "Dispose in compost bin. Great for soil.", "#795548"
    else:
        return "🗑️ General Waste", "Dispose in general waste bin.", "#9E9E9E"

# Tabs for better UX
tab1, tab2, tab3 = st.tabs(["📸 Upload", "📊 Results", "ℹ️ About"])

with tab1:
    uploaded_file = st.file_uploader("Upload an image of waste", type=["jpg", "jpeg", "png"])

with tab2:
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        # Convert image to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG")
        img_bytes = img_bytes.getvalue()

        # Call Azure
        response = requests.post(endpoint, headers=headers, params=params, data=img_bytes)

        if response.status_code == 200:
            data = response.json()
            tags = data.get("tags", [])

            # Classification
            category, tip, color = classify_waste(tags)

            # Result card
            st.markdown(
                f"<div style='background-color:{color}; padding:20px; border-radius:10px; text-align:center; color:white;'>"
                f"<h2>{category}</h2>"
                f"<p>{tip}</p>"
                "</div>",
                unsafe_allow_html=True
            )

            # Confidence section
            st.subheader("Confidence Scores")
            for t in tags[:5]:
                st.progress(t["confidence"])
                st.write(f"**{t['name'].capitalize()}**: {t['confidence']*100:.1f}%")
        else:
            st.error("Error calling Azure API: " + response.text)

with tab3:
    st.markdown("### About this App")
    st.write(
        """
        This app uses **Azure Computer Vision** to analyze waste images  
        and classify them as ♻️ Recyclable, 🌱 Compost, or 🗑️ General Waste.  

        Built with **Streamlit** + **Python**, designed to promote eco-friendly habits.  
        """
    )

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color: gray;'>Made with ❤️ by Muhammad Reyaan</p>", unsafe_allow_html=True)
