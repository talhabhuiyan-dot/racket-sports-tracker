import streamlit as st
import pandas as pd

st.set_page_config(page_title="Racket Sports Tracker", page_icon="🏓", layout="wide")

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
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
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🏓 Racket Sports Tracker</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Log your matches across table tennis, badminton, and tennis — and track your progress over time.</p>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Player profile
# ---------------------------------------------------------------------------
st.write("---")
st.subheader("Your Profile")

if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "starting_rating" not in st.session_state:
    st.session_state.starting_rating = 1000

with st.form("profile_form"):
    name_input = st.text_input("Your name", value=st.session_state.player_name)
    starting_rating_input = st.slider(
        "Self-assessed starting skill level (1000 = beginner, 1500 = intermediate, 2000+ = advanced)",
        min_value=800, max_value=2500, value=st.session_state.starting_rating, step=25
    )
    profile_submitted = st.form_submit_button("Save Profile")

    if profile_submitted:
        st.session_state.player_name = name_input
        st.session_state.starting_rating = starting_rating_input
        st.success(f"Profile saved for {name_input}!")

if st.session_state.player_name:
    st.info(f"Currently tracking matches for: **{st.session_state.player_name}**")

# ---------------------------------------------------------------------------
# Sport selection
# ---------------------------------------------------------------------------
st.write("---")
st.subheader("Select a Sport")

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

# ---------------------------------------------------------------------------
# Match logging form
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Match history
# ---------------------------------------------------------------------------
st.write("---")
st.subheader("Match History")

if st.session_state.matches:
    history_df = pd.DataFrame(st.session_state.matches)
    st.dataframe(history_df, use_container_width=True, hide_index=True)
else:
    st.info("No matches logged yet. Log your first match above!")

# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------
st.write("---")
st.subheader("Your Ratings")

if st.session_state.matches:
    df = pd.DataFrame(st.session_state.matches)

    rating_rows = []
    for sport_name in df["Sport"].unique():
        sport_matches = df[df["Sport"] == sport_name]
        wins = (sport_matches["Result"] == "Win").sum()
        losses = (sport_matches["Result"] == "Loss").sum()
        draws = (sport_matches["Result"] == "Draw").sum()
        total = len(sport_matches)
        rating = st.session_state.starting_rating + (wins * 25) - (losses * 20)

        rating_rows.append({
            "Sport": sport_name,
            "Matches Played": total,
            "Wins": wins,
            "Losses": losses,
            "Draws": draws,
            "Rating": rating
        })

    ratings_df = pd.DataFrame(rating_rows)
    st.dataframe(ratings_df, use_container_width=True, hide_index=True)
else:
    st.info("Log some matches to see your ratings.")
    
