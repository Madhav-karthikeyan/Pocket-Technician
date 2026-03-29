import streamlit as st
import time
import datetime
import random
import os
from pathlib import Path

st.set_page_config(page_title="Kulffi ❤️", layout="wide")

# ---------- SESSION ----------
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# ---------- PASSWORD ----------
if not st.session_state.unlocked:
    st.markdown("<h1 style='text-align:center;'>🔐 Only For Kulffi ❤️</h1>", unsafe_allow_html=True)
    password = st.text_input("Enter the password", type="password")

    if password == "kulffi":
        st.session_state.unlocked = True
        st.rerun()
    else:
        st.stop()

# ---------- INTRO ----------
if not st.session_state.intro_done:
    st.markdown("""
    <div style="height:100vh; display:flex; justify-content:center; align-items:center;
    background:black; color:white; font-size:40px; text-align:center;">
    This isn't just an app… 💫<br><br>
    It's our story ❤️
    </div>
    """, unsafe_allow_html=True)

    time.sleep(3)
    st.session_state.intro_done = True
    st.rerun()

# ---------- TIME BASED HEARTS ----------
start_date = datetime.date(2023, 5, 1)
days = (datetime.date.today() - start_date).days

heart_count = min(20, 5 + days // 30)

hearts_html = ""
for i in range(heart_count):
    left = random.randint(0, 100)
    delay = random.uniform(0, 5)
    hearts_html += f'<div class="heart" style="left:{left}%; animation-delay:{delay}s;">❤️</div>'

# ---------- CLOCK ----------
start_clock = datetime.datetime(2018, 2, 21, 0, 0, 0)
now = datetime.datetime.now()
diff = now - start_clock

years = diff.days // 365
months = (diff.days % 365) // 30
days_clock = (diff.days % 365) % 30
hours, remainder = divmod(diff.seconds, 3600)
minutes, seconds = divmod(remainder, 60)

st.markdown(f"""
<div style="text-align:center; font-size:20px; color:#ff4b6e;">
⏳ Since Feb 21, 2018<br>
{years} years {months} months {days_clock} days<br>
{hours}h {minutes}m {seconds}s
</div>
""", unsafe_allow_html=True)

# ---------- CSS ----------
st.markdown(f"""
<style>
body {{
    background:black;
    color:white;
}}

.title {{
    text-align:center;
    font-size:45px;
    color:#ff4b6e;
}}

.heart {{
    position:fixed;
    bottom:-10px;
    animation:floatUp 6s linear infinite;
}}

@keyframes floatUp {{
    0% {{transform:translateY(0); opacity:1;}}
    100% {{transform:translateY(-100vh); opacity:0;}}
}}

.chat-left {{
    background:#262626;
    padding:10px;
    border-radius:15px;
    margin:10px;
}}

.chat-right {{
    background:#ff4b6e;
    padding:10px;
    border-radius:15px;
    margin:10px;
    margin-left:auto;
}}

.spotify {{
    position:fixed;
    bottom:20px;
    right:20px;
    width:260px;
    background:#121212;
    padding:15px;
    border-radius:15px;
}}
</style>

{hearts_html}
""", unsafe_allow_html=True)

# ---------- MUSIC (FIXED) ----------
audio_extensions = (".mp3", ".wav", ".ogg", ".m4a")
audio_files = [f"assets/{file}" for file in os.listdir("assets") if file.lower().endswith(audio_extensions)]

if audio_files:
    with open(audio_files[0], "rb") as f:
        st.audio(f.read())

# ---------- NAV ----------
page = st.sidebar.radio("Our Story ❤️", [
    "Beginning",
    "Chats",
    "Memories",
    "Letter"
])

# ---------- BEGINNING ----------
if page == "Beginning":
    st.markdown('<div class="title">Kulffi ❤️</div>', unsafe_allow_html=True)

    st.write(f"❤️ {days} days with you")

    st.write("""
    I still don’t understand how one person became my entire happiness…
    but somehow, you did.
    """)

# ---------- CHATS ----------
elif page == "Chats":
    st.markdown('<div class="title">Our Chats 💬</div>', unsafe_allow_html=True)

    st.markdown('<div class="chat-left">Kulffi… ❤️</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-right">Hmm? 😌</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-left">I miss you</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-right">Come fast 😭❤️</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-left">You are mine right?</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-right">Always 💖</div>', unsafe_allow_html=True)

# ---------- MEMORIES ----------
elif page == "Memories":
    st.markdown('<div class="title">Our Memories 📸</div>', unsafe_allow_html=True)

    cols = st.columns(3)

    image_extensions = (".jpg", ".jpeg", ".png")
    images = [f"assets/{file}" for file in os.listdir("assets") if file.lower().endswith(image_extensions)]

    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    videos = [f"assets/{file}" for file in os.listdir("assets") if file.lower().endswith(video_extensions)]

    # ----- IMAGE GRID -----
    for i, img in enumerate(images):
        with cols[i % 3]:
            st.image(img)

    # ----- AUTO SLIDESHOW -----
    if images:
        st.markdown("### 💖 Slideshow")
        placeholder = st.empty()
        for img in images:
            placeholder.image(img)
            time.sleep(1.5)

    # ----- VIDEOS -----
    for vid in videos:
        with open(vid, "rb") as f:
            st.video(f.read())

    # ----- ALL AUDIOS -----
    for audio in audio_files:
        with open(audio, "rb") as f:
            st.audio(f.read())

# ---------- LETTER ----------
elif page == "Letter":
    st.markdown('<div class="title">For You Kulffi 💌</div>', unsafe_allow_html=True)

    st.write("""
    Kulffi,

    I don’t even know where to start… because how do you explain someone who became everything?

    You didn’t just walk into my life…  
    you changed it completely.

    The way you talk, the way you laugh, the way you care…  
    every little thing about you stays in my mind longer than it should.

    You are not just someone I love.  
    You are my comfort.  
    My peace.  
    My favorite person in this entire world.

    There are days when everything feels heavy…  
    but then I think of you, and suddenly things feel okay again.

    I don’t know what I did to deserve you,  
    but I know one thing for sure…

    I never want a life where you are not in it.

    If life gives me choices again and again,  
    I will always choose you.

    Not once.  
    Not twice.  
    But every single time.

    Stay with me…  
    grow with me…  
    and let’s turn this into something forever.

    I love you, Kulffi ❤️
    """)

    if st.button("One Last Surprise 🎁"):
        st.balloons()
        st.success("You are my forever ❤️")
