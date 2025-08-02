import requests
import pandas as pd
import streamlit as st
import numpy as np
from cricketapidata import *
from datetime import datetime
import time
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Auto refresh the Streamlit app every 60 seconds (60000 ms)
st_autorefresh(interval=30000, limit=None, key="datarefresh")

# Load external CSS
with open("cricket.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#st.set_page_config(layout="wide")

# Sidebar single-date selector
#st.sidebar.header("Filter by Match Date")
today = datetime.today().date()
# selected_date = st.date_input("Select match date:", today)
selected_date = today

matchData = returnMatches(selected_date)


# Banner
st.markdown('<div class="welcome-banner">Welcome to Fleet Cricket Club</div>', unsafe_allow_html=True)

if matchData.empty:
    st.markdown("""
                <div class="match-banner")>
                <div class="match-team">No fixtures to display</div>
                </div>
                """, unsafe_allow_html=True)
else:
    matchData = matchData.sort_values(by='my_team_name')

    st.markdown(f"""
                <div class="match-banner")>
                <div class="match-team">Showing fixtures for: {selected_date.strftime("%A %d %B")}</div>
                </div>
                """, unsafe_allow_html=True)


    for match in matchData.to_dict(orient='records'):
        st.markdown(f"""
        <div class="match-banner">
            <div class="match-team">{match['homelogo']} {match['home_team_name']}<br/><i>{match['home_summary']}</i></div>
            <div class="vs-team">{match['result']}</div>
            <div class="match-team">{match['awaylogo']} {match['away_team_name']} <br/><i>{match['away_summary']}</i></div>
        </div>
        """, unsafe_allow_html=True)




#st.caption(f"Last updated: {pd.Timestamp.now().strftime('%H:%M:%S')}")

clock_html = """
<div id="clock" class="caption-clock"></div>

<script>
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById('clock').innerText = timeString;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""

# Display the HTML with embedded JavaScript
#components.html(clock_html, height=100)





#matchData = matchData[['id', 'my_team_name', 'oppo_team_name', 'venue']]
#st.dataframe(matchData)





