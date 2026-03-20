import streamlit as st
import requests
import time
import json as _json

st.set_page_config(page_title="SLA Risk Copilot", page_icon="🚚", layout="wide")
API_URL = "https://opsintellect-ai.onrender.com/predict"

for k, v in {"drivers_available":22,"traffic_index":1.2,"system_latency_ms":120,"priority":"MEDIUM","promised_mins":40,"last_result":None}.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@700&family=Syne:wght@700;800&family=DM+Sans:wght@400;600&display=swap');
*{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}

[data-testid="stAppViewContainer"]{
    background:linear-gradient(160deg,#060b18 0%,#0a1020 50%,#080e1c 100%);
    color:#e2e8f0;min-height:100vh;
}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stSidebar"]{display:none;}
.block-container{padding:2rem 2.5rem 3rem;max-width:1440px;}

/* HERO */
.hero{position:relative;padding:36px 40px 28px;border-radius:24px;overflow:hidden;
    background:linear-gradient(135deg,rgba(0,212,255,0.08),rgba(99,102,241,0.06));
    border:1px solid rgba(0,212,255,0.18);margin-bottom:1.8rem;
    box-shadow:0 20px 50px rgba(0,0,0,0.4),inset 0 1px 0 rgba(255,255,255,0.05);}
.hero-eyebrow{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:0.2em;text-transform:uppercase;color:rgba(0,212,255,0.75);margin-bottom:10px;display:flex;align-items:center;gap:8px;}
.hero-eyebrow::before{content:"";display:inline-block;width:24px;height:1px;background:rgba(0,212,255,0.5);}
.hero-title{font-family:'Syne',sans-serif;font-size:44px;font-weight:800;line-height:1.1;
    background:linear-gradient(135deg,#fff 30%,rgba(0,212,255,0.9) 70%,rgba(99,102,241,0.9) 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:8px;}
.hero-sub{font-size:14px;color:rgba(226,232,240,0.6);max-width:500px;line-height:1.6;}
.hero-badge{position:absolute;top:24px;right:28px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;
    color:rgba(16,185,129,0.9);background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);
    padding:5px 12px;border-radius:999px;display:flex;align-items:center;gap:6px;}
.hero-badge::before{content:"";width:5px;height:5px;border-radius:50%;background:#10b981;animation:blink 1.4s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.3;}}

/* GLASS CARD */
.glass-card{position:relative;border-radius:18px;padding:18px 20px;
    background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
    box-shadow:0 12px 30px rgba(0,0,0,0.3);overflow:hidden;}
.glass-card::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);}
.section-title{font-family:'Syne',sans-serif;font-size:12px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;
    color:rgba(0,212,255,0.65);margin-bottom:12px;display:flex;align-items:center;gap:7px;}
.section-title::before{content:"";width:3px;height:12px;border-radius:2px;background:linear-gradient(180deg,#00d4ff,#6366f1);flex-shrink:0;}

/* RISK */
.risk-low,.risk-medium,.risk-high{padding:16px 22px;border-radius:16px;font-family:'Syne',sans-serif;font-size:19px;font-weight:800;letter-spacing:0.05em;}
.risk-low{background:linear-gradient(135deg,rgba(16,185,129,0.16),rgba(16,185,129,0.06));border:1px solid rgba(16,185,129,0.38);color:#6ee7b7;}
.risk-medium{background:linear-gradient(135deg,rgba(245,158,11,0.16),rgba(245,158,11,0.06));border:1px solid rgba(245,158,11,0.38);color:#fcd34d;}
.risk-high{background:linear-gradient(135deg,rgba(239,68,68,0.16),rgba(239,68,68,0.06));border:1px solid rgba(239,68,68,0.38);color:#fca5a5;}
.conclusion-text{font-family:'DM Sans',sans-serif;font-size:13px;font-weight:400;opacity:0.8;margin-top:5px;}

/* METRICS */
[data-testid="stMetric"]{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:10px 13px!important;}
[data-testid="stMetricLabel"]{font-family:'Space Mono',monospace!important;font-size:9px!important;letter-spacing:0.12em!important;text-transform:uppercase!important;color:rgba(148,163,184,0.65)!important;}
[data-testid="stMetricValue"]{font-family:'Syne',sans-serif!important;font-size:19px!important;font-weight:700!important;color:#e2e8f0!important;}

/* SLIDERS / SELECT */
[data-testid="stSlider"]>div>div>div{background:rgba(0,212,255,0.15)!important;}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]{background:linear-gradient(135deg,#00d4ff,#6366f1)!important;}
[data-baseweb="select"]>div{background:rgba(255,255,255,0.04)!important;border-color:rgba(255,255,255,0.1)!important;border-radius:10px!important;}

/* BUTTONS */
[data-testid="stButton"]>button{width:100%;border-radius:12px;border:1px solid rgba(255,255,255,0.1);
    background:rgba(255,255,255,0.04);color:rgba(226,232,240,0.85);
    font-family:'DM Sans',sans-serif;font-weight:600;font-size:13px;padding:0.6rem 1rem;
    transition:border-color 0.15s,background 0.15s,color 0.15s;}
[data-testid="stButton"]>button:hover{border-color:rgba(0,212,255,0.35);background:rgba(0,212,255,0.08);color:#fff;}
[data-testid="stButton"]>button:active{transform:scale(0.98);}

/* PROBABILITY */
.prob-label{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:rgba(148,163,184,0.55);margin-bottom:3px;}
.prob-value{font-family:'Syne',sans-serif;font-size:28px;font-weight:800;margin-bottom:7px;}
.prob-met{color:#6ee7b7;}.prob-fail{color:#fca5a5;}
.inline-bar-track{width:100%;height:5px;background:rgba(255,255,255,0.06);border-radius:999px;overflow:hidden;}
.inline-bar-fill{height:100%;border-radius:999px;}
.bar-met{background:linear-gradient(90deg,#10b981,#34d399);}
.bar-fail{background:linear-gradient(90deg,#ef4444,#f87171);}
.bar-pct{font-family:'Space Mono',monospace;font-size:9px;color:rgba(148,163,184,0.45);margin-top:3px;}

/* REASON / IMPROVE */
.reason-item,.improve-item{display:flex;align-items:flex-start;gap:9px;padding:8px 11px;margin-bottom:6px;border-radius:10px;font-size:13px;line-height:1.5;}
.reason-item{background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.12);color:rgba(199,210,254,0.9);}
.improve-item{background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.12);color:rgba(167,243,208,0.9);}
.reason-dot{flex-shrink:0;margin-top:5px;width:5px;height:5px;border-radius:50%;background:#818cf8;}
.improve-dot{flex-shrink:0;margin-top:5px;width:5px;height:5px;border-radius:50%;background:#34d399;}

hr{border:none!important;height:1px!important;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.15),transparent)!important;margin:1.2rem 0!important;}
[data-testid="stWidgetLabel"] p{font-size:13px!important;color:rgba(148,163,184,0.75)!important;font-weight:500!important;}

/* ══ CHAT FAB ══ */
.chat-fab{
    position:fixed;left:20px;bottom:20px;z-index:10000;
    width:52px;height:52px;border-radius:50%;
    background:linear-gradient(135deg,#00d4ff,#6366f1);
    box-shadow:0 4px 20px rgba(0,212,255,0.45);
    display:flex;align-items:center;justify-content:center;font-size:22px;
    cursor:pointer;user-select:none;transition:transform 0.15s,box-shadow 0.15s;
}
.chat-fab:hover{transform:scale(1.08);box-shadow:0 6px 28px rgba(0,212,255,0.6);}
.chat-fab:active{transform:scale(0.95);}

/* ══ CHAT PANEL ══ */
.chat-panel{
    position:fixed;left:20px;bottom:82px;z-index:9999;
    width:320px;max-width:calc(100vw - 40px);
    border-radius:18px;
    background:rgba(7,12,24,0.97);
    border:1px solid rgba(0,212,255,0.18);
    box-shadow:0 16px 48px rgba(0,0,0,0.7);
    display:none;flex-direction:column;overflow:hidden;
}
.chat-panel.open{display:flex;}
.cp-hdr{padding:12px 14px 10px;background:rgba(0,212,255,0.06);border-bottom:1px solid rgba(255,255,255,0.05);display:flex;align-items:center;gap:9px;}
.cp-av{width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,rgba(0,212,255,0.3),rgba(99,102,241,0.3));border:1px solid rgba(0,212,255,0.3);display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0;}
.cp-name{font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:#e2e8f0;}
.cp-status{font-size:10px;color:rgba(16,185,129,0.8);display:flex;align-items:center;gap:4px;margin-top:1px;}
.cp-status::before{content:"";width:4px;height:4px;border-radius:50%;background:#10b981;animation:blink 1.4s ease-in-out infinite;}
.cp-pills{padding:7px 11px 6px;display:flex;flex-wrap:wrap;gap:5px;border-bottom:1px solid rgba(255,255,255,0.05);}
.cp-pill{padding:3px 10px;border-radius:999px;font-size:11px;font-family:'DM Sans',sans-serif;font-weight:500;
    background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.18);color:rgba(0,212,255,0.8);
    cursor:pointer;transition:background 0.15s,color 0.15s;white-space:nowrap;}
.cp-pill:hover{background:rgba(0,212,255,0.18);color:#fff;}
.cp-msgs{padding:10px 12px;max-height:190px;overflow-y:auto;display:flex;flex-direction:column;gap:6px;flex:1;}
.cp-msgs::-webkit-scrollbar{width:2px;}
.cp-msgs::-webkit-scrollbar-thumb{background:rgba(0,212,255,0.2);border-radius:1px;}
.msg-u{align-self:flex-end;max-width:88%;padding:6px 10px;border-radius:12px 12px 2px 12px;font-size:12px;line-height:1.45;
    background:linear-gradient(135deg,rgba(0,212,255,0.2),rgba(99,102,241,0.2));border:1px solid rgba(0,212,255,0.2);color:#e2e8f0;}
.msg-b{align-self:flex-start;max-width:88%;padding:6px 10px;border-radius:12px 12px 12px 2px;font-size:12px;line-height:1.45;
    background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);color:rgba(226,232,240,0.9);}
.cp-inp-row{padding:7px 10px 10px;border-top:1px solid rgba(255,255,255,0.05);display:flex;gap:6px;background:rgba(0,0,0,0.15);}
.cp-inp{flex:1;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:9px;
    color:#e2e8f0;font-family:'DM Sans',sans-serif;font-size:12px;padding:6px 10px;outline:none;transition:border-color 0.15s;}
.cp-inp:focus{border-color:rgba(0,212,255,0.4);}
.cp-inp::placeholder{color:rgba(148,163,184,0.35);}
.cp-send{flex-shrink:0;padding:6px 12px;border-radius:9px;cursor:pointer;
    background:linear-gradient(135deg,rgba(0,212,255,0.25),rgba(99,102,241,0.25));
    border:1px solid rgba(0,212,255,0.3);color:#00d4ff;
    font-family:'DM Sans',sans-serif;font-size:12px;font-weight:700;transition:background 0.15s,color 0.15s;}
.cp-send:hover{background:linear-gradient(135deg,rgba(0,212,255,0.4),rgba(99,102,241,0.4));color:#fff;}

[data-testid="stBottom"]{display:none!important;}
</style>
""", unsafe_allow_html=True)

# ── HERO
st.markdown("""
<div class="hero">
    <div class="hero-badge">LIVE SYSTEM</div>
    <div class="hero-eyebrow">Delivery Intelligence Platform</div>
    <div class="hero-title">SLA Risk Copilot</div>
    <div class="hero-sub">Real-time SLA breach prediction, explainability, and action guidance for last-mile delivery operations.</div>
</div>
""", unsafe_allow_html=True)

# ── SCENARIO BUTTONS
c1,c2,c3 = st.columns(3)
with c1:
    if st.button("🟢  Load LOW Scenario"):
        st.session_state.drivers_available=45;st.session_state.traffic_index=0.6
        st.session_state.system_latency_ms=60;st.session_state.priority="LOW";st.session_state.promised_mins=50
with c2:
    if st.button("🟡  Load MEDIUM Scenario"):
        st.session_state.drivers_available=22;st.session_state.traffic_index=1.2
        st.session_state.system_latency_ms=120;st.session_state.priority="MEDIUM";st.session_state.promised_mins=40
with c3:
    if st.button("🔴  Load HIGH Scenario"):
        st.session_state.drivers_available=0;st.session_state.traffic_index=4.0
        st.session_state.system_latency_ms=550;st.session_state.priority="HIGH";st.session_state.promised_mins=12

st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

# ── INPUT + SUMMARY
left,right = st.columns([1.15,1],gap="large")
with left:
    st.markdown('<div class="glass-card"><div class="section-title">Order Input Panel</div></div>', unsafe_allow_html=True)
    st.slider("Drivers Available",  0,100, st.session_state.drivers_available,           key="drivers_available")
    st.slider("Traffic Index",      0.0,5.0,float(st.session_state.traffic_index),0.1,   key="traffic_index")
    st.slider("System Latency (ms)",0,1000,st.session_state.system_latency_ms,10,         key="system_latency_ms")
    st.selectbox("Priority",["LOW","MEDIUM","HIGH"],index=["LOW","MEDIUM","HIGH"].index(st.session_state.priority),key="priority")
    st.slider("Promised Minutes",   5,120, st.session_state.promised_mins,                key="promised_mins")
    predict_btn = st.button("⚡  Predict SLA Risk")
with right:
    st.markdown('<div class="glass-card"><div class="section-title">Live Summary</div></div>', unsafe_allow_html=True)
    a,b = st.columns(2)
    a.metric("Drivers", st.session_state.drivers_available)
    b.metric("Traffic", st.session_state.traffic_index)
    a.metric("Latency", st.session_state.system_latency_ms)
    b.metric("Promise", st.session_state.promised_mins)
    st.metric("Priority", st.session_state.priority)

# ── PREDICTION
if predict_btn:
    payload={"drivers_available":int(st.session_state.drivers_available),"traffic_index":float(st.session_state.traffic_index),"system_latency_ms":int(st.session_state.system_latency_ms),"priority":st.session_state.priority,"promised_mins":int(st.session_state.promised_mins)}
    try:
        with st.spinner("Analyzing…"):
            time.sleep(0.4)
            r=requests.post(API_URL,json=payload,timeout=10);r.raise_for_status()
            st.session_state.last_result=r.json()
    except Exception as e:
        st.error(f"API call failed: {e}")

result = st.session_state.last_result

# ── RESULTS
if result:
    st.divider()
    pm=float(result['probability_sla_met']); pf=float(result['probability_sla_fail'])
    x,y=st.columns(2)
    with x:
        st.markdown(f'<div class="glass-card" style="padding:13px 18px;"><div class="prob-label">SLA Will Be Met</div><div class="prob-value prob-met">{pm:.3f}</div><div class="inline-bar-track"><div class="inline-bar-fill bar-met" style="width:{int(pm*100)}%"></div></div><div class="bar-pct">{int(pm*100)}% confidence</div></div>', unsafe_allow_html=True)
    with y:
        st.markdown(f'<div class="glass-card" style="padding:13px 18px;"><div class="prob-label">SLA Will Fail</div><div class="prob-value prob-fail">{pf:.3f}</div><div class="inline-bar-track"><div class="inline-bar-fill bar-fail" style="width:{int(pf*100)}%"></div></div><div class="bar-pct">{int(pf*100)}% risk</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:0.7rem'></div>", unsafe_allow_html=True)
    cat=result["risk_category"]; conc=result["conclusion"]
    if cat=="LOW":   st.markdown(f'<div class="risk-low">🟢 &nbsp;LOW RISK<div class="conclusion-text">{conc}</div></div>',   unsafe_allow_html=True)
    elif cat=="MEDIUM": st.markdown(f'<div class="risk-medium">🟡 &nbsp;MEDIUM RISK<div class="conclusion-text">{conc}</div></div>', unsafe_allow_html=True)
    else: st.markdown(f'<div class="risk-high">🔴 &nbsp;HIGH RISK<div class="conclusion-text">{conc}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:0.8rem'></div>", unsafe_allow_html=True)
    rh="".join([f'<div class="reason-item"><span class="reason-dot"></span><span>{i}</span></div>' for i in result.get("reasoning",[])])
    ih="".join([f'<div class="improve-item"><span class="improve-dot"></span><span>{i}</span></div>' for i in result.get("improvements",[])])
    r1,r2=st.columns(2,gap="large")
    with r1: st.markdown(f'<div class="glass-card"><div class="section-title">Why this prediction?</div>{rh}</div>', unsafe_allow_html=True)
    with r2: st.markdown(f'<div class="glass-card"><div class="section-title">How to improve it?</div>{ih}</div>', unsafe_allow_html=True)

# ══ FLOATING CHAT ══
import streamlit.components.v1 as components
_rjs = _json.dumps(result) if result else "null"

_chat_html = (
"<script>(function(){"
"var pd=window.parent.document,e;"
"e=pd.getElementById('sla-root');if(e)e.remove();"
"e=pd.getElementById('sla-styles');if(e)e.remove();"
"var s=pd.createElement('style');s.id='sla-styles';"
"s.textContent="
"'#sla-fab{position:fixed;left:20px;bottom:20px;z-index:2147483647;width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#00d4ff,#6366f1);box-shadow:0 4px 20px rgba(0,212,255,.5);display:flex;align-items:center;justify-content:center;font-size:22px;cursor:pointer;user-select:none;border:none;outline:none;transition:transform .15s;}'"
"+'#sla-fab:hover{transform:scale(1.1);}'"
"+'#sla-fab:active{transform:scale(0.94);}'"
"+'#sla-panel{position:fixed;left:20px;bottom:82px;z-index:2147483646;width:320px;border-radius:18px;background:#070c18;border:1px solid rgba(0,212,255,.22);box-shadow:0 16px 48px rgba(0,0,0,.85);flex-direction:column;overflow:hidden;display:none;font-family:system-ui,sans-serif;}'"
"+'#sla-panel.open{display:flex;}'"
"+'#sla-hdr{padding:11px 14px 9px;background:rgba(0,212,255,.06);border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;gap:9px;}'"
"+'#sla-av{width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,rgba(0,212,255,.3),rgba(99,102,241,.3));border:1px solid rgba(0,212,255,.3);display:flex;align-items:center;justify-content:center;font-size:15px;}'"
"+'#sla-nm{font-weight:700;font-size:13px;color:#e2e8f0;}'"
"+'#sla-st{font-size:10px;color:rgba(16,185,129,.85);display:flex;align-items:center;gap:4px;margin-top:1px;}'"
"+'#sla-st::before{content:\"\";width:4px;height:4px;border-radius:50%;background:#10b981;}'"
"+'#sla-pills{padding:7px 11px 6px;display:flex;flex-wrap:wrap;gap:5px;border-bottom:1px solid rgba(255,255,255,.05);}'"
"+'#sla-pills span{padding:3px 10px;border-radius:999px;font-size:11px;font-weight:500;background:rgba(0,212,255,.07);border:1px solid rgba(0,212,255,.18);color:rgba(0,212,255,.85);cursor:pointer;white-space:nowrap;}'"
"+'#sla-pills span:hover{background:rgba(0,212,255,.2);color:#fff;}'"
"+'#sla-msgs{padding:10px 12px;flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:6px;max-height:190px;}'"
"+'#sla-msgs::-webkit-scrollbar{width:2px;}'"
"+'#sla-msgs::-webkit-scrollbar-thumb{background:rgba(0,212,255,.2);}'"
"+'#sla-msgs .u{align-self:flex-end;max-width:88%;padding:6px 10px;border-radius:12px 12px 2px 12px;font-size:12px;line-height:1.45;background:linear-gradient(135deg,rgba(0,212,255,.2),rgba(99,102,241,.2));border:1px solid rgba(0,212,255,.2);color:#e2e8f0;}'"
"+'#sla-msgs .b{align-self:flex-start;max-width:88%;padding:6px 10px;border-radius:12px 12px 12px 2px;font-size:12px;line-height:1.45;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);color:rgba(226,232,240,.9);}'"
"+'#sla-inprow{padding:7px 10px 10px;border-top:1px solid rgba(255,255,255,.05);display:flex;gap:6px;background:rgba(0,0,0,.18);}'"
"+'#sla-inp{flex:1;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:9px;color:#e2e8f0;font-size:12px;padding:6px 10px;outline:none;}'"
"+'#sla-inp:focus{border-color:rgba(0,212,255,.4);}'"
"+'#sla-inp::placeholder{color:rgba(148,163,184,.35);}'"
"+'#sla-send{flex-shrink:0;padding:6px 12px;border-radius:9px;cursor:pointer;background:linear-gradient(135deg,rgba(0,212,255,.25),rgba(99,102,241,.25));border:1px solid rgba(0,212,255,.3);color:#00d4ff;font-size:12px;font-weight:700;}'"
"+'#sla-send:hover{background:linear-gradient(135deg,rgba(0,212,255,.45),rgba(99,102,241,.45));color:#fff;}';"
"pd.head.appendChild(s);"
"var root=pd.createElement('div');root.id='sla-root';"
"root.innerHTML='<button id=\"sla-fab\" title=\"SLA Assistant\">&#x1F916;</button>'"
"+'<div id=\"sla-panel\">'"
"+'<div id=\"sla-hdr\"><div id=\"sla-av\">&#x1F916;</div><div><div id=\"sla-nm\">SLA Assistant</div><div id=\"sla-st\">Online</div></div></div>'"
"+'<div id=\"sla-pills\">'"
"+'<span data-q=\"Why is this order risky?\">Why risky?</span>'"
"+'<span data-q=\"What is the main issue?\">Main issue?</span>'"
"+'<span data-q=\"How to improve?\">How to improve?</span>'"
"+'<span data-q=\"What is the probability?\">Probability?</span>'"
"+'</div>'"
"+'<div id=\"sla-msgs\"><div class=\"b\">&#x1F44B; Hi! Run a prediction then ask me anything.</div></div>'"
"+'<div id=\"sla-inprow\"><input id=\"sla-inp\" placeholder=\"Ask something...\"/><button id=\"sla-send\">Send</button></div>'"
"+'</div>';"
"pd.body.appendChild(root);"
"var R=__RESULT__,isOpen=false;"
"pd.getElementById('sla-fab').onclick=function(){isOpen=!isOpen;pd.getElementById('sla-panel').classList[isOpen?'add':'remove']('open');if(isOpen){scr();pd.getElementById('sla-inp').focus();}};"
"pd.querySelectorAll('#sla-pills span').forEach(function(p){p.onclick=function(){snd(p.getAttribute('data-q'));};});"
"pd.getElementById('sla-send').onclick=function(){snd();};"
"pd.getElementById('sla-inp').onkeydown=function(e){if(e.key==='Enter')snd();};"
"function scr(){var m=pd.getElementById('sla-msgs');if(m)m.scrollTop=m.scrollHeight;}"
"function add(txt,u){var m=pd.getElementById('sla-msgs'),d=pd.createElement('div');d.className=u?'u':'b';d.textContent=txt;m.appendChild(d);scr();}"
"function rep(q){if(!R)return'Run a prediction first!';"
"var rs=R.reasoning||[],im=R.improvements||[];"
"var rt=rs.length?rs.join('; '):'the current inputs';"
"var it=im.length?im.join('; '):'continue normal monitoring';"
"var ql=q.toLowerCase();"
"if(['hi','hello','hey'].indexOf(ql)>=0)return'Ask: Why risky? / Main issue? / How to improve? / Probability?';"
"if(ql.includes('why')&&(ql.includes('risk')||ql.includes('risky')))return'Risky mainly because '+rt+'.';"
"if(ql.includes('main')||ql.includes('issue')||ql.includes('fail'))return'Main factors: '+rt+'.';"
"if(ql.includes('improve')||ql.includes('fix')||ql.includes('reduce'))return'To improve: '+it+'.';"
"if(ql.includes('driver')){var dr=rs.filter(function(r){return r.includes('driver')});return dr.length?dr.join('; ')+'.':'Driver not main issue.';}"
"if(ql.includes('traffic')){var tr=rs.filter(function(r){return r.includes('traffic')});return tr.length?tr.join('; ')+'.':'Traffic not main issue.';}"
"if(ql.includes('latency')||ql.includes('system')){var lr=rs.filter(function(r){return r.includes('latency')||r.includes('system')});return lr.length?lr.join('; ')+'.':'Latency not main issue.';}"
"if(ql.includes('prob')||ql.includes('chance')||ql.includes('sla'))return'SLA meet: '+R.probability_sla_met+'. Fail: '+R.probability_sla_fail+'.';"
"if(ql.includes('time')||ql.includes('promised')){var pr=rs.filter(function(r){return r.includes('promised')||r.includes('tight')});return pr.length?pr.join('; ')+'.':'Promised time not main issue.';}"
"return'Reasons: '+rt+'. Actions: '+it+'.';}"
"function snd(preset){var inp=pd.getElementById('sla-inp'),val=preset||inp.value.trim();if(!val)return;add(val,true);inp.value='';"
"var m=pd.getElementById('sla-msgs'),t=pd.createElement('div');t.className='b';t.id='sla-t';t.innerHTML='<i style=\"opacity:.4\">typing...</i>';m.appendChild(t);scr();"
"setTimeout(function(){var x=pd.getElementById('sla-t');if(x)x.remove();add(rep(val),false);},350);}"
"})();</script>"
)

components.html(_chat_html.replace('__RESULT__', _rjs), height=0, scrolling=False)