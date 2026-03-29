import streamlit as st
import time
import datetime
import random
import os
from pathlib import Path
import base64

st.set_page_config(page_title="Kulffi ❤️", layout="wide")

# ---------- HIDE STREAMLIT UI ----------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

html {
    scroll-behavior: smooth;
}
</style>
""", unsafe_allow_html=True)

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
# ---------- ROMANTIC GLOWING CLOCK ----------
start_clock = datetime.datetime(2018, 2, 21, 0, 0, 0)
start_clock_js = start_clock.strftime("%Y-%m-%dT%H:%M:%S")

clock_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap');

.clock-container {{
    text-align: center;
    margin-top: 50px;
    font-family: 'Poppins', sans-serif;
}}

.clock-title {{
    font-size: 20px;
    color: #ff9ab0;
    margin-bottom: 15px;
    letter-spacing: 1px;
}}

.clock-box {{
    display: inline-block;
    padding: 20px 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #ff4b6e, #ff8fa3, #ff4b6e);
    color: white;
    font-size: 42px;
    font-weight: 600;
    letter-spacing: 2px;
    box-shadow: 0 0 20px rgba(255, 75, 110, 0.6),
                0 0 40px rgba(255, 75, 110, 0.4),
                0 0 60px rgba(255, 75, 110, 0.2);
    animation: glowPulse 2.5s infinite ease-in-out, heartbeat 1.8s infinite;
}}

@keyframes glowPulse {{
    0% {{
        box-shadow: 0 0 10px rgba(255,75,110,0.4),
                    0 0 20px rgba(255,75,110,0.3);
    }}
    50% {{
        box-shadow: 0 0 30px rgba(255,75,110,0.8),
                    0 0 60px rgba(255,75,110,0.5);
    }}
    100% {{
        box-shadow: 0 0 10px rgba(255,75,110,0.4),
                    0 0 20px rgba(255,75,110,0.3);
    }}
}}

@keyframes heartbeat {{
    0%, 100% {{ transform: scale(1); }}
    25% {{ transform: scale(1.05); }}
    50% {{ transform: scale(1); }}
    75% {{ transform: scale(1.05); }}
}}
</style>

<div class="clock-container">
    <div class="clock-title">⏳ Our Time Since Feb 21, 2018 ❤️</div>
    <div id="romantic-clock" class="clock-box">Loading...</div>
</div>

<script>
const startTime = new Date("{start_clock_js}").getTime();

function updateClock() {{
    const now = new Date().getTime();
    let diff = Math.floor((now - startTime) / 1000);

    const years = Math.floor(diff / (365 * 24 * 3600));
    diff -= years * 365 * 24 * 3600;

    const days = Math.floor(diff / (24 * 3600));
    diff -= days * 24 * 3600;

    const hours = Math.floor(diff / 3600);
    diff -= hours * 3600;

    const minutes = Math.floor(diff / 60);
    const seconds = diff - minutes * 60;

    document.getElementById("romantic-clock").innerHTML =
        years + "y " +
        days + "d " +
        hours + "h " +
        minutes + "m " +
        seconds + "s";
}}

updateClock();
setInterval(updateClock, 1000);
</script>
"""

st.components.v1.html(clock_html, height=200)

# ---------- FLOATING HEARTS ----------
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
}}

.subtitle {{
    text-align: center;
    color: #ff9ab0;
    margin-bottom: 30px;
}}

.section {{
    background: rgba(255, 255, 255, 0.04);
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
}}

@keyframes floatUp {{
    0% {{ transform: translateY(0); opacity: 0; }}
    10% {{ opacity: 1; }}
    100% {{ transform: translateY(-110vh); opacity: 0; }}
}}
</style>

{hearts_html}

<div class="main-wrap">
  <div class="title">Kulffi ❤️</div>
  <div class="subtitle">Just scroll with love ✨</div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------- LOAD MEDIA ----------
# ---------- LOAD MEDIA ----------
audio_extensions = (".mp3", ".wav", ".ogg", ".m4a")
image_extensions = (".jpg", ".jpeg", ".png")
video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".webm")

ASSETS = Path("assets")

audio_files = []
images = []
videos = []

if ASSETS.exists():
    all_files = list(ASSETS.iterdir())

    audio_files = sorted([
        str(f) for f in all_files if f.suffix.lower() in audio_extensions
    ])

    images = sorted([
        str(f) for f in all_files if f.suffix.lower() in image_extensions
    ])

    videos = sorted([
        str(f) for f in all_files if f.suffix.lower() in video_extensions
    ])
# ---------- FUNCTIONS (UNCHANGED) ----------

def render_beginning_section():
    st.markdown("## 🌸 Beginning")
    st.write(f"❤️ {days_together} days with you")
    st.write("""
I still don’t understand how one person became my entire happiness…
but somehow, you did.. you are soooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo special to me, loveeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee you sooooooooooooooooooooooooooooooooooooooooooooooooooooo much.
""")

def render_chats_section():
    st.markdown("## 💬 Our Chats")
    st.markdown('<div style="background:#262626;padding:10px;border-radius:15px;margin:10px;">Ennaku epadi nu theriyala, enkitta iruka motha love vum unnakey tharanum, unkita iruka motha love vum naney eduthukanum kulffi ❤️</div>', unsafe_allow_html=True)
    st.markdown('<div style="background:#ff4b6e;padding:10px;border-radius:15px;margin:10px;margin-left:auto;">will you accept me?</div>', unsafe_allow_html=True)

def render_memories_section():
    st.markdown("## 📸 Memories")

    if images:
        cols = st.columns(3)
        for i, img in enumerate(images):
            with cols[i % 3]:
                st.image(img, use_container_width=True)

    if videos:
        st.markdown("### 🎬 Videos")
        for vid in videos:
            with open(vid, "rb") as f:
                st.video(f.read())

def render_letter_section():
    st.markdown("## 💌 Letter")
    st.write("""
My dear Kulffi,

I’ve been thinking about you a lot while writing this, and I kept wondering how to say everything I feel in simple words. Even now, I know it still won’t be enough… but I want to try, because you truly mean so much to me.

Somewhere along the way, you became more than just a person in my life. You became a part of my everyday thoughts. I don’t even realize it sometimes, but you’re there—in the songs I hear, in random moments, in quiet times when I’m doing nothing. It’s a strange and beautiful feeling, how one person can slowly become so important without even trying.

I don’t think I say this enough, but you’ve changed me in ways I never expected. You’ve made me calmer when I used to overthink, softer when I used to be a little distant, and happier in ways that feel real and peaceful. Being around you, even just talking to you, makes everything feel easier. With you, I don’t feel like I have to pretend or try too hard. I can just be myself, and that means a lot to me.

There are days when life feels confusing, heavy, or tiring. Sometimes things don’t go as planned, and everything feels a bit too much. But even in those moments, thinking about you brings a kind of comfort I can’t fully explain. It’s like a quiet support, a small light that makes things feel a little better. You’ve become my peace in ways I never thought someone could be.

I really don’t know what the future will look like. Life can be unpredictable, and things don’t always go the way we expect. But one thing I feel very sure about is this—if I ever get the choice, I will always choose you. Not just in the good and easy moments, but also in the difficult and messy ones. Because to me, choosing you means choosing something honest and real.

I want more of everything with you. More conversations that last longer than we expect. More laughter over small and silly things. More memories that we can look back on and smile about. More moments where we just sit and talk about nothing and everything at the same time. I don’t want to rush anything or force anything. I just want us to grow slowly, naturally, and truly understand each other step by step.

You’ve become someone very special to me, and I hope you know that. Not just today, not just because it’s your birthday, but every single day. You matter to me more than I can easily put into words.

And today, on your birthday, I just want to remind you how important you are. I hope your day is full of happiness, smiles, and all the little things that make you feel loved and appreciated. You deserve all the good things in the world.

Happy Birthday, my dear Kulffi ❤️

Please stay just the way you are… because that’s the person I fell for, and the person I continue to choose every day.

Always yours.

Fruit

""")

# ---------- MUSIC PLAYER ----------
import base64

if audio_files:
    st.markdown("## 🎵 Our Songs")

    songs_data = []

    for i, audio in enumerate(audio_files):
        with open(audio, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()

            ext = audio.split(".")[-1]
            mime = f"audio/{ext}"
            song_names = {
                 "song1": "En Jeevan",
                 "song2": "Kurumugil",
                 "song3": "Until I Find You",
                  "song4": "Moongil Thootam",
                   "song5": "Oru Kili Oru Kili",
                 "song6": "Perfect",
                   "song7": "Mounam Pesum Varthai Yavum",
                    "song8": "Anbil Mele Panithuli",
                    "song9": "Ponmayame",
                "song10": "Sidu Sidu"
                }

            file_name = os.path.basename(audio).split(".")[0]
            name = song_names.get(file_name, file_name)

            # Optional: match album art (same name .jpg/.png)
            img_path = os.path.splitext(audio)[0] + ".jpg"
            if os.path.exists(img_path):
                with open(img_path, "rb") as img:
                    img_b64 = base64.b64encode(img.read()).decode()
                    img_src = f"data:image/jpeg;base64,{img_b64}"
            else:
                img_src = ""

            songs_data.append({
                "name": name,
                "data": f"data:{mime};base64,{b64}",
                "img": img_src
            })

    songs_js = str(songs_data).replace("'", '"')

    player_html = f"""
    <style>
    .player {{
        text-align:center;
        padding:20px;
        border-radius:20px;
        background: rgba(255,75,110,0.1);
        box-shadow: 0 0 30px rgba(255,75,110,0.4);
        color:white;
    }}

    .cover {{
        width:120px;
        height:120px;
        border-radius:15px;
        margin-bottom:10px;
        object-fit:cover;
        box-shadow: 0 0 15px rgba(255,75,110,0.6);
    }}

    .title {{
        font-size:18px;
        margin-bottom:10px;
        color:#ff9ab0;
    }}

    .controls button {{
        background:#ff4b6e;
        border:none;
        color:white;
        padding:8px 14px;
        margin:5px;
        border-radius:50px;
        cursor:pointer;
    }}

    .progress-container {{
        width:100%;
        height:6px;
        background:#333;
        border-radius:10px;
        margin-top:10px;
        cursor:pointer;
    }}

    .progress {{
        height:100%;
        width:0%;
        background:#ff4b6e;
        border-radius:10px;
    }}
    </style>

    <div class="player">
        <img id="cover" class="cover" src="" />
        <div id="title" class="title">Loading...</div>

        <audio id="audio"></audio>

        <div class="controls">
            <button onclick="prevSong()">⏮</button>
            <button onclick="playSong()">▶</button>
            <button onclick="pauseSong()">⏸</button>
            <button onclick="nextSong()">⏭</button>
        </div>

        <div class="progress-container" onclick="seek(event)">
            <div id="progress" class="progress"></div>
        </div>
    </div>

    <script>
    let songs = {songs_js};

    let index = 0;
    let audio = document.getElementById("audio");
    let title = document.getElementById("title");
    let cover = document.getElementById("cover");
    let progress = document.getElementById("progress");

    function loadSong() {{
        audio.src = songs[index].data;
        title.innerText = songs[index].name;

        if(songs[index].img) {{
            cover.src = songs[index].img;
        }} else {{
            cover.src = "";
        }}

        audio.play();
    }}

    function playSong() {{
        audio.play();
    }}

    function pauseSong() {{
        audio.pause();
    }}

    function nextSong() {{
        index = (index + 1) % songs.length;
        loadSong();
    }}

    function prevSong() {{
        index = (index - 1 + songs.length) % songs.length;
        loadSong();
    }}

    audio.ontimeupdate = function() {{
        if(audio.duration) {{
            let percent = (audio.currentTime / audio.duration) * 100;
            progress.style.width = percent + "%";
        }}
    }}

    function seek(e) {{
        let rect = e.currentTarget.getBoundingClientRect();
        let x = e.clientX - rect.left;
        let width = rect.width;
        let percent = x / width;

        audio.currentTime = percent * audio.duration;
    }}

    audio.onended = nextSong;

    loadSong();
    </script>
    """

    st.components.v1.html(player_html, height=350)
# ---------- SINGLE PAGE FLOW ----------
render_beginning_section()
st.markdown("---")

render_chats_section()
st.markdown("---")

render_memories_section()
st.markdown("---")

render_letter_section()
# ---------- FINAL SURPRISE ----------
st.markdown("---")
st.markdown("## 🎁 One Last Surprise")

if st.button("Click for Surprise 🎉"):

    # More balloons (repeat for stronger effect)
    for _ in range(5):
        st.balloons()
        time.sleep(0.3)

    # Big glowing message
    surprise_html = """
    <style>
    .birthday-text {
        text-align:center;
        font-size:50px;
        font-weight:700;
        color:#ffffff;
        margin-top:30px;
        text-shadow: 
            0 0 10px #ff4b6e,
            0 0 20px #ff4b6e,
            0 0 40px #ff4b6e;
        animation: glow 2s infinite alternate;
    }

    @keyframes glow {
        from { text-shadow: 0 0 10px #ff4b6e; }
        to { text-shadow: 0 0 30px #ff4b6e, 0 0 60px #ff4b6e; }
    }
    </style>

    <div class="birthday-text">
        🎂 Happy Birthday My Dear Kulffi ❤️
    </div>
    """

    st.components.v1.html(surprise_html, height=150)
