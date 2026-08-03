import streamlit as st

st.set_page_config(page_title="Racket Sports Tracker", page_icon="🏓", layout="wide")

st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF4B4B, #FF8C42);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .sport-card {
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.15s;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🏓 Racket Sports Tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Log your matches across table tennis, badminton, and tennis — and track your progress over time.</p>', unsafe_allow_html=True)

st.write("")
col1, col2, col3 = st.columns(3)

with col1:
    tt_selected = st.button("🏓 Table Tennis", use_container_width=True)
with col2:
    bad_selected = st.button("🏸 Badminton", use_container_width=True)
with col3:
    tennis_selected = st.button("🎾 Tennis", use_container_width=True)

if "sport" not in st.session_state:
    st.session_state.sport = "Table Tennis"

if tt_selected:
    st.session_state.sport = "Table Tennis"
elif bad_selected:
    st.session_state.sport = "Badminton"
elif tennis_selected:
    st.session_state.sport = "Tennis"

st.write("")
st.info(f"**Selected sport:** {st.session_state.sport}")

import pandas as pd

st.write("---")
st.subheader(f"Log a {st.session_state.sport} match")

if "matches" not in st.session_state:
    st.session_state.matches = []

with st.form("match_form"):
    opponent = st.text_input("Opponent name")
    your_score = st.number_input("Your score", min_value=0, step=1)
    opponent_score = st.number_input("Opponent's score", min_value=0, step=1)
    match_date = st.date_input("Date")
    submitted = st.form_submit_button("Log Match")

    if submitted:
        result = "Win" if your_score > opponent_score else "Loss" if your_score < opponent_score else "Draw"
        st.session_state.matches.append({
            "Sport": st.session_state.sport,
            "Date": match_date,
            "Opponent": opponent,
            "Your Score": your_score,
            "Opponent Score": opponent_score,
            "Result": result
        })
        st.success(f"Match logged! Result: {result}")

st.write("---")
st.subheader("Match History")

if st.session_state.matches:
    df = pd.DataFrame(st.session_state.matches)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No matches logged yet. Log your first match above!")
