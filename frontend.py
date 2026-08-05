import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: #050810 !important;
    color: #e0f2fe;
}

/* ── Animated Background ── */
.stApp::before {
    content: "";
    position: fixed;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background:
        radial-gradient(circle at 20% 30%, rgba(26,107,191,0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(139,92,246,0.10) 0%, transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(6,182,212,0.06) 0%, transparent 50%);
    animation: bgMove 25s ease-in-out infinite alternate;
    z-index: 0;
    pointer-events: none;
}
@keyframes bgMove {
    0%   { transform: translate(0,0) scale(1); }
    50%  { transform: translate(-3%,-2%) scale(1.05); }
    100% { transform: translate(2%,1%) scale(0.98); }
}

/* ── Hero ── */
.hero-wrapper {
    position: relative;
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 2rem;
    height: 300px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}
.hero-bg {
    width: 100%; height: 100%;
    object-fit: cover;
    display: block;
    filter: brightness(0.35) saturate(1.2);
    position: absolute;
    top: 0; left: 0;
}
.hero-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(5,8,16,0.7) 0%, rgba(26,107,191,0.15) 100%);
    z-index: 1;
}
.hero-content {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
}
.hero-badge {
    background: rgba(26,107,191,0.25);
    border: 1px solid rgba(58,123,213,0.6);
    color: #a5d8ff !important;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.4rem 1.2rem;
    border-radius: 30px;
    margin-bottom: 1rem;
    box-shadow: 0 0 25px rgba(26,107,191,0.3);
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.6rem;
    line-height: 1.1;
    text-shadow: 0 4px 30px rgba(0,0,0,0.5);
}
.hero-sub {
    color: #a5c8e8;
    font-size: 1.1rem;
    max-width: 600px;
    line-height: 1.6;
}

/* ── Destination Cards (Bright & Clear) ── */
.dest-card {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    height: 130px;
    cursor: pointer;
    transition: all 0.4s ease;
    box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.08);
}
.dest-card:hover {
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 20px 40px rgba(26,107,191,0.25);
    border-color: rgba(58,123,213,0.4);
}
.dest-card img {
    width: 100%; height: 100%;
    object-fit: cover;
    display: block;
    filter: brightness(0.65) saturate(1.3);  /* BRIGHTER */
    transition: all 0.4s ease;
}
.dest-card:hover img {
    filter: brightness(0.85) saturate(1.5);
    transform: scale(1.1);
}
.dest-label {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 16px 8px 12px;
    text-align: center;
    color: #ffffff;
    font-size: 0.95rem;
    font-weight: 700;
    background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 60%, transparent 100%);
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
    letter-spacing: 0.02em;
}

/* ── Input Section ── */
.input-label {
    color: #7ab8f5;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* ── Quick Chips ── */
.chip-btn {
    background: rgba(17,27,43,0.9);
    border: 1px solid rgba(58,123,213,0.3);
    color: #c7e0ff;
    padding: 0.5rem 1rem;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}
.chip-btn:hover {
    background: rgba(26,107,191,0.3);
    border-color: #3a7bd5;
    color: #fff;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(26,107,191,0.2);
}

/* ── Generate Button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1a6bbf 0%, #0d4a8a 50%, #0a3d75 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 1rem 2.5rem !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 0 30px rgba(26,107,191,0.35), 0 8px 25px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 0 50px rgba(26,107,191,0.6), 0 12px 35px rgba(0,0,0,0.5) !important;
    transform: translateY(-3px) !important;
    background: linear-gradient(135deg, #2278d4 0%, #1057a0 50%, #0d4a8a 100%) !important;
}

/* ── VISUAL PIPELINE STEPS ── */
.pipeline-box {
    background: rgba(14,22,35,0.8);
    border: 1px solid rgba(58,123,213,0.2);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}
.pipeline-box:hover {
    border-color: rgba(58,123,213,0.5);
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(26,107,191,0.15);
}
.pipeline-icon {
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
    display: block;
}
.pipeline-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #e0f2fe;
    margin-bottom: 0.3rem;
}
.pipeline-desc {
    font-size: 0.75rem;
    color: #7aa8cc;
}
.pipeline-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(58,123,213,0.5);
    font-size: 1.5rem;
    font-weight: 700;
}

/* ── Status Widgets ── */
[data-testid="stStatusWidget"] {
    background: rgba(14,26,46,0.9) !important;
    border: 1px solid rgba(58,123,213,0.25) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
}
[data-testid="stStatusWidget"] > div:first-child {
    background: rgba(14,26,46,0.95) !important;
    border-radius: 16px 16px 0 0 !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
}
[data-testid="stStatusWidget"] details,
[data-testid="stStatusWidget"] details > div,
[data-testid="stStatusWidget"] [data-testid="stVerticalBlock"] {
    background: rgba(10,21,32,0.95) !important;
    color: #ffffff !important;
    padding: 0.5rem 1rem !important;
}

/* ── Metrics ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-box {
    flex: 1;
    background: rgba(14,22,35,0.8);
    border: 1px solid rgba(58,123,213,0.2);
    border-radius: 16px;
    padding: 1.5rem 1rem;
    text-align: center;
    backdrop-filter: blur(16px);
    transition: all 0.3s ease;
}
.metric-box:hover {
    transform: translateY(-5px);
    border-color: rgba(58,123,213,0.5);
    box-shadow: 0 15px 30px rgba(26,107,191,0.15);
}
.metric-val {
    font-size: 2.5rem;
    font-weight: 800;
    color: #4ea8f0;
    text-shadow: 0 0 20px rgba(78,168,240,0.3);
}
.metric-lbl {
    font-size: 0.8rem;
    color: #8ab8d8;
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

/* ── Final Plan Card ── */
.final-card {
    background: rgba(12,26,46,0.9);
    border: 1px solid rgba(58,123,213,0.3);
    border-left: 4px solid #3a7bd5;
    border-radius: 20px;
    padding: 2rem;
    line-height: 1.9;
    color: #cce0f5;
    font-size: 1rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.4);
}
.final-card h1, .final-card h2, .final-card h3 {
    color: #e8f4ff;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid rgba(58,123,213,0.2);
    padding-bottom: 0.5rem;
}
.final-card strong { color: #7ab8f5; }

/* ── Section Headers ── */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin: 2.5rem 0 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(58,123,213,0.25);
}
.sec-head span {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e0f2fe;
}

/* ── Save Bar ── */
.save-bar {
    background: rgba(14,22,35,0.8);
    border: 1px solid rgba(58,123,213,0.2);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #8ab8d8;
    font-size: 0.9rem;
    backdrop-filter: blur(16px);
}

/* ── Sidebar (Brighter) ── */
section[data-testid="stSidebar"] {
    background: rgba(8,12,20,0.95) !important;
    border-right: 1px solid rgba(20,31,48,0.8) !important;
}
.sidebar-chip {
    background: rgba(14,26,43,0.9);
    border: 1px solid rgba(26,107,191,0.3);
    border-radius: 10px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: #a5c8e8;
    font-weight: 500;
    transition: all 0.3s ease;
}
.sidebar-chip:hover {
    background: rgba(26,107,191,0.2);
    border-color: #3a7bd5;
    transform: translateX(5px);
}
.sidebar-title {
    color: #e0f2fe;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 1.5rem 0 0.8rem;
    letter-spacing: 0.02em;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: rgba(10,21,32,0.9) !important;
    border: 1px solid rgba(58,123,213,0.3) !important;
    border-radius: 14px !important;
    color: #e8f4ff !important;
    font-size: 1rem !important;
    resize: none !important;
    padding: 1rem !important;
}
.stTextArea textarea:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 3px rgba(58,123,213,0.2) !important;
}

/* ── Text Input ── */
input[type="text"], .stTextInput input {
    background: rgba(14,26,43,0.9) !important;
    border: 1px solid rgba(26,107,191,0.3) !important;
    border-radius: 10px !important;
    color: #e0f2fe !important;
}

/* ── Download Button ── */
div[data-testid="stDownloadButton"] > button {
    background: rgba(26,58,92,0.9) !important;
    color: #e8f4ff !important;
    border: 1px solid rgba(58,123,213,0.4) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(34,80,128,0.9) !important;
    box-shadow: 0 8px 20px rgba(26,107,191,0.3) !important;
    transform: translateY(-2px) !important;
}

/* ── Hide branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🌍 AI Travel Planner</div>", unsafe_allow_html=True)
    st.markdown("---")

    thread_id = st.text_input("👤 User ID", value="aarohi_user",
                              help="Your session ID — keeps travel history across queries")

    st.markdown("<div class='sidebar-title'>⚡ Powered by</div>", unsafe_allow_html=True)
    for tech in ["🔗 LangGraph", "🧠 Groq · LLaMA 3.3 70B", "🐘 PostgreSQL", "🔍 Tavily Search", "✈️ AviationStack"]:
        st.markdown(f"<div class='sidebar-chip'>{tech}</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>🤖 Agent Pipeline</div>", unsafe_allow_html=True)
    for step in ["① Flight Agent", "② Hotel Agent", "③ Itinerary Agent", "④ Final Agent"]:
        st.markdown(f"<div class='sidebar-chip'>{step}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  HERO SECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrapper">
    <img class="hero-bg"
         src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
         alt="airplane above clouds"/>
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-badge">✦ Multi-Agent AI System</div>
        <div class="hero-title">✈️ AI Travel Booking System</div>
        <div class="hero-sub">Four specialized agents work together — searching flights, hotels, building an itinerary, and delivering your perfect trip plan.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  DESTINATION CARDS (Bright & Clear using Streamlit Columns)
# ═══════════════════════════════════════════════════════════════════════════════
DESTINATIONS = [
    ("🇯🇵 Tokyo",     "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400&q=80"),
    ("🇫🇷 Paris",     "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400&q=80"),
    ("🇹🇭 Bangkok",   "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=400&q=80"),
    ("🇮🇹 Rome",      "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=400&q=80"),
    ("🇦🇪 Dubai",     "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=400&q=80"),
]

st.markdown("<br>", unsafe_allow_html=True)
cols = st.columns(5)
for col, (name, img_url) in zip(cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div class="dest-card">
            <img src="{img_url}" alt="{name}" loading="lazy" />
            <div class="dest-label">{name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  VISUAL AGENT PIPELINE (Left-to-Right Steps)
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="sec-head"><span>🛠️ How It Works</span></div>
""", unsafe_allow_html=True)

p1, p2, p3, p4, p5, p6, p7 = st.columns([2,0.5,2,0.5,2,0.5,2])

with p1:
    st.markdown("""
    <div class="pipeline-box">
        <span class="pipeline-icon">✈️</span>
        <div class="pipeline-title">Flight Agent</div>
        <div class="pipeline-desc">Searches best flights & routes</div>
    </div>
    """, unsafe_allow_html=True)
with p2:
    st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)
with p3:
    st.markdown("""
    <div class="pipeline-box">
        <span class="pipeline-icon">🏨</span>
        <div class="pipeline-title">Hotel Agent</div>
        <div class="pipeline-desc">Finds stays & attractions</div>
    </div>
    """, unsafe_allow_html=True)
with p4:
    st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)
with p5:
    st.markdown("""
    <div class="pipeline-box">
        <span class="pipeline-icon">🗓️</span>
        <div class="pipeline-title">Itinerary Agent</div>
        <div class="pipeline-desc">Builds day-by-day plan</div>
    </div>
    """, unsafe_allow_html=True)
with p6:
    st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)
with p7:
    st.markdown("""
    <div class="pipeline-box">
        <span class="pipeline-icon">🧠</span>
        <div class="pipeline-title">Final Agent</div>
        <div class="pipeline-desc">Combines everything</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  INPUT SECTION
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='input-label'>🗺️ Describe your trip</div>", unsafe_allow_html=True)

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

QUICK = ["7-day Japan under ₹2L", "Paris trip for 5 days", "Dubai weekend trip", "Bali backpacking 10 days"]
qcols = st.columns(len(QUICK))
for qc, label in zip(qcols, QUICK):
    with qc:
        if st.button(label, key=f"q_{label}"):
            st.session_state.user_query = label

user_query = st.text_area(
    label="Trip description",
    value=st.session_state.user_query,
    placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
    height=120,
    label_visibility="hidden",
    key="query_input"
)

generate = st.button("🚀  Generate My Travel Plan", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  AGENT PIPELINE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════
AGENT_META = {
    "flight_agent":    ("✈️", "Flight Agent"),
    "hotel_agent":     ("🏨", "Hotel Agent"),
    "itinerary_agent": ("🗓️", "Itinerary Agent"),
    "final_agent":     ("🧠", "Final Agent"),
}

if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        collected = {"flight_results": "", "hotel_results": "",
                     "itinerary": "", "final_response": "", "llm_calls": 0}

        st.markdown("---")
        st.markdown("<div class='sec-head'><span>🤖 Agent Pipeline — Live Execution</span></div>",
                    unsafe_allow_html=True)

        for chunk in app.stream(
            {
                "messages": [HumanMessage(content=user_query)],
                "user_query": user_query,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
            stream_mode="updates",
        ):
            for node_name, state_update in chunk.items():
                icon, label = AGENT_META.get(node_name, ("🔧", node_name))

                with st.status(f"{icon}  {label}", state="complete", expanded=True):
                    if node_name == "flight_agent":
                        text = state_update.get("flight_results", "")
                        collected["flight_results"] = text
                        st.markdown(text or "_No flight data returned._")

                    elif node_name == "hotel_agent":
                        text = state_update.get("hotel_results", "")
                        collected["hotel_results"] = text
                        st.markdown(text or "_No hotel data returned._")

                    elif node_name == "itinerary_agent":
                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = text
                        st.markdown(text or "_No itinerary generated._")

                    elif node_name == "final_agent":
                        msgs = state_update.get("messages", [])
                        text = msgs[-1].content if msgs else ""
                        collected["final_response"] = text
                        st.markdown(text or "_No final response._")

                    collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])

        # ── Metrics ──
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">Agents Run</div></div>
            <div class="metric-box"><div class="metric-val">{collected['llm_calls']}</div><div class="metric-lbl">LLM Calls</div></div>
            <div class="metric-box"><div class="metric-val">✅</div><div class="metric-lbl">Status</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Final Plan ──
        if collected["final_response"]:
            st.markdown("<div class='sec-head'><span>🧠 Final Travel Plan</span></div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='final-card'>{collected['final_response']}</div>",
                        unsafe_allow_html=True)

        # ── Save ──
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"
        save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
        os.makedirs(save_dir, exist_ok=True)

        file_content = f"""# Travel Plan
**Query:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {thread_id}

---

## ✈️ Flight Information
{collected['flight_results'] or 'N/A'}

---

## 🏨 Hotel Information
{collected['hotel_results'] or 'N/A'}

---

## 🗓️ Itinerary
{collected['itinerary'] or 'N/A'}

---

## 🧠 Final Travel Plan
{collected['final_response'] or 'N/A'}

---
*LLM Calls: {collected['llm_calls']}*
"""
        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write(file_content)

        dl_col, info_col = st.columns([1, 3])
        with dl_col:
            st.download_button("⬇️ Download Plan", data=file_content,
                               file_name=filename, mime="text/markdown",
                               use_container_width=True)
        with info_col:
            st.markdown(f"<div class='save-bar'>📁 Auto-saved → <code>travel_plans/{filename}</code></div>",
                        unsafe_allow_html=True)