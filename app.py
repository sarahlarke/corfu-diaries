import os
import sqlite3
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

# ============================================================
# THE CORFU DIARIES - FINAL SINGLE FILE STREAMLIT APP
# ============================================================
# Files needed in your GitHub repo:
#   app.py
#   lauren.jpg
#   requirements.txt
#
# requirements.txt:
#   streamlit
#   pandas
# ============================================================

APP_TITLE = "The Corfu Diaries"
GUEST_PASSWORD = "corfu"
ADMIN_PASSWORD = "laurenadmin"

TRIP_START = date(2026, 5, 7)
TRIP_END = date(2026, 5, 10)

GUESTS = [
    "Sarah", "Lauren", "Lyn", "Jane", "Emily", "Gemma", "Drew",
    "Sara", "Kelly", "Jessie", "Tracy", "Charlotte", "Jenny", "Louise"
]

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

BRIDE_PHOTO = "lauren.jpg"


# ============================================================
# PAGE CONFIG + STYLE
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;700&display=swap');

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 214, 186, 0.55), transparent 35%),
            radial-gradient(circle at top right, rgba(255, 190, 210, 0.45), transparent 30%),
            linear-gradient(180deg, #fff8f1 0%, #fff1f5 45%, #fffaf6 100%);
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #7b3f45;
    }

    .hero {
        background: linear-gradient(135deg, rgba(255,255,255,0.94), rgba(255,244,235,0.90));
        padding: 2.4rem 1.8rem;
        border-radius: 34px;
        border: 1px solid rgba(201, 159, 122, 0.35);
        box-shadow: 0 18px 45px rgba(123, 63, 69, 0.14);
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        font-size: 3.35rem;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }

    .hero p {
        font-size: 1.15rem;
        color: #735b57;
    }

    .tagline {
        display: inline-block;
        background: #fff0df;
        color: #9b644a;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        font-weight: 700;
        margin-top: 0.5rem;
        border: 1px solid rgba(166, 120, 58, 0.22);
    }

    .card {
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(201, 159, 122, 0.28);
        padding: 1.35rem;
        border-radius: 28px;
        box-shadow: 0 12px 30px rgba(123, 63, 69, 0.09);
        margin-bottom: 1rem;
    }

    .feature-card {
        background: linear-gradient(135deg, #fff7ed, #fff1f5);
        border: 1px solid rgba(201, 159, 122, 0.35);
        padding: 1.5rem;
        border-radius: 30px;
        box-shadow: 0 12px 32px rgba(123, 63, 69, 0.1);
        margin-bottom: 1rem;
    }

    .gold {
        color: #a6783a;
        font-weight: 800;
    }

    .small-muted {
        color: #7b6a67;
        font-size: 0.95rem;
    }

    .stImage img {
        border-radius: 28px;
        box-shadow: 0 15px 35px rgba(123, 63, 69, 0.16);
    }

    div.stButton > button {
        border-radius: 999px;
        border: 1px solid #c99f7a;
        background: linear-gradient(135deg, #fff4e6, #ffe9f0);
        color: #7a5148;
        font-weight: 800;
        padding: 0.55rem 1.1rem;
        box-shadow: 0 8px 18px rgba(123, 63, 69, 0.1);
    }

    div.stButton > button:hover {
        border: 1px solid #a6783a;
        color: #7b3f45;
        transform: translateY(-1px);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff4e8 0%, #ffeef4 100%);
        border-right: 1px solid rgba(201, 159, 122, 0.25);
    }

    input, textarea, select {
        border-radius: 16px !important;
    }

    .stTextInput, .stTextArea, .stSelectbox, .stMultiSelect {
        margin-bottom: 0.35rem;
    }

    @media (max-width: 768px) {
        .hero h1 {
            font-size: 2.35rem;
        }
        .hero {
            padding: 1.55rem 1rem;
            border-radius: 26px;
        }
        .card, .feature-card {
            padding: 1rem;
            border-radius: 22px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE HELPERS
# ============================================================

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


def safe_html(text):
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def get_table(name):
    return run_query(f"SELECT * FROM {name}", fetch=True)


# ============================================================
# GENERAL HELPERS
# ============================================================

def days_to_trip():
    today = date.today()
    if today < TRIP_START:
        return f"{(TRIP_START - today).days} days to go"
    if TRIP_START <= today <= TRIP_END:
        return "We are in Corfu!"
    return "The memories live on"


def hero_block(subtitle="A private little memory book for Lauren’s hen weekend"):
    st.markdown(
        f"""
        <div class="hero">
            <h1>The Corfu Diaries 💍✨</h1>
            <p>{subtitle}</p>
            <div class="tagline">One weekend · Thirteen women · Endless memories</div>
            <p class="small-muted" style="margin-top:1rem;">{days_to_trip()}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_bride_photo(caption="The reason we’re all here ❤️"):
    if Path(BRIDE_PHOTO).exists():
        st.image(BRIDE_PHOTO, caption=caption, use_container_width=True)
    else:
        st.info("Add Lauren’s photo as `lauren.jpg` in the same folder as this app.")


# ============================================================
# LOGIN
# ============================================================

def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.admin = False
        st.session_state.user_name = None

    if st.session_state.logged_in:
        return True

    hero_block()

    col1, col2 = st.columns([1, 1])

    with col1:
        show_bride_photo()

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>Welcome to Lauren’s Corfu hub</h3>
                <p>Add the stories, quotes, photos and little moments that make the weekend unforgettable.</p>
                <p class="small-muted">Guest password: <b>corfu</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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


# ============================================================
# PAGES
# ============================================================

def home():
    hero_block()

    col1, col2 = st.columns([1, 1])
    with col1:
        show_bride_photo()

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>How this works</h3>
                <p>📸 <b>Memory Wall</b> — add the moments as they happen.</p>
                <p>😂 <b>Quotes</b> — save the lines nobody should forget.</p>
                <p>🏆 <b>Nominations</b> — suggest people for awards with reasons.</p>
                <p>🗳️ <b>Voting</b> — choose the final winners before we head home.</p>
                <p>💌 <b>For Lauren</b> — leave messages she can keep forever.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="card">
                <h3>Little rule 💛</h3>
                <p>Don’t wait until the end — add funny moments while they’re fresh. 
                The more everyone adds, the better the final awards will be.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def add_memory():
    st.header("📸 Memory Wall")
    st.caption("Capture the moments before they disappear into the group chat.")

    with st.form("memory_form", clear_on_submit=True):
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
    df = run_query("SELECT * FROM memories ORDER BY id DESC LIMIT 30", fetch=True)
    if df.empty:
        st.info("No memories yet — be the first to add one.")
    else:
        for _, row in df.iterrows():
            st.markdown(
                f"""
                <div class="card">
                    <b>{safe_html(row['category'])} memory</b><br>
                    <span class="small-muted">By {safe_html(row['submitted_by'])} · involving {safe_html(row['people'])}</span>
                    <p>{safe_html(row['memory'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def upload_photo():
    st.header("📷 Upload Photos")
    st.caption("Add the wholesome, chaotic and iconic evidence.")

    with st.form("photo_form", clear_on_submit=True):
        submitted_by = st.session_state.user_name
        uploaded = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"])
        people = st.multiselect("Who is in it?", GUESTS)
        caption = st.text_input("Caption")

        if st.form_submit_button("Upload photo 📸"):
            if uploaded is not None:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                safe_name = uploaded.name.replace(" ", "_").replace("/", "_").replace("\\", "_")
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
    if df.empty:
        st.info("No photos yet.")
    else:
        cols = st.columns(2)
        for i, row in df.iterrows():
            with cols[i % 2]:
                if Path(row["file_path"]).exists():
                    st.image(row["file_path"], caption=row["caption"], use_container_width=True)
                    st.caption(f"Uploaded by {row['submitted_by']} · {row['people']}")


def quotes():
    st.header("😂 Quotes & Chaos")
    st.caption("Because someone will say something that deserves preserving forever.")

    with st.form("quote_form", clear_on_submit=True):
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
    if df.empty:
        st.info("No quotes yet.")
    else:
        for _, row in df.iterrows():
            st.markdown(
                f"""
                <div class="card">
                    <h3>“{safe_html(row['quote'])}”</h3>
                    <p class="small-muted">Said by {safe_html(row['said_by'])} · submitted by {safe_html(row['submitted_by'])}</p>
                    <p>{safe_html(row['context'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def nominate():
    st.header("🏆 Nominate")
    st.info("Nominate people throughout the trip. The reasons make the final ceremony much funnier.")

    with st.form("nomination_form", clear_on_submit=True):
        submitted_by = st.session_state.user_name
        award = st.selectbox("Award category", AWARDS)
        nominee = st.selectbox("Who are you nominating?", GUESTS)
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
    df = run_query("SELECT * FROM nominations ORDER BY id DESC LIMIT 30", fetch=True)
    if df.empty:
        st.info("No nominations yet.")
    else:
        for _, row in df.iterrows():
            st.markdown(
                f"""
                <div class="card">
                    <b>{safe_html(row['award'])}</b><br>
                    <span class="small-muted">{safe_html(row['nominee'])} · nominated by {safe_html(row['submitted_by'])}</span>
                    <p>{safe_html(row['reason'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def vote():
    st.header("🗳️ Vote")
    st.info("Spread the love — try to vote for different people across the categories 💛")

    voter = st.session_state.user_name

    existing = run_query("SELECT award, nominee FROM votes WHERE voter = ?", (voter,), fetch=True)
    existing_map = dict(zip(existing["award"], existing["nominee"])) if not existing.empty else {}

    completed = len(existing_map)
    st.progress(completed / len(AWARDS))
    st.caption(f"You have voted in {completed} of {len(AWARDS)} categories.")

    for award in AWARDS:
        st.markdown(f"### {award}")
        current = existing_map.get(award)
        if current:
            st.success(f"Current vote: {current}")

        choice = st.selectbox(
            f"Who wins {award}?",
            ["Choose..."] + GUESTS,
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
    st.header("💌 For Lauren")
    st.info("These are for Lauren to keep — funny, emotional, advice, memories, anything lovely.")

    with st.form("bride_message_form", clear_on_submit=True):
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
    votes = run_query(
        "SELECT award, nominee, COUNT(*) as votes FROM votes GROUP BY award, nominee ORDER BY award, votes DESC",
        fetch=True
    )

    if votes.empty:
        st.info("No votes yet.")
    else:
        for award in AWARDS:
            award_df = votes[votes["award"] == award]
            if not award_df.empty:
                winner = award_df.iloc[0]
                st.markdown(f"### {award}")
                st.success(f"Current winner: {winner['nominee']} with {winner['votes']} vote(s)")
                st.dataframe(award_df, use_container_width=True, hide_index=True)

    st.subheader("Downloads")
    tables = {
        "memories": get_table("memories"),
        "quotes": get_table("quotes"),
        "photos": get_table("photos"),
        "nominations": get_table("nominations"),
        "votes": get_table("votes"),
        "bride_messages": get_table("bride_messages"),
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
    if bm.empty:
        st.info("No bride messages yet.")
    else:
        for _, row in bm.iterrows():
            st.markdown(
                f"""
                <div class="card">
                    <b>From {safe_html(row['submitted_by'])}</b>
                    <p>{safe_html(row['message'])}</p>
                    <p><b>Advice:</b> {safe_html(row['advice'])}</p>
                    <p><b>Favourite memory:</b> {safe_html(row['favourite_memory'])}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def final_script():
    st.header("🎤 Final Awards Script")

    if not st.session_state.admin:
        st.error("Admin only.")
        return

    votes = run_query(
        "SELECT award, nominee, COUNT(*) as votes FROM votes GROUP BY award, nominee ORDER BY award, votes DESC",
        fetch=True
    )
    nominations = get_table("nominations")

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
        ]["reason"].tolist() if not nominations.empty else []

        reason_text = reasons[0] if reasons else "for bringing something unforgettable to the trip."

        script_lines.append(f"🏆 {award}")
        script_lines.append(f"This award goes to... {winner}!")
        script_lines.append(f"With {vote_count} vote(s), {winner} wins because {reason_text}")
        script_lines.append("")

    script_lines.append("And finally, Lauren — the reason we are all here.")
    script_lines.append("This weekend has been full of fun, chaos, laughter and love, and it says so much about you that this group came together to celebrate you.")
    script_lines.append("We love you, we are so excited for your next chapter, and we cannot wait to celebrate you on your wedding day. 💍❤️")

    final = "\n".join(script_lines)

    st.text_area("Copy/read this script", final, height=520)

    st.download_button(
        "Download ceremony script",
        final.encode("utf-8"),
        file_name="corfu_diaries_awards_script.txt",
        mime="text/plain",
    )


def admin_reset():
    st.header("⚠️ Reset Test Data")

    if not st.session_state.admin:
        st.error("Admin only.")
        return

    st.warning("Only use this before the trip if you want to clear test data.")

    confirm = st.text_input("Type RESET to confirm")
    if st.button("Clear all entries"):
        if confirm == "RESET":
            for table in ["memories", "quotes", "photos", "bride_messages", "nominations", "votes"]:
                run_query(f"DELETE FROM {table}")
            st.success("All data cleared.")
        else:
            st.error("Type RESET first.")


# ============================================================
# MAIN
# ============================================================

def main():
    init_db()

    if not login():
        return

    st.sidebar.title("💍 The Corfu Diaries")
    st.sidebar.caption("Lauren’s Corfu memory hub")
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
