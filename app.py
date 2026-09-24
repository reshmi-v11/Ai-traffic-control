import streamlit as st
import random
import time
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="TrafficAI - Smart Traffic Flow Simulator",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: Inter, sans-serif; }
[data-testid="stAppViewContainer"] { background: #f5f7fb; }
[data-testid="stSidebar"] { background: #101827; }
[data-testid="stSidebar"] * { color: #dce5f3; }

.brand { color:#fff; font-size:23px; font-weight:800; padding:8px 0 18px; }
.brand span { color:#938eff; }
.subbrand { color:#718096; font-size:8px; letter-spacing:1.3px; }
.live { background:#182338; border:1px solid #26344b; padding:10px;
        border-radius:9px; font-size:9px; font-weight:800; margin-bottom:18px; }
.dot { display:inline-block; width:7px; height:7px; border-radius:50%;
       background:#2bd486; margin-right:7px; }

.hero { background:linear-gradient(120deg,#171f36,#2c3b60);
        border-radius:18px; padding:28px 30px; color:white; }
.hero-label { color:#aaa6ff; font-size:9px; font-weight:800; letter-spacing:1.2px; }
.hero h1 { font-size:31px; line-height:1.15; margin:10px 0; }
.hero h1 span { color:#aaa6ff; }
.hero p { color:#bcc7d8; font-size:11px; line-height:1.7; max-width:700px; }

.metric-card { background:white; border:1px solid #e6ebf1; border-radius:13px;
               padding:16px; min-height:115px; }
.metric-icon { font-size:22px; }
.metric-title { color:#8792a3; font-size:9px; margin-top:6px; }
.metric-value { color:#172033; font-size:22px; font-weight:800; margin-top:4px; }

.card {
    background:#ffffff;
    border:1px solid #dfe6ef;
    border-radius:14px;
    padding:20px;
    color:#172033;
    box-shadow:0 4px 14px rgba(30,50,90,.06);
}
.card h2 { color:#172033 !important; font-size:28px; font-weight:800; margin:10px 0; }
.card small { color:#718096 !important; font-size:10px; font-weight:700; letter-spacing:.8px; }
.card b { color:#172033 !important; font-size:11px; }
.advisor { border-left:3px solid #5b55e8; background:#f7f7fc;
           padding:12px; font-size:10px; }
.road { height:370px; border-radius:14px; position:relative; overflow:hidden;
        background:#d7ded2;
        background-image:linear-gradient(#cbd5c7 1px,transparent 1px),
                         linear-gradient(90deg,#cbd5c7 1px,transparent 1px);
        background-size:28px 28px; }
.road-h { position:absolute; left:0; right:0; top:50%; height:105px;
          transform:translateY(-50%); background:#454c56; }
.road-v { position:absolute; top:0; bottom:0; left:50%; width:105px;
          transform:translateX(-50%); background:#454c56; }
.intersection { position:absolute; width:105px; height:105px; left:50%; top:50%;
               transform:translate(-50%,-50%); background:#3e454f; }
.car { position:absolute; font-size:25px; z-index:5; }
.map-label { position:absolute; z-index:7; background:rgba(255,255,255,.93);
             padding:6px 9px; border-radius:6px; font-size:9px; font-weight:600; }
.north { top:10px; left:55%; }
.south { bottom:10px; left:55%; }
.east { right:10px; top:54%; }
.west { left:10px; top:40%; }
.incident { padding:12px; border-bottom:1px solid #edf0f4; font-size:10px; }
.footer { color:#8994a5; font-size:8px; text-align:center; margin-top:25px; }
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
if "vehicles" not in st.session_state:
    st.session_state.vehicles = {"North": 70, "South": 38, "East": 96, "West": 55}
    st.session_state.density = {"North": 62, "South": 35, "East": 81, "West": 48}
    st.session_state.phase = "East-West"
    st.session_state.timer = 18
    st.session_state.optimized = False
    st.session_state.incidents = []
    st.session_state.history = []

DIRECTIONS = ["North", "South", "East", "West"]


def get_metrics():
    total = sum(st.session_state.vehicles.values())
    density = round(sum(st.session_state.density.values()) / 4)
    waiting = max(12, round(18 + density * 0.55 + random.uniform(-4, 4)))
    status = "HIGH" if density >= 78 else "MEDIUM" if density >= 52 else "LOW"
    return total, density, waiting, status


def reset_simulation():
    st.session_state.vehicles = {"North": 70, "South": 38, "East": 96, "West": 55}
    st.session_state.density = {"North": 62, "South": 35, "East": 81, "West": 48}
    st.session_state.phase = "East-West"
    st.session_state.timer = 18
    st.session_state.optimized = False
    st.session_state.incidents = []
    st.session_state.history = []


def optimize():
    busiest = max(DIRECTIONS, key=lambda d: st.session_state.vehicles[d])
    st.session_state.optimized = True
    st.session_state.phase = busiest
    st.session_state.timer = 35
    st.session_state.vehicles[busiest] = max(
        5, st.session_state.vehicles[busiest] - random.randint(8, 16)
    )


def simulate_incident():
    event, severity = random.choice([
        ("Road Block", "HIGH"),
        ("Accident", "CRITICAL"),
        ("Heavy Rain", "MEDIUM"),
        ("Signal Fault", "HIGH"),
    ])
    direction = random.choice(DIRECTIONS)
    st.session_state.vehicles[direction] += random.randint(8, 16)
    st.session_state.density[direction] = min(
        100, st.session_state.density[direction] + random.randint(8, 15)
    )
    st.session_state.incidents.insert(0, {
        "event": event,
        "severity": severity,
        "direction": direction,
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    st.session_state.incidents = st.session_state.incidents[:5]


def update_simulation():
    for direction in DIRECTIONS:
        change = random.randint(-5, 8)
        if st.session_state.optimized and direction == st.session_state.phase:
            change -= random.randint(2, 6)

        vehicles = max(
            5, min(180, st.session_state.vehicles[direction] + change)
        )
        density = max(
            5,
            min(100, round(vehicles / 1.2 + random.uniform(-5, 5))),
        )

        st.session_state.vehicles[direction] = vehicles
        st.session_state.density[direction] = density

    st.session_state.timer -= 1
    if st.session_state.timer <= 0:
        st.session_state.phase = (
            "North-South"
            if st.session_state.phase == "East-West"
            else "East-West"
        )
        st.session_state.timer = 30 if st.session_state.optimized else 20

    _, density, _, _ = get_metrics()
    st.session_state.history.append(density)
    st.session_state.history = st.session_state.history[-30:]


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        '<div class="brand">🚦 Traffic<span>AI</span>'
        '<div class="subbrand">FLOW INTELLIGENCE</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="live"><span class="dot"></span> LIVE SIMULATION</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        ["Dashboard", "Live Map", "Predictions", "Analytics", "Incidents"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("AI Traffic Simulator")
    st.caption("v1.0 • Python Frontend")


# ---------- Header ----------
head1, head2 = st.columns([7, 2])
with head1:
    st.title(page)
    st.caption("Real-time traffic intelligence & simulation")
with head2:
    if st.button("↻ Reset", use_container_width=True):
        reset_simulation()
        st.rerun()
    if st.button("✦ AI Optimize", type="primary", use_container_width=True):
        optimize()
        st.toast("AI optimization applied to the simulation.")
        st.rerun()

total, density, waiting, status = get_metrics()


# ---------- Dashboard ----------
if page == "Dashboard":
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-label">● REAL-TIME CITY SIMULATION</div>
            <h1>Understand traffic.<br><span>Predict what happens next.</span></h1>
            <p>Explore changing traffic conditions, adaptive signal timing and
            simulated incidents in a safe virtual environment.</p>
            <p><b>Active signal:</b> {st.session_state.phase}
            &nbsp; • &nbsp; <b>Timer:</b> {st.session_state.timer}s</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    metric_cols = st.columns(4)
    cards = [
        ("🚗", "Vehicles in network", total),
        ("◉", "Traffic density", f"{density}%"),
        ("◷", "Avg. waiting time", f"{waiting} sec"),
        ("⚡", "Active signals", "4"),
    ]

    for col, (icon, title, value) in zip(metric_cols, cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-icon">{icon}</div>'
                f'<div class="metric-title">{title}</div>'
                f'<div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.35, 1])

    with left:
        st.markdown('<div class="card"><b>Live Traffic Map</b><br>'
                    '<small>Virtual four-way intersection</small><br><br>',
                    unsafe_allow_html=True)

        st.markdown(
            '<div class="road">'
            '<div class="road-h"></div><div class="road-v"></div>'
            '<div class="intersection"></div>'
            '<div class="map-label north">NORTH</div>'
            '<div class="map-label south">SOUTH</div>'
            '<div class="map-label east">EAST</div>'
            '<div class="map-label west">WEST</div>',
            unsafe_allow_html=True,
        )

        for i, emoji in enumerate(["🚗", "🚙", "🚕", "🚗", "🚙", "🚗"]):
            x = random.randint(8, 88)
            y = 43 if i % 2 == 0 else 55
            st.markdown(
                f'<div class="car" style="left:{x}%;top:{y}%">{emoji}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div></div>", unsafe_allow_html=True)

    with right:
        st.markdown("### Traffic by Direction")
        for direction in DIRECTIONS:
            st.progress(
                st.session_state.density[direction] / 100,
                text=f"{direction}: {st.session_state.vehicles[direction]} vehicles",
            )

        st.markdown("### AI Traffic Advisor")
        if status == "HIGH":
            message = (
                "⚠️ Congestion risk is elevated. Try AI Optimize to prioritize "
                "the busiest simulated direction."
            )
        elif st.session_state.optimized:
            message = (
                "✦ Adaptive signal mode is active. The busiest direction "
                "currently receives priority."
            )
        else:
            message = (
                "Traffic is currently manageable. Run AI Optimize to test "
                "a dynamic signal strategy."
            )

        st.markdown(
            f'<div class="advisor">{message}</div>',
            unsafe_allow_html=True,
        )

        if st.button("✦ Run optimization simulation", use_container_width=True):
            optimize()
            st.rerun()

    st.subheader("Live Density Trend")
    if not st.session_state.history:
        st.session_state.history = [
            density + random.randint(-10, 10) for _ in range(12)
        ]

    st.line_chart(
        pd.DataFrame({"Traffic Density": st.session_state.history}),
        height=220,
    )


# ---------- Live Map ----------
elif page == "Live Map":
    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">● LIVE VISUALIZATION</div>
            <h1>Smart City Intersection</h1>
            <p>Watch vehicles move through the virtual intersection in real time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        f"### 🚦 Active signal: `{st.session_state.phase}` • "
        f"`{st.session_state.timer}s`"
    )

    st.markdown(
        '<div class="road" style="height:520px">'
        '<div class="road-h"></div><div class="road-v"></div>'
        '<div class="intersection"></div>'
        '<div class="map-label north">NORTH</div>'
        '<div class="map-label south">SOUTH</div>'
        '<div class="map-label east">EAST</div>'
        '<div class="map-label west">WEST</div>',
        unsafe_allow_html=True,
    )

    for i, emoji in enumerate(
        ["🚗", "🚙", "🚕", "🚗", "🚙", "🚗", "🚕", "🚙"]
    ):
        if i % 2 == 0:
            x = random.randint(5, 90)
            y = 43 if i % 3 else 55
        else:
            x = 44 if i % 3 else 55
            y = random.randint(5, 90)

        st.markdown(
            f'<div class="car" style="left:{x}%;top:{y}%">{emoji}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- Predictions ----------
elif page == "Predictions":
    st.markdown(
        '''
        <div class="hero">
            <div class="hero-label">↗ FORECAST ENGINE</div>
            <h1>Traffic Prediction</h1>
            <p>AI-powered forecast of traffic volume for the next 15 minutes.
            Monitor predicted vehicle flow and congestion risk by direction.</p>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.write("")
    predictions = {
        "North": round(st.session_state.vehicles["North"] * 1.07),
        "South": round(st.session_state.vehicles["South"] * 1.14),
        "East": round(st.session_state.vehicles["East"] * 1.21),
        "West": round(st.session_state.vehicles["West"] * 1.10),
    }

    st.subheader("Prediction Summary")
    cols = st.columns(3)
    cards = [
        ("IN 5 MINUTES", round(total * 1.07), "LOW RISK", "#e9f8f0", "#168457"),
        ("IN 10 MINUTES", round(total * 1.14), "MEDIUM RISK", "#fff4dc", "#b77900"),
        ("IN 15 MINUTES", round(total * 1.21), "HIGH RISK", "#ffe8eb", "#d9364f"),
    ]

    for col, (title, value, risk, bg, color) in zip(cols, cards):
        with col:
            st.markdown(
                f'''
                <div class="card">
                    <small>{title}</small>
                    <h2 style="color:#172033 !important;font-size:30px;
                    margin:12px 0 10px;font-weight:800;">
                    {value} vehicles</h2>
                    <span style="background:{bg};color:{color};
                    padding:7px 13px;border-radius:20px;font-size:10px;
                    font-weight:800;">{risk}</span>
                </div>
                ''',
                unsafe_allow_html=True,
            )

    st.write("")
    st.subheader("Predicted Traffic by Direction")

    rows = []
    for direction in DIRECTIONS:
        current = st.session_state.vehicles[direction]
        predicted = predictions[direction]
        increase = predicted - current
        percent = round(increase / current * 100)
        risk = "High" if predicted >= 100 else "Medium" if predicted >= 60 else "Low"
        rows.append({
            "Direction": direction,
            "Current": current,
            "Predicted (15 min)": predicted,
            "Increase": f"+{increase} ({percent}%)",
            "Risk": risk,
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )

    st.write("")
    st.subheader("Traffic Forecast")

    chart = pd.DataFrame({
        "Now": [st.session_state.vehicles[d] for d in DIRECTIONS],
        "5 min": [round(st.session_state.vehicles[d] * m)
                  for d, m in zip(DIRECTIONS, [1.03, 1.04, 1.07, 1.05])],
        "10 min": [round(st.session_state.vehicles[d] * m)
                   for d, m in zip(DIRECTIONS, [1.05, 1.08, 1.14, 1.08])],
        "15 min": [predictions[d] for d in DIRECTIONS],
    }, index=DIRECTIONS)

    st.line_chart(chart, height=350)

    highest = max(predictions, key=predictions.get)
    highest_value = predictions[highest]

    if highest_value >= 100:
        st.error(
            f"⚠️ **{highest} direction is predicted to experience high "
            f"traffic ({highest_value} vehicles) within 15 minutes.**"
        )
    elif highest_value >= 60:
        st.warning(
            f"⚠️ **{highest} direction may become moderately congested "
            f"within 15 minutes.**"
        )
    else:
        st.success(
            "✓ Traffic conditions are expected to remain manageable "
            "over the next 15 minutes."
        )

# ---------- Analytics ----------
elif page == "Analytics":
    metric_cols = st.columns(4)
    for col, title, value in zip(
        metric_cols,
        ["Network vehicles", "Density", "Waiting time", "Incidents"],
        [total, f"{density}%", f"{waiting} sec", len(st.session_state.incidents)],
    ):
        col.metric(title, value)

    st.subheader("Direction Analytics")

    df = pd.DataFrame(
        {
            "Direction": DIRECTIONS,
            "Vehicles": [
                st.session_state.vehicles[d] for d in DIRECTIONS
            ],
            "Density (%)": [
                st.session_state.density[d] for d in DIRECTIONS
            ],
        }
    )

    df["Status"] = df["Density (%)"].apply(
        lambda x: "Congested" if x > 75 else ("Busy" if x > 50 else "Clear")
    )

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Vehicle Distribution")
    st.bar_chart(df.set_index("Direction")["Vehicles"])


# ---------- Incidents ----------
else:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">⚠ INCIDENT SIMULATOR</div>
            <h1>Test unexpected traffic events</h1>
            <p>Generate safe simulated events and observe the dashboard response.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("⚠ Simulate Incident", type="primary"):
        simulate_incident()
        st.toast("Incident simulated.")
        st.rerun()

    st.subheader("Recent Incidents")

    if not st.session_state.incidents:
        st.info("No incidents. Generate one to test the system.")

    for item in st.session_state.incidents:
        st.markdown(
            f'<div class="incident"><b>⚠ {item["event"]}</b> — '
            f'{item["direction"]} direction<br>'
            f'<small>{item["time"]} • {item["severity"]}</small></div>',
            unsafe_allow_html=True,
        )


# ---------- Live simulation loop ----------
update_simulation()

st.markdown(
    '<div class="footer">Frontend-only simulation • '
    'No real traffic infrastructure is controlled.</div>',
    unsafe_allow_html=True,
)

time.sleep(1.2)
st.rerun()
