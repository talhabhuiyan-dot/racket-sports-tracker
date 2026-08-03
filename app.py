import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Racket Sports Tracker", page_icon="🏓", layout="wide")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("racket_tracker.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT,
            date TEXT,
            opponent TEXT,
            your_score INTEGER,
            opponent_score INTEGER,
            result TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            player_name TEXT,
            starting_rating INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_match(sport, date, opponent, your_score, opponent_score, result):
    conn = sqlite3.connect("racket_tracker.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO matches (sport, date, opponent, your_score, opponent_score, result) VALUES (?, ?, ?, ?, ?, ?)",
        (sport, str(date), opponent, your_score, opponent_score, result)
    )
    conn.commit()
    conn.close()

def load_matches():
    conn = sqlite3.connect("racket_tracker.db")
    df = pd.read_sql_query("SELECT * FROM matches", conn)
    conn.close()
    return df

def save_profile(name, starting_rating):
    conn = sqlite3.connect("racket_tracker.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO profile (id, player_name, starting_rating) VALUES (1, ?, ?)",
        (name, starting_rating)
    )
    conn.commit()
    conn.close()

def load_profile():
    conn = sqlite3.connect("racket_tracker.db")
    c = conn.cursor()
    c.execute("SELECT player_name, starting_rating FROM profile WHERE id = 1")
    row = c.fetchone()
    conn.close()
    return row if row else ("", 1000)

init_db()

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

saved_name, saved_rating = load_profile()

with st.form("profile_form"):
    name_input = st.text_input("Your name", value=saved_name)
    starting_rating_input = st.slider(
        "Self-assessed starting skill level (1000 = beginner, 1500 = intermediate, 2000+ = advanced)",
        min_value=800, max_value=2500, value=saved_rating, step=25
    )
    profile_submitted = st.form_submit_button("Save Profile")

    if profile_submitted:
        save_profile(name_input, starting_rating_input)
        st.success(f"Profile saved for {name_input}!")
        st.rerun()

if saved_name:
    st.info(f"Currently tracking matches for: **{saved_name}**")

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

with st.form("match_form"):
    opponent = st.text_input("Opponent name")
    your_score = st.number_input("Your score", min_value=0, step=1)
    opponent_score = st.number_input("Opponent's score", min_value=0, step=1)
    match_date = st.date_input("Date")
    submitted = st.form_submit_button("Log Match")

    if submitted:
        result = "Win" if your_score > opponent_score else "Loss" if your_score < opponent_score else "Draw"
        save_match(st.session_state.sport, match_date, opponent, your_score, opponent_score, result)
        st.success(f"Match logged! Result: {result}")
        st.rerun()

# ---------------------------------------------------------------------------
# Match history
# ---------------------------------------------------------------------------
st.write("---")
st.subheader("Match History")

history_df = load_matches()

if not history_df.empty:
    st.dataframe(history_df, use_container_width=True, hide_index=True)
else:
    st.info("No matches logged yet. Log your first match above!")

# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------
st.write("---")
st.subheader("Your Ratings")

if not history_df.empty:
    _, starting_rating = load_profile()

    rating_rows = []
    for sport_name in history_df["sport"].unique():
        sport_matches = history_df[history_df["sport"] == sport_name]
        wins = (sport_matches["result"] == "Win").sum()
        losses = (sport_matches["result"] == "Loss").sum()
        draws = (sport_matches["result"] == "Draw").sum()
        total = len(sport_matches)
        rating = starting_rating + (wins * 25) - (losses * 20)

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

st.write("---")
st.subheader("Rating Progress Over Time")

if not history_df.empty:
    import plotly.express as px

    _, starting_rating = load_profile()

    progress_df = history_df.sort_values("date").copy()
    progress_df["rating_change"] = progress_df["result"].map({"Win": 25, "Loss": -20, "Draw": 0})

    progress_rows = []
    for sport_name in progress_df["sport"].unique():
        sport_matches = progress_df[progress_df["sport"] == sport_name].sort_values("date")
        running_rating = starting_rating
        for _, row in sport_matches.iterrows():
            running_rating += row["rating_change"]
            progress_rows.append({
                "Sport": sport_name,
                "Date": row["date"],
                "Rating": running_rating
            })

    progress_chart_df = pd.DataFrame(progress_rows)

    fig = px.line(
        progress_chart_df,
        x="Date",
        y="Rating",
        color="Sport",
        markers=True
    )
    fig.update_layout(yaxis_title="Rating", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Log some matches to see your rating progress.")
    
