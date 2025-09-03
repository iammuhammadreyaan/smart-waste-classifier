import streamlit as st
import requests
from PIL import Image
import io

# 🔑 Azure details (replace with your own)
import os
import streamlit as st

subscription_key = st.secrets["AZURE_KEY"]
endpoint = st.secrets["AZURE_ENDPOINT"] + "/vision/v3.2/analyze"


headers = {"Ocp-Apim-Subscription-Key": subscription_key}
params = {"visualFeatures": "Tags,Description"}

# Waste classification logic
def classify_waste(tags):
    recyclable = {"plastic", "glass", "metal", "paper", "cardboard"}
    compost = {"food", "fruit", "vegetable", "organic"}
    
    tag_set = set([t['name'].lower() for t in tags])
    
    if tag_set & recyclable:
        return "♻️ Recyclable", "Dispose in recycle bin. Rinse if needed."
    elif tag_set & compost:
        return "🌱 Compost", "Dispose in compost bin. Good for soil."
    else:
        return "🗑️ General Waste", "Dispose in general waste bin."

# Streamlit UI
st.title("🌍 Smart Waste Classifier (Eco Helper)")

uploaded_file = st.file_uploader("Upload an image of waste", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes = img_bytes.getvalue()

    # Send to Azure CV API
    response = requests.post(endpoint, headers=headers, params=params, data=img_bytes)
    
    if response.status_code == 200:
        data = response.json()
        tags = data.get("tags", [])
        
        # Classify waste
        category, tip = classify_waste(tags)
        
        st.subheader("Result")
        st.write("Category:", category)
        st.write("Tip:", tip)

        st.subheader("Azure Tags Detected")
        st.write([t['name'] for t in tags])
    else:
        st.error("Error calling Azure API: " + response.text)
