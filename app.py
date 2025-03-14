import streamlit as st
import joblib

# Load the trained model and vectorizer
model = joblib.load("phishing_detector.pkl")
vectorizer = joblib.load("vectorizer.pkl")  # Load the same feature extractor

# Title
st.title("🔍 Phishing URL Detector")

# Input field
url_input = st.text_input("Enter a URL:")

if st.button("Predict"):
    if url_input:
        # Convert the input URL to feature vector using the same method as training
        input_vector = vectorizer.transform([url_input])

        # Make a prediction
        prediction = model.predict(input_vector)[0]

        # Show result
        if prediction == 1:
            st.error("🚨 This URL is **Phishing**!")
        else:
            st.success("✅ This URL is **Legitimate**.")
    else:
        st.warning("⚠️ Please enter a URL to check.")
