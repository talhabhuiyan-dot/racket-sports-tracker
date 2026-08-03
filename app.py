import streamlit as st

st.set_page_config(page_title="Racket Sports Tracker", layout="wide")

st.title("🏓 Racket Sports Tracker")
st.write("Log your matches across table tennis, badminton, and tennis, and track your progress over time.")

sport = st.selectbox("Select a sport", ["Table Tennis", "Badminton", "Tennis"])
st.write("You selected:", sport)
