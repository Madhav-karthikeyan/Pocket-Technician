import datetime
import os
import random
import time

import streamlit as st

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
    st.markdown(
        """
    <div style="height:100vh; display:flex; justify-content:center; align-items:center;
    background:black; color:white; font-size:40px; text-align:center;">
    This isn't just an app… 💫<br><br>
    It's our story ❤️
    </div>
    """,
        unsafe_allow_html=True,
    )

    time.sleep(3)
    st.session_state.intro_done = True
    st.rerun()

# ---------- DATES ----------
start_date = datetime.date(2023, 5, 1)
days_together = (datetime.date.today() - start_date).days

start_clock = datetime.datetime(2018, 2, 21, 0, 0, 0)
start_clock_js = start_clock.strftime("%Y-%m-%dT%H:%M:%S")

# More hearts over time (grows with months passed)
heart_count = min(120, 20 + max(0, days_together // 10))
hearts_html = ""
for _ in range(heart_count):
    left = random.randint(0, 100)
    delay = random.uniform(0, 8)
    duration = random.uniform(4, 10)
    size = random.uniform(14, 34)
    hearts_html += (
        f'<div class="heart" style="left:{left}%; animation-delay:{delay}s; '
        f'animation-duration:{duration}s; font-size:{size}px;">❤️</div>'
    )

# ---------- CSS + CLOCK ----------
st.markdown(
    f"""
<style>
body, .stApp {{
    background: #090909;
    color: #ffffff;
}}

.main-wrap {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 12px 40px;
}}

.title {{
    text-align: center;
    font-size: 3rem;
    color: #ff4b6e;
    margin-top: 10px;
    margin-bottom: 10px;
}}

.subtitle {{
    text-align: center;
    color: #ff9ab0;
    margin-bottom: 30px;
}}

.section {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 22px;
    margin: 22px 0;
}}

.section h2 {{
    color: #ff6f8e;
    margin-top: 0;
}}

.flip-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    margin-top: 14px;
}}

.flip-box {{
    background: #111;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #2f2f2f;
    box-shadow: inset 0 -3px 0 #050505;
    text-align: center;
}}

.flip-value {{
    font-family: 'Courier New', monospace;
    font-weight: 700;
    font-size: 2rem;
    color: #fff;
    background: linear-gradient(180deg, #1f1f1f 0%, #0b0b0b 52%, #1a1a1a 100%);
    border-radius: 8px;
    padding: 8px 0;
    position: relative;
    overflow: hidden;
}}

.flip-value::after {{
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    border-top: 1px solid rgba(255, 255, 255, 0.25);
}}

.flip-label {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #ffa7ba;
    margin-top: 8px;
}}

.heart {{
    position: fixed;
    bottom: -30px;
    z-index: 1;
    pointer-events: none;
    animation-name: floatUp;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    opacity: 0.86;
}}

@keyframes floatUp {{
    0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
    10% {{ opacity: 1; }}
    100% {{ transform: translateY(-110vh) rotate(25deg); opacity: 0; }}
}}

.media-grid img {{
    border-radius: 12px;
}}

hr {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.12);
    margin: 20px 0;
}}
</style>

{hearts_html}

<div class="main-wrap">
  <div class="title">Kulffi ❤️</div>
  <div class="subtitle">All in one page. Just scroll with love ✨</div>

  <div class="section">
    <h2>⏳ Flip Clock Since Feb 21, 2018</h2>
    <div class="flip-grid">
      <div class="flip-box"><div class="flip-value" id="years">00</div><div class="flip-label">Years</div></div>
      <div class="flip-box"><div class="flip-value" id="months">00</div><div class="flip-label">Months</div></div>
      <div class="flip-box"><div class="flip-value" id="weeks">00</div><div class="flip-label">Weeks</div></div>
      <div class="flip-box"><div class="flip-value" id="days">00</div><div class="flip-label">Days</div></div>
      <div class="flip-box"><div class="flip-value" id="hours">00</div><div class="flip-label">Hours</div></div>
      <div class="flip-box"><div class="flip-value" id="minutes">00</div><div class="flip-label">Minutes</div></div>
      <div class="flip-box"><div class="flip-value" id="seconds">00</div><div class="flip-label">Seconds</div></div>
    </div>
  </div>
</div>

<script>
const startTime = new Date('{start_clock_js}').getTime();

function pad(n) {{
  return String(n).padStart(2, '0');
}}

function updateClock() {{
  const now = Date.now();
  let diff = Math.max(0, Math.floor((now - startTime) / 1000));

  const years = Math.floor(diff / (365 * 24 * 3600));
  diff -= years * 365 * 24 * 3600;

  const months = Math.floor(diff / (30 * 24 * 3600));
  diff -= months * 30 * 24 * 3600;

  const weeks = Math.floor(diff / (7 * 24 * 3600));
  diff -= weeks * 7 * 24 * 3600;

  const days = Math.floor(diff / (24 * 3600));
  diff -= days * 24 * 3600;

  const hours = Math.floor(diff / 3600);
  diff -= hours * 3600;

  const minutes = Math.floor(diff / 60);
  const seconds = diff - minutes * 60;

  const ids = ['years','months','weeks','days','hours','minutes','seconds'];
  const vals = [years, months, weeks, days, hours, minutes, seconds];

  ids.forEach((id, i) => {{
    const el = document.getElementById(id);
    if (el) el.textContent = pad(vals[i]);
  }});
}}

updateClock();
setInterval(updateClock, 1000);
</script>
""",
    unsafe_allow_html=True,
)

# ---------- OPTIONAL MEDIA ----------
audio_extensions = (".mp3", ".wav", ".ogg", ".m4a")
image_extensions = (".jpg", ".jpeg", ".png")
video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".webm")

assets_path = Path("assets")
audio_files = []
images = []
videos = []

if assets_path.exists() and assets_path.is_dir():
    audio_files = [
        str(assets_path / file)
        for file in os.listdir(assets_path)
        if file.lower().endswith(audio_extensions)
    ]
    images = [
        str(assets_path / file)
        for file in os.listdir(assets_path)
        if file.lower().endswith(image_extensions)
    ]
    videos = [
        str(assets_path / file)
        for file in os.listdir(assets_path)
        if file.lower().endswith(video_extensions)
    ]

# ---------- APP NAV ----------
page = st.sidebar.radio(
    "Our Story ❤️",
    ["Beginning", "Chats", "Memories", "Letter", "All In One Scroll"],
)

# ---------- BEGINNING ----------
def render_beginning_section():
    st.markdown("## 🌸 Beginning")
    st.write(f"❤️ {days_together} days with you")
    st.write(
        """
I still don’t understand how one person became my entire happiness…
but somehow, you did.
"""
    )


# ---------- CHATS ----------
def render_chats_section():
    st.markdown("## 💬 Our Chats")
    st.markdown('<div style="background:#262626;padding:10px;border-radius:15px;margin:10px;">Kulffi… ❤️</div>', unsafe_allow_html=True)
    st.markdown('<div style="background:#ff4b6e;padding:10px;border-radius:15px;margin:10px;margin-left:auto;">Hmm? 😌</div>', unsafe_allow_html=True)
    st.markdown('<div style="background:#262626;padding:10px;border-radius:15px;margin:10px;">I miss you</div>', unsafe_allow_html=True)
    st.markdown('<div style="background:#ff4b6e;padding:10px;border-radius:15px;margin:10px;margin-left:auto;">Come fast 😭❤️</div>', unsafe_allow_html=True)
    st.markdown('<div style="background:#262626;padding:10px;border-radius:15px;margin:10px;">You are mine right?</div>', unsafe_allow_html=True)
    st.markdown('<div style="background:#ff4b6e;padding:10px;border-radius:15px;margin:10px;margin-left:auto;">Always 💖</div>', unsafe_allow_html=True)


# ---------- MEMORIES ----------
def render_memories_section():
    st.markdown("## 📸 Memories")

    if images:
        cols = st.columns(3)
        for i, img in enumerate(images):
            with cols[i % 3]:
                st.image(img, use_container_width=True)

        st.markdown("### 💖 Slideshow")
        placeholder = st.empty()
        for img in images:
            placeholder.image(img, use_container_width=True)
            time.sleep(1.2)
    else:
        st.info("No images found in the assets folder yet.")

    if videos:
        st.markdown("### 🎬 Videos")
        for vid in videos:
            with open(vid, "rb") as f:
                st.video(f.read())

    if audio_files:
        st.markdown("### 🎵 Audio")
        for audio in audio_files:
            with open(audio, "rb") as f:
                st.audio(f.read())


# ---------- LETTER ----------
def render_letter_section():
    st.markdown("## 💌 Letter")
    st.write(
        """
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
"""
    )

    if st.button("One Last Surprise 🎁"):
        st.balloons()
        st.success("You are my forever ❤️")


if page == "Beginning":
    render_beginning_section()
elif page == "Chats":
    render_chats_section()
elif page == "Memories":
    render_memories_section()
elif page == "Letter":
    render_letter_section()
else:
    render_beginning_section()
    st.markdown("---")
    render_chats_section()
    st.markdown("---")
    render_memories_section()
    st.markdown("---")
    render_letter_section()
