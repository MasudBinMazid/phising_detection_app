try:
    import streamlit as st
    import joblib
    import time
    import sqlite3
    import hashlib
except ModuleNotFoundError as e:
    print("Required modules are not installed. Please install them using 'pip install streamlit joblib'.")
    raise e

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

# Create user table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    credits INTEGER DEFAULT 20
)
""")

# Create history table
c.execute("""
CREATE TABLE IF NOT EXISTS history (
    username TEXT,
    url TEXT,
    status TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
)
""")
conn.commit()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Sidebar for menu
st.sidebar.title("Menu")
if "username" in st.session_state:
    st.sidebar.subheader(f"👤 {st.session_state['username']}")
    credits_placeholder = st.sidebar.empty()
    history_placeholder = st.sidebar.empty()
    
    def update_sidebar():
        credits_placeholder.write(f"💰 Credits: {st.session_state['credits']}")
        c.execute("SELECT url, status FROM history WHERE username=? ORDER BY rowid DESC LIMIT 10", (st.session_state['username'],))
        history = c.fetchall()
        history_placeholder.text("\n".join([f"🔗 {url} {'✅' if status == 'Legitimate' else '❌'}" for url, status in history]))
    
    update_sidebar()
    
    if st.sidebar.button("Buy Credits 💳"):
        st.session_state["credits"] += 10  # Adds 10 credits
        c.execute("UPDATE users SET credits=? WHERE username=?", (st.session_state["credits"], st.session_state["username"]))
        conn.commit()
        update_sidebar()
        st.success("💰 10 Credits Added Successfully!")
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# Authentication system
def login_page():
    st.subheader("🔑 Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
        user = c.fetchone()
        if user:
            st.session_state["username"] = username
            st.session_state["credits"] = user[2]
            st.success("✅ Login Successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def signup_page():
    st.subheader("🆕 Create a New Account")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    if st.button("Sign Up"):
        c.execute("SELECT * FROM users WHERE username=?", (new_username,))
        if c.fetchone():
            st.error("Username already exists. Choose a different one.")
        else:
            c.execute("INSERT INTO users (username, password, credits) VALUES (?, ?, ?)", 
                      (new_username, hash_password(new_password), 20))
            conn.commit()
            st.success("✅ Account created successfully! Please login.")

# Main page logic
if "username" not in st.session_state:
    login_page()
    signup_page()
else:
    st.subheader("🔍 Check a URL")
    url_input = st.text_input("Enter a URL to check", placeholder="https://example.com")
    if st.button("🔎 Predict"):
        if url_input and st.session_state["credits"] > 0:
            with st.spinner("Analyzing URL... 🧐"):
                time.sleep(1.5)  # Simulate loading time
                try:
                    model = joblib.load("phishing_detector.pkl")
                    vectorizer = joblib.load("vectorizer.pkl")
                    input_vector = vectorizer.transform([url_input])
                    prediction = model.predict(input_vector)[0]
                    status = "Phishing" if prediction == 1 else "Legitimate"
                    st.session_state["credits"] -= 1  # Deduct credit
                    c.execute("UPDATE users SET credits=? WHERE username=?", (st.session_state["credits"], st.session_state["username"]))
                    c.execute("INSERT INTO history (username, url, status) VALUES (?, ?, ?)", (st.session_state["username"], url_input, status))
                    conn.commit()
                    update_sidebar()
                    if prediction == 1:
                        st.error("🚨 This URL is **Phishing**! Be cautious!")
                    else:
                        st.success("✅ This URL is **Legitimate**.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        elif st.session_state["credits"] == 0:
            st.warning("⚠️ You have no credits left. Please buy more credits.")
        else:
            st.warning("⚠️ Please enter a URL to check.")
