import base64
import datetime
import os
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Kulffi ❤️", layout="wide")

# ---------- SESSION ----------
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False

# ---------- PASSWORD ----------
if not st.session_state.unlocked:
    st.markdown("<h1 style='text-align:center;'>🔐 Only For Kulffi ❤️</h1>", unsafe_allow_html=True)
    password = st.text_input("Enter the password", type="password")

    if password == "kulffi":
        st.session_state.unlocked = True
        st.rerun()
    else:
        st.stop()

# ---------- DATES ----------
start_date = datetime.date(2023, 5, 1)
days_together = (datetime.date.today() - start_date).days
start_clock = datetime.datetime(2018, 2, 21, 0, 0, 0)
start_clock_js = start_clock.strftime("%Y-%m-%dT%H:%M:%S")

# ---------- HEARTS ----------
heart_count = min(140, 25 + max(0, days_together // 8))
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

# ---------- CSS ----------
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
    margin-bottom: 24px;
}}
.section {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 22px;
    margin: 22px 0;
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
</style>
{hearts_html}
<div class="main-wrap">
  <div class="title">Kulffi ❤️</div>
  <div class="subtitle">Everything in one page, just scroll 💖</div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- RUNNING FLIP CLOCK ----------
clock_html = f"""
<div style="max-width:1100px;margin:0 auto;">
  <div class="section" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:18px;padding:22px;">
    <h2 style="color:#ff6f8e;margin:0 0 12px 0;">⏳ Flip Clock Since Feb 21, 2018</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;">
      {''.join([f'''<div style="background:#111;border-radius:12px;padding:10px;border:1px solid #2f2f2f;text-align:center;"><div id="{k}" style="font-family:Courier New,monospace;font-weight:700;font-size:2rem;color:#fff;background:linear-gradient(180deg,#1f1f1f 0%,#0b0b0b 52%,#1a1a1a 100%);border-radius:8px;padding:8px 0;">00</div><div style="font-size:.78rem;letter-spacing:.08em;color:#ffa7ba;margin-top:8px;text-transform:uppercase;">{k}</div></div>''' for k in ['years','months','weeks','days','hours','minutes','seconds']])}
    </div>
  </div>
</div>
<script>
  const startTime = new Date('{start_clock_js}').getTime();
  function pad(n) {{ return String(n).padStart(2, '0'); }}
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

    const vals = {{ years, months, weeks, days, hours, minutes, seconds }};
    Object.entries(vals).forEach(([id, value]) => {{
      const el = document.getElementById(id);
      if (el) el.textContent = pad(value);
    }});
  }}
  updateClock();
  setInterval(updateClock, 1000);
</script>
"""
components.html(clock_html, height=260)

# ---------- ASSETS ----------
audio_extensions = (".mp3", ".wav", ".ogg", ".m4a")
image_extensions = (".jpg", ".jpeg", ".png")
video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".webm")

assets_path = Path("assets")
audio_files, images, videos = [], [], []
if assets_path.exists() and assets_path.is_dir():
    audio_files = [
        str(assets_path / file)
        for file in sorted(os.listdir(assets_path))
        if file.lower().endswith(audio_extensions)
    ]
    images = [
        str(assets_path / file)
        for file in sorted(os.listdir(assets_path))
        if file.lower().endswith(image_extensions)
    ]
    videos = [
        str(assets_path / file)
        for file in sorted(os.listdir(assets_path))
        if file.lower().endswith(video_extensions)
    ]

# ---------- SINGLE STRAIGHT PAGE ----------
st.markdown("## 🌸 Beginning")
st.write(f"❤️ {days_together} days with you")
st.write(
    """
I still don’t understand how one person became my entire happiness…
but somehow, you did.
"""
)

st.markdown("---")
st.markdown("## 📸 Memories")
if images:
    cols = st.columns(3)
    for i, img in enumerate(images):
        with cols[i % 3]:
            st.image(img, use_container_width=True)
else:
    st.info("No images found in the assets folder yet.")

if videos:
    st.markdown("### 🎬 Videos")
    for vid in videos:
        with open(vid, "rb") as f:
            st.video(f.read())

st.markdown("---")
st.markdown("## 🎵 Music Player")
if audio_files:
    tracks_js = []
    for path in audio_files:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext = Path(path).suffix.lower().replace(".", "")
        mime = "mp4" if ext == "m4a" else ext
        tracks_js.append(
            {
                "name": Path(path).name,
                "src": f"data:audio/{mime};base64,{encoded}",
            }
        )

    tracks_literal = str(tracks_js).replace("'", '"')
    player_html = f"""
    <div style="max-width:1100px;margin:0 auto;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:18px;padding:20px;">
      <div id="song" style="color:#ff9ab0;margin-bottom:10px;font-weight:600;">Loading...</div>
      <audio id="player" controls style="width:100%;"></audio>
      <div style="display:flex;gap:10px;margin-top:10px;">
        <button onclick="prevTrack()">⏮ Prev</button>
        <button onclick="togglePlay()">⏯ Play / Pause</button>
        <button onclick="nextTrack()">⏭ Next</button>
      </div>
    </div>
    <script>
      const tracks = {tracks_literal};
      let idx = 0;
      const player = document.getElementById('player');
      const song = document.getElementById('song');

      function loadTrack(i) {{
        idx = (i + tracks.length) % tracks.length;
        player.src = tracks[idx].src;
        song.textContent = 'Now Playing: ' + tracks[idx].name;
        player.play();
      }}

      function nextTrack() {{ loadTrack(idx + 1); }}
      function prevTrack() {{ loadTrack(idx - 1); }}
      function togglePlay() {{
        if (player.paused) player.play();
        else player.pause();
      }}
      player.addEventListener('ended', nextTrack);
      if (tracks.length) loadTrack(0);
    </script>
    """
    components.html(player_html, height=180)
else:
    st.info("No audio files found in assets folder yet.")

st.markdown("---")
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
