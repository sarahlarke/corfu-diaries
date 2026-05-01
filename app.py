import os
import sqlite3
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

APP_TITLE = "The Corfu Diaries"
GUEST_PASSWORD = "corfu"
ADMIN_PASSWORD = "laurenadmin"

TRIP_START = date(2026, 5, 7)
TRIP_END = date(2026, 5, 10)

GUESTS = [
    "Sarah", "Lauren", "Lyn", "Jane", "Emily", "Gemma", "Drew",
    "Sara", "Kelly", "Jessie", "Tracy", "Charlotte", "Jenny", "Louise"
]

VOTE_GUESTS = GUESTS  # people you can vote for

AWARDS = [
    "Main Character of Corfu ✨",
    "Just One More… 🍹",
    "Dancefloor Energy 💃",
    "Quote of the Trip 😂",
    "Corfu Chaos Creator 🍸",
    "Most Likely to Lose Something 👀",
    "Story of the Trip 📖",
    "Effortlessly Chic ✨",
    "Best Energy All Round 🌟",
    "The Glue 💛",
    "Ultimate Hype Woman 🙌",
    "Kindest Soul 🤍",
    "Calm in the Chaos 🧘‍♀️",
    "Lauren’s VIP 💍✨",
]

DB_PATH = "corfu_diaries.db"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #fff7f0 0%, #fdf1f5 45%, #fffaf5 100%);
    }
    .hero {
        background: rgba(255,255,255,0.78);
        padding: 2rem;
        border-radius: 28px;
        box-shadow: 0 12px 35px rgba(160, 80, 80, 0.12);
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        font-size: 3rem;
        margin-bottom: 0.3rem;
        color: #8a4f4d;
    }
    .hero p {
        font-size: 1.2rem;
        color: #6f5a57;
    }
    .card {
        background: rgba(255,255,255,0.86);
        border: 1px solid rgba(210, 160, 140, 0.25);
        padding: 1.3rem;
        border-radius: 24px;
        box-shadow: 0 8px 25px rgba(160, 80, 80, 0.08);
        margin-bottom: 1rem;
    }
    .gold {
        color: #a6783a;
        font-weight: 700;
    }
    .small-muted {
        color: #7b6a67;
        font-size: 0.95rem;
    }
    div.stButton > button {
        border-radius: 999px;
        border: 1px solid #c99f7a;
        background: #fff8f0;
        color: #7a5148;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            submitted_by TEXT,
            people TEXT,
            category TEXT,
            memory TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            submitted_by TEXT,
            said_by TEXT,
            quote TEXT,
            context TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            submitted_by TEXT,
            people TEXT,
            caption TEXT,
            file_path TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS bride_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            submitted_by TEXT,
            message TEXT,
            advice TEXT,
            favourite_memory TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS nominations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            submitted_by TEXT,
            award TEXT,
            nominee TEXT,
            reason TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            voter TEXT,
            award TEXT,
            nominee TEXT,
            UNIQUE(voter, award)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            item_type TEXT,
            item_id INTEGER,
            reaction TEXT,
            submitted_by TEXT
        )
    """)

    conn.commit()
    conn.close()


def run_query(query, params=(), fetch=False):
    conn = connect()
    if fetch:
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.admin = False
        st.session_state.user_name = None

    if st.session_state.logged_in:
        return True

    st.markdown(
        """
        <div class="hero">
            <h1>The Corfu Diaries 💍✨</h1>
            <p>One weekend. Thirteen women. Endless memories.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if Path("lauren.jpg").exists():
            st.image("lauren.jpg", use_container_width=True)
        else:
            st.info("Add Lauren’s photo as `lauren.jpg` in the same folder as this app.")

    with col2:
        st.subheader("Enter the trip hub")
        name = st.selectbox("Who are you?", GUESTS)
        password = st.text_input("Password", type="password")

        if st.button("Enter ✨"):
            if password == GUEST_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.admin = False
                st.session_state.user_name = name
                st.rerun()
            elif password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.admin = True
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Wrong password lovely x")

    return False


def days_to_trip():
    today = date.today()
    if today < TRIP_START:
        return f"{(TRIP_START - today).days} days to go"
    if TRIP_START <= today <= TRIP_END:
        return "We are in Corfu!"
    return "The memories live on"


def home():
    st.markdown(
        f"""
        <div class="hero">
            <h1>The Corfu Diaries 💍✨</h1>
            <p>Celebrating Lauren in Corfu · {days_to_trip()}</p>
            <p class="small-muted">Add memories, quotes, photos, nominations and votes throughout the trip.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if Path("lauren.jpg").exists():
            st.image("lauren.jpg", caption="The reason we’re all here ❤️", use_container_width=True)

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>How this works</h3>
                <p>📸 Add photos and memories as they happen.</p>
                <p>😂 Save the best quotes before they’re forgotten.</p>
                <p>🏆 Nominate people for awards.</p>
                <p>🗳️ Vote before the final awards moment.</p>
                <p>💌 Leave Lauren a message she can keep forever.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def add_memory():
    st.header("📸 Add to the Memory Wall")

    with st.form("memory_form"):
        submitted_by = st.session_state.user_name
        people = st.multiselect("Who was involved?", GUESTS)
        category = st.selectbox("Type of memory", ["Funny", "Sweet", "Chaotic", "Iconic", "Wholesome", "Other"])
        memory = st.text_area("What happened?")

        if st.form_submit_button("Save memory ✨"):
            if memory.strip():
                run_query(
                    "INSERT INTO memories VALUES (NULL,?,?,?,?,?)",
                    (now(), submitted_by, ", ".join(people), category, memory),
                )
                st.success("Memory saved!")
            else:
                st.warning("Add a memory first.")

    st.subheader("Latest memories")
    df = run_query("SELECT * FROM memories ORDER BY id DESC LIMIT 20", fetch=True)
    for _, row in df.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <b>{row['category']} memory</b><br>
                <span class="small-muted">By {row['submitted_by']} · involving {row['people']}</span>
                <p>{row['memory']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def upload_photo():
    st.header("📷 Upload Photos")

    with st.form("photo_form"):
        submitted_by = st.session_state.user_name
        uploaded = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"])
        people = st.multiselect("Who is in it?", GUESTS)
        caption = st.text_input("Caption")

        if st.form_submit_button("Upload photo 📸"):
            if uploaded is not None:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                safe_name = uploaded.name.replace(" ", "_")
                file_path = UPLOAD_DIR / f"{timestamp}_{safe_name}"

                with open(file_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                run_query(
                    "INSERT INTO photos VALUES (NULL,?,?,?,?,?)",
                    (now(), submitted_by, ", ".join(people), caption, str(file_path)),
                )
                st.success("Photo uploaded!")
            else:
                st.warning("Choose a photo first.")

    st.subheader("Photo gallery")
    df = run_query("SELECT * FROM photos ORDER BY id DESC", fetch=True)
    cols = st.columns(3)
    for i, row in df.iterrows():
        with cols[i % 3]:
            if Path(row["file_path"]).exists():
                st.image(row["file_path"], caption=row["caption"], use_container_width=True)


def quotes():
    st.header("😂 Quote of the Trip")

    with st.form("quote_form"):
        submitted_by = st.session_state.user_name
        said_by = st.selectbox("Who said it?", GUESTS)
        quote = st.text_area("What did they say?")
        context = st.text_input("Context")

        if st.form_submit_button("Save quote 😂"):
            if quote.strip():
                run_query(
                    "INSERT INTO quotes VALUES (NULL,?,?,?,?,?)",
                    (now(), submitted_by, said_by, quote, context),
                )
                st.success("Quote saved!")
            else:
                st.warning("Add the quote first.")

    st.subheader("Saved quotes")
    df = run_query("SELECT * FROM quotes ORDER BY id DESC", fetch=True)
    for _, row in df.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <h3>“{row['quote']}”</h3>
                <p class="small-muted">Said by {row['said_by']} · submitted by {row['submitted_by']}</p>
                <p>{row['context']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def nominate():
    st.header("🏆 Nominate Someone")

    st.info("Nominate throughout the trip. The best reasons will help make the final awards script funnier.")

    with st.form("nomination_form"):
        submitted_by = st.session_state.user_name
        award = st.selectbox("Award category", AWARDS)
        nominee = st.selectbox("Who are you nominating?", VOTE_GUESTS)
        reason = st.text_area("Why should they win?")

        if st.form_submit_button("Submit nomination 🏆"):
            if reason.strip():
                run_query(
                    "INSERT INTO nominations VALUES (NULL,?,?,?,?,?)",
                    (now(), submitted_by, award, nominee, reason),
                )
                st.success("Nomination saved!")
            else:
                st.warning("Add a reason first.")

    st.subheader("Recent nominations")
    df = run_query("SELECT * FROM nominations ORDER BY id DESC LIMIT 20", fetch=True)
    for _, row in df.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <b>{row['award']}</b><br>
                <span class="small-muted">{row['nominee']} · nominated by {row['submitted_by']}</span>
                <p>{row['reason']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def vote():
    st.header("🗳️ Vote for the Corfu Diaries Awards")
    st.info("Spread the love — try to vote for different people across the categories 💛")

    voter = st.session_state.user_name

    existing = run_query("SELECT award, nominee FROM votes WHERE voter = ?", (voter,), fetch=True)
    existing_map = dict(zip(existing["award"], existing["nominee"])) if not existing.empty else {}

    for award in AWARDS:
        st.markdown(f"### {award}")
        current = existing_map.get(award)
        if current:
            st.success(f"You voted for {current}")
        choice = st.selectbox(
            f"Who wins {award}?",
            ["Choose..."] + VOTE_GUESTS,
            key=f"vote_{award}",
        )
        if st.button(f"Save vote for {award}", key=f"btn_{award}"):
            if choice == "Choose...":
                st.warning("Choose someone first.")
            else:
                run_query(
                    """
                    INSERT INTO votes (created_at, voter, award, nominee)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(voter, award)
                    DO UPDATE SET nominee=excluded.nominee, created_at=excluded.created_at
                    """,
                    (now(), voter, award, choice),
                )
                st.success(f"Vote saved for {choice}")
                st.rerun()


def bride_messages():
    st.header("💌 Messages for Lauren")

    st.info("These are for Lauren to keep — funny, emotional, advice, memories, anything lovely.")

    with st.form("bride_message_form"):
        submitted_by = st.session_state.user_name
        message = st.text_area("Your message to Lauren")
        advice = st.text_input("Marriage advice / life advice")
        favourite_memory = st.text_area("Favourite memory with Lauren")

        if st.form_submit_button("Save message 💌"):
            if message.strip() or advice.strip() or favourite_memory.strip():
                run_query(
                    "INSERT INTO bride_messages VALUES (NULL,?,?,?,?,?)",
                    (now(), submitted_by, message, advice, favourite_memory),
                )
                st.success("Saved for Lauren ❤️")
            else:
                st.warning("Write something first.")


def results_dashboard():
    st.header("👑 Admin Dashboard")

    if not st.session_state.admin:
        st.error("Admin only.")
        return

    st.subheader("Vote results")
    votes = run_query("SELECT award, nominee, COUNT(*) as votes FROM votes GROUP BY award, nominee ORDER BY award, votes DESC", fetch=True)

    if votes.empty:
        st.info("No votes yet.")
    else:
        for award in AWARDS:
            award_df = votes[votes["award"] == award]
            if not award_df.empty:
                winner = award_df.iloc[0]
                st.markdown(f"### {award}")
                st.success(f"Current winner: {winner['nominee']} with {winner['votes']} votes")
                st.dataframe(award_df, use_container_width=True)

    st.subheader("Downloads")
    tables = {
        "memories": run_query("SELECT * FROM memories", fetch=True),
        "quotes": run_query("SELECT * FROM quotes", fetch=True),
        "photos": run_query("SELECT * FROM photos", fetch=True),
        "nominations": run_query("SELECT * FROM nominations", fetch=True),
        "votes": run_query("SELECT * FROM votes", fetch=True),
        "bride_messages": run_query("SELECT * FROM bride_messages", fetch=True),
    }

    for name, df in tables.items():
        st.download_button(
            f"Download {name}.csv",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"{name}.csv",
            mime="text/csv",
        )

    st.subheader("Bride messages")
    bm = tables["bride_messages"]
    for _, row in bm.iterrows():
        st.markdown(
            f"""
            <div class="card">
                <b>From {row['submitted_by']}</b>
                <p>{row['message']}</p>
                <p><b>Advice:</b> {row['advice']}</p>
                <p><b>Favourite memory:</b> {row['favourite_memory']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def final_script():
    st.header("🎤 Final Awards Ceremony Script")

    if not st.session_state.admin:
        st.error("Admin only.")
        return

    votes = run_query("SELECT award, nominee, COUNT(*) as votes FROM votes GROUP BY award, nominee ORDER BY award, votes DESC", fetch=True)
    nominations = run_query("SELECT * FROM nominations", fetch=True)

    if votes.empty:
        st.info("No votes yet.")
        return

    script_lines = []
    script_lines.append("Welcome to the official Corfu Diaries Awards 💍✨")
    script_lines.append("One weekend. Thirteen women. Endless memories.")
    script_lines.append("We have laughed, overshared, possibly lost the plot, and created memories Lauren will hopefully never forget.\n")

    for award in AWARDS:
        award_votes = votes[votes["award"] == award]
        if award_votes.empty:
            continue

        winner = award_votes.iloc[0]["nominee"]
        vote_count = award_votes.iloc[0]["votes"]

        reasons = nominations[
            (nominations["award"] == award) &
            (nominations["nominee"] == winner)
        ]["reason"].tolist()

        reason_text = reasons[0] if reasons else "for bringing something unforgettable to the trip."

        script_lines.append(f"🏆 {award}")
        script_lines.append(f"This award goes to... {winner}!")
        script_lines.append(f"With {vote_count} vote(s), {winner} wins {award} {reason_text}")
        script_lines.append("")

    script_lines.append("And finally, Lauren — the reason we are all here.")
    script_lines.append("This weekend has been full of fun, chaos, laughter and love, and it says so much about you that this group came together to celebrate you.")
    script_lines.append("We love you, we are so excited for your next chapter, and we cannot wait to celebrate you on your wedding day. 💍❤️")

    final = "\n".join(script_lines)

    st.text_area("Copy/read this script", final, height=500)

    st.download_button(
        "Download ceremony script",
        final.encode("utf-8"),
        file_name="corfu_diaries_awards_script.txt",
        mime="text/plain",
    )


def admin_reset():
    st.header("⚠️ Admin Reset")
    if not st.session_state.admin:
        st.error("Admin only.")
        return

    st.warning("Only use this if you want to clear test data before the trip.")

    if st.button("Clear all entries"):
        for table in ["memories", "quotes", "photos", "bride_messages", "nominations", "votes", "reactions"]:
            run_query(f"DELETE FROM {table}")
        st.success("All data cleared.")


def main():
    init_db()

    if not login():
        return

    st.sidebar.title("The Corfu Diaries 💍")
    st.sidebar.caption(f"Logged in as {st.session_state.user_name}")

    pages = [
        "🏠 Home",
        "📸 Memory Wall",
        "📷 Upload Photos",
        "😂 Quotes",
        "🏆 Nominate",
        "🗳️ Vote",
        "💌 For Lauren",
    ]

    if st.session_state.admin:
        pages += ["👑 Admin Dashboard", "🎤 Final Script", "⚠️ Reset Data"]

    page = st.sidebar.radio("Menu", pages)

    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.admin = False
        st.session_state.user_name = None
        st.rerun()

    if page == "🏠 Home":
        home()
    elif page == "📸 Memory Wall":
        add_memory()
    elif page == "📷 Upload Photos":
        upload_photo()
    elif page == "😂 Quotes":
        quotes()
    elif page == "🏆 Nominate":
        nominate()
    elif page == "🗳️ Vote":
        vote()
    elif page == "💌 For Lauren":
        bride_messages()
    elif page == "👑 Admin Dashboard":
        results_dashboard()
    elif page == "🎤 Final Script":
        final_script()
    elif page == "⚠️ Reset Data":
        admin_reset()


if __name__ == "__main__":
    main()