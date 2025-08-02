import streamlit as st
import requests
import time

# Initialize session state
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()

# Time since last run
elapsed = time.time() - st.session_state.last_run

# If 60s passed, update timestamp and rerun
if elapsed > 60:
    st.session_state.last_run = time.time()
    st.experimental_rerun()

# Display data (simulate API call)
@st.cache_data(ttl=60)
def fetch_data():
    response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
    return response.json()

data = fetch_data()

# Show data
st.write(data)

# Optional: show countdown
countdown = int(60 - elapsed)
st.markdown(f"⏳ Refreshing in **{countdown}** seconds")
