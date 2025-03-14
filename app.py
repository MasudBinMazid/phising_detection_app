try:
    import streamlit as st
    import joblib
    from PIL import Image
    import time
    import base64
except ModuleNotFoundError as e:
    print("Required modules are not installed. Please install them using 'pip install streamlit joblib pillow'.")
    raise e

# Load the trained model and vectorizer
try:
    model = joblib.load("phishing_detector.pkl")
    vectorizer = joblib.load("vectorizer.pkl")  # Load the same feature extractor
except FileNotFoundError:
    print("Model or vectorizer file not found. Ensure 'phishing_detector.pkl' and 'vectorizer.pkl' exist in the directory.")
    raise

# Set page config
st.set_page_config(page_title="Phishing URL Detector", page_icon="🔍", layout="centered")

# Custom background image
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode()
        bg_image = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
        }}
        </style>
        """
        st.markdown(bg_image, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Background image not found. Please provide a valid image path.")

# Uncomment the next line and add a valid image path to enable a background image
# add_bg_from_local("background.jpg")

# Title
st.markdown("<h1 style='text-align: center; color: #000000;'>🔍 Phishing URL Detector</h1>", unsafe_allow_html=True)

# Input field with styling
st.markdown("<h3 style='text-align: center; color: #000000;'>Enter a URL to check</h3>", unsafe_allow_html=True)
url_input = st.text_input("", placeholder="https://example.com", key="url_input")

# Prediction button with enhanced design
if st.button("🔎 Predict", help="Click to analyze the URL"):
    if url_input:
        with st.spinner("Analyzing URL... 🧐"):
            time.sleep(1.5)  # Simulate loading time
            try:
                # Convert the input URL to feature vector
                input_vector = vectorizer.transform([url_input])
                # Make a prediction
                prediction = model.predict(input_vector)[0]
                # Show result
                if prediction == 1:
                    st.error("🚨 This URL is **Phishing**! Be cautious!")
                    st.markdown("<h3 style='text-align: center; color: red;'>⚠️ Phishing Alert!</h3>", unsafe_allow_html=True)
                else:
                    st.success("✅ This URL is **Legitimate**.")
                    st.markdown("<h3 style='text-align: center; color: green;'>✔️ Safe to Visit</h3>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("⚠️ Please enter a URL to check.")