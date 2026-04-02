"""
app.py — Quench Café · Vibe Predictor
======================================
Streamlit app with live model training — bypasses pickle entirely
to avoid Python 3.14 compatibility issues. Trains the Random Forest
on startup using the synthetic dataset, then caches it for the session.

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import os, sys

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quench · Vibe Predictor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── train model on startup (cached for session) ────────────────────────────────
@st.cache_resource(show_spinner="Training model on 8,083 orders...")
def train_model():
    """
    Load synthetic data and train the reverse model (drink → personality).
    Uses @st.cache_resource so it only trains once per session.
    No pickle files needed — avoids Python version compatibility issues.
    """
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cafe_orders_synthetic.csv")
    df = pd.read_csv(data_path)

    # Features the model uses to predict personality
    FEATURE_COLS = [
        "extra_hot", "extra_shot", "hour", "group_size",
        "food_pairing", "size", "milk", "syrup", "category",
        "cold_foam", "iced", "whipped_cream",
    ]

    # Keep only columns that exist
    available = [c for c in FEATURE_COLS if c in df.columns]
    X_raw = df[available].copy()
    y_raw = df["personality_type"]

    # One-hot encode categorical columns
    X = pd.get_dummies(X_raw)
    feature_cols = list(X.columns)

    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    # Train Random Forest — same config as vibe_model.py
    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X, y)

    return model, le, feature_cols

model, le, feature_cols = train_model()

# ── drink catalogue ────────────────────────────────────────────────────────────
MENU = {
    "Hot Coffee": [
        {"key":"americano",   "name":"Caffè Americano",         "cal":{"tall":15,"grande":25,"venti":30},    "cat":"espresso","hot":True},
        {"key":"cappuccino",  "name":"Cappuccino",               "cal":{"tall":80,"grande":140,"venti":200},  "cat":"espresso","hot":True},
        {"key":"caffe_mocha", "name":"Caffè Mocha",              "cal":{"tall":290,"grande":370,"venti":470}, "cat":"espresso","hot":True},
        {"key":"white_mocha", "name":"White Chocolate Mocha",    "cal":{"tall":360,"grande":470,"venti":580}, "cat":"espresso","hot":True},
        {"key":"caramel_mac", "name":"Caramel Macchiato",        "cal":{"tall":190,"grande":250,"venti":330}, "cat":"espresso","hot":True},
        {"key":"flat_white",  "name":"Flat White",               "cal":{"tall":170,"grande":220,"venti":300}, "cat":"espresso","hot":True},
        {"key":"cafe_latte",  "name":"Caffè Latte",              "cal":{"tall":190,"grande":240,"venti":290}, "cat":"espresso","hot":True},
        {"key":"hot_choc",    "name":"Hot Chocolate",            "cal":{"tall":300,"grande":400,"venti":520}, "cat":"hot",     "hot":True},
    ],
    "Cold Coffee": [
        {"key":"cold_brew",     "name":"Cold Brew",                              "cal":{"tall":5,"grande":5,"venti":5},       "cat":"coffee",  "hot":False},
        {"key":"vscb",          "name":"Vanilla Sweet Cream Cold Brew",          "cal":{"tall":110,"grande":200,"venti":320}, "cat":"coffee",  "hot":False},
        {"key":"iced_latte",    "name":"Iced Caffè Latte",                       "cal":{"tall":130,"grande":190,"venti":250}, "cat":"espresso","hot":False},
        {"key":"iced_mac",      "name":"Iced Caramel Macchiato",                 "cal":{"tall":180,"grande":250,"venti":330}, "cat":"espresso","hot":False},
        {"key":"brown_sugar",   "name":"Iced Brown Sugar Oatmilk Shaken Espresso","cal":{"tall":120,"grande":200,"venti":290},"cat":"espresso","hot":False},
        {"key":"iced_mocha",    "name":"Iced Caffè Mocha",                       "cal":{"tall":250,"grande":350,"venti":450}, "cat":"espresso","hot":False},
        {"key":"iced_americano","name":"Iced Caffè Americano",                   "cal":{"tall":15,"grande":25,"venti":30},    "cat":"espresso","hot":False},
    ],
    "Matcha & Tea": [
        {"key":"iced_matcha",     "name":"Iced Matcha Latte",           "cal":{"tall":200,"grande":280,"venti":360}, "cat":"latte","hot":False},
        {"key":"matcha_latte",    "name":"Matcha Latte",                "cal":{"tall":200,"grande":240,"venti":310}, "cat":"latte","hot":True},
        {"key":"lavender_matcha", "name":"Iced Lavender Cream Matcha",  "cal":{"tall":230,"grande":310,"venti":400}, "cat":"latte","hot":False},
        {"key":"chai_latte",      "name":"Chai Latte",                  "cal":{"tall":240,"grande":310,"venti":380}, "cat":"tea", "hot":True},
        {"key":"london_fog",      "name":"London Fog Latte",            "cal":{"tall":200,"grande":250,"venti":320}, "cat":"tea", "hot":True},
        {"key":"honey_citrus",    "name":"Honey Citrus Mint Tea",       "cal":{"tall":130,"grande":180,"venti":230}, "cat":"tea", "hot":True},
        {"key":"earl_grey",       "name":"Earl Grey Tea",               "cal":{"tall":0,"grande":0,"venti":0},       "cat":"tea", "hot":True},
    ],
    "Refreshers": [
        {"key":"strawberry_acai",    "name":"Strawberry Açaí Refresher",          "cal":{"tall":90,"grande":130,"venti":200},  "cat":"refresher","hot":False},
        {"key":"pink_drink",         "name":"Pink Drink",                         "cal":{"tall":140,"grande":200,"venti":290}, "cat":"refresher","hot":False},
        {"key":"dragon_drink",       "name":"Dragon Drink",                       "cal":{"tall":130,"grande":190,"venti":280}, "cat":"refresher","hot":False},
        {"key":"mango_dragonfruit",  "name":"Mango Dragonfruit Refresher",        "cal":{"tall":90,"grande":130,"venti":200},  "cat":"refresher","hot":False},
        {"key":"strawberry_lemonade","name":"Strawberry Açaí Lemonade Refresher", "cal":{"tall":120,"grande":190,"venti":280}, "cat":"refresher","hot":False},
    ],
}
ALL_DRINKS = {d["key"]: d for cat in MENU.values() for d in cat}

VIBE_META = {
    "sunny_social":        {"emoji":"☀️", "color":"#0d5c2e", "desc":"Oat milk. Cold foam. Always iced. You probably convinced two people to try matcha."},
    "chill_studious":      {"emoji":"📚", "color":"#1a237e", "desc":"Headphones in, laptop open. This is fuel, not a treat. You said please and thank you."},
    "rushed_professional": {"emoji":"💼", "color":"#33280a", "desc":"Meeting in twelve minutes. Ordered while walking in. Out before the sleeve was on."},
    "moody_intense":       {"emoji":"🖤", "color":"#1a0d1a", "desc":"Extra hot. Extra shot. You nod instead of saying thank you. The barista remembered you."},
    "cozy_comfort":        {"emoji":"🧸", "color":"#3e1f00", "desc":"You came here to stay a while. The whipped cream was non-negotiable."},
    "adventurous":         {"emoji":"🌀", "color":"#00363a", "desc":"You either asked for a recommendation or ordered something new. You'll tell someone about this."},
}

# ── SVG drink card illustrations ───────────────────────────────────────────────
DRINK_SVGS = {
    "americano":    '<rect x="20" y="30" width="80" height="80" rx="8" fill="#1a0800"/><ellipse cx="60" cy="32" rx="40" ry="10" fill="#4a2800" opacity=".8"/><path d="M100 55 Q116 55 116 70 Q116 85 100 85" fill="none" stroke="#2d1800" stroke-width="6" stroke-linecap="round"/>',
    "cappuccino":   '<rect x="18" y="28" width="84" height="76" rx="10" fill="#3d1800"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#4d2800" stroke-width="6" stroke-linecap="round"/><ellipse cx="60" cy="30" rx="42" ry="14" fill="#f0e0c8"/><ellipse cx="60" cy="26" rx="34" ry="10" fill="#fff"/>',
    "caffe_mocha":  '<rect x="18" y="28" width="84" height="76" rx="10" fill="#1a0800"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#2d1200" stroke-width="6" stroke-linecap="round"/><ellipse cx="60" cy="30" rx="42" ry="14" fill="#f5f0e8"/><ellipse cx="60" cy="24" rx="28" ry="10" fill="#fff"/><ellipse cx="44" cy="20" rx="20" ry="8" fill="#fff"/>',
    "caramel_mac":  '<rect x="18" y="28" width="84" height="76" rx="10" fill="#3d2800"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#4d3800" stroke-width="6" stroke-linecap="round"/><rect x="18" y="50" width="84" height="54" fill="#1a0a00"/><rect x="18" y="28" width="84" height="30" fill="#f5e6c8" opacity=".85"/><path d="M22 46 Q38 38 54 46 Q70 54 86 46 Q94 40 102 46" fill="none" stroke="#c8860a" stroke-width="2" opacity=".8"/>',
    "flat_white":   '<rect x="20" y="30" width="80" height="74" rx="10" fill="#2d1800"/><path d="M100 54 Q116 54 116 70 Q116 86 100 86" fill="none" stroke="#3d2800" stroke-width="5" stroke-linecap="round"/><ellipse cx="60" cy="32" rx="40" ry="12" fill="#e8c8a0"/><circle cx="60" cy="34" r="12" fill="none" stroke="#c89060" stroke-width="1.5" opacity=".5"/>',
    "hot_choc":     '<rect x="18" y="28" width="84" height="76" rx="10" fill="#1a0800"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#2d1200" stroke-width="6" stroke-linecap="round"/><ellipse cx="60" cy="30" rx="42" ry="14" fill="#f5f0e8"/><ellipse cx="60" cy="24" rx="32" ry="12" fill="#fff"/><ellipse cx="44" cy="18" rx="20" ry="9" fill="#fff"/>',
    "cold_brew":    '<rect x="20" y="18" width="80" height="96" rx="8" fill="#0d0500"/><rect x="22" y="30" width="32" height="20" rx="4" fill="rgba(255,255,255,.18)"/><rect x="22" y="58" width="36" height="22" rx="4" fill="rgba(255,255,255,.18)"/><rect x="62" y="44" width="28" height="18" rx="4" fill="rgba(255,255,255,.14)"/><ellipse cx="60" cy="20" rx="40" ry="8" fill="#1a0800" opacity=".8"/>',
    "vscb":         '<rect x="20" y="18" width="80" height="96" rx="8" fill="#1a0800"/><rect x="20" y="68" width="80" height="46" fill="#0d0500"/><rect x="20" y="18" width="80" height="56" fill="#d4a870" opacity=".6"/><rect x="22" y="25" width="30" height="20" rx="4" fill="rgba(255,255,255,.22)"/><ellipse cx="60" cy="20" rx="40" ry="8" fill="#e8c8a0"/>',
    "iced_latte":   '<rect x="20" y="18" width="80" height="96" rx="8" fill="#3d2800"/><rect x="20" y="60" width="80" height="54" fill="#1a0a00"/><rect x="20" y="18" width="80" height="48" fill="#f5e6c8" opacity=".8"/><rect x="22" y="26" width="28" height="18" rx="4" fill="rgba(255,255,255,.25)"/><rect x="60" y="34" width="26" height="16" rx="4" fill="rgba(255,255,255,.2)"/>',
    "iced_mac":     '<rect x="20" y="18" width="80" height="96" rx="8" fill="#3d2800"/><rect x="20" y="62" width="80" height="52" fill="#1a0a00"/><rect x="20" y="18" width="80" height="50" fill="#f5e6c8" opacity=".85"/><path d="M24 56 Q40 46 56 56 Q70 64 86 56 Q94 50 98 56" fill="none" stroke="#c8860a" stroke-width="2" opacity=".8"/>',
    "brown_sugar":  '<rect x="20" y="18" width="80" height="96" rx="8" fill="#2d1400"/><rect x="20" y="60" width="80" height="54" fill="#0d0500"/><rect x="20" y="18" width="80" height="48" fill="#c8a050" opacity=".75"/><circle cx="36" cy="36" r="4" fill="#5d2800" opacity=".6"/><circle cx="52" cy="28" r="3" fill="#5d2800" opacity=".5"/><circle cx="68" cy="34" r="4" fill="#5d2800" opacity=".6"/>',
    "iced_mocha":   '<rect x="20" y="18" width="80" height="96" rx="8" fill="#1a0800"/><rect x="20" y="60" width="80" height="54" fill="#0d0400"/><rect x="20" y="18" width="80" height="48" fill="#4a1800" opacity=".7"/><ellipse cx="60" cy="20" rx="40" ry="8" fill="#f5f0e8"/>',
    "iced_americano":"<rect x='20' y='18' width='80' height='96' rx='8' fill='#0d0500'/><rect x='22' y='28' width='30' height='20' rx='4' fill='rgba(255,255,255,.18)'/><rect x='22' y='56' width='34' height='20' rx='4' fill='rgba(255,255,255,.16)'/><ellipse cx='60' cy='20' rx='40' ry='8' fill='#1a0800' opacity='.7'/>",
    "iced_matcha":  '<rect x="20" y="18" width="80" height="96" rx="8" fill="#2d5a3d"/><rect x="20" y="58" width="80" height="56" fill="#4a7c59"/><rect x="20" y="18" width="80" height="46" fill="#c8e6c9" opacity=".85"/><rect x="22" y="26" width="28" height="18" rx="4" fill="rgba(255,255,255,.28)"/>',
    "matcha_latte": '<rect x="18" y="28" width="84" height="76" rx="10" fill="#1e4428"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#2d5a3d" stroke-width="5" stroke-linecap="round"/><rect x="18" y="52" width="84" height="52" fill="#4a7c59"/><rect x="18" y="28" width="84" height="30" fill="#a8d5b5" opacity=".6"/><ellipse cx="60" cy="30" rx="42" ry="12" fill="#e8f5e9"/>',
    "lavender_matcha":'<rect x="20" y="18" width="80" height="96" rx="8" fill="#2d5a3d"/><rect x="20" y="18" width="80" height="48" fill="#9b8ec4" opacity=".7"/><rect x="20" y="60" width="80" height="54" fill="#4a7c59"/>',
    "chai_latte":   '<rect x="18" y="28" width="84" height="76" rx="10" fill="#4a2810"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#5a3820" stroke-width="5" stroke-linecap="round"/><rect x="18" y="52" width="84" height="52" fill="#8b4513" opacity=".8"/><rect x="18" y="28" width="84" height="30" fill="#d4956a" opacity=".7"/><ellipse cx="60" cy="30" rx="42" ry="12" fill="#f0d8b8"/>',
    "london_fog":   '<rect x="18" y="28" width="84" height="76" rx="10" fill="#3d3020"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#4d4030" stroke-width="5" stroke-linecap="round"/><rect x="18" y="52" width="84" height="52" fill="#6b5a3d" opacity=".7"/><rect x="18" y="28" width="84" height="30" fill="#e8d5b0" opacity=".6"/><ellipse cx="60" cy="30" rx="42" ry="12" fill="#f8f4ee"/>',
    "honey_citrus": '<rect x="18" y="28" width="84" height="76" rx="10" fill="#6b4c00"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#7a5800" stroke-width="5" stroke-linecap="round"/><rect x="18" y="28" width="84" height="76" rx="10" fill="#d4a020" opacity=".6"/>',
    "earl_grey":    '<rect x="18" y="28" width="84" height="76" rx="10" fill="#3d2800"/><path d="M102 52 Q118 52 118 70 Q118 88 102 88" fill="none" stroke="#4d3800" stroke-width="5" stroke-linecap="round"/><rect x="18" y="28" width="84" height="76" rx="10" fill="#8b6914" opacity=".5"/>',
    "strawberry_acai":'<rect x="20" y="18" width="80" height="96" rx="8" fill="#4a1a2a"/><rect x="20" y="44" width="80" height="70" fill="#e91e63" opacity=".7"/><rect x="20" y="18" width="80" height="34" fill="#f48fb1" opacity=".8"/><circle cx="38" cy="72" r="8" fill="#c2185b" opacity=".9"/><circle cx="62" cy="62" r="10" fill="#c2185b" opacity=".85"/><circle cx="82" cy="80" r="7" fill="#880e4f"/>',
    "pink_drink":   '<rect x="20" y="18" width="80" height="96" rx="8" fill="#3d1a28"/><rect x="20" y="18" width="80" height="96" rx="8" fill="#f48fb1" opacity=".7"/><circle cx="36" cy="68" r="8" fill="#e91e8c" opacity=".8"/><circle cx="60" cy="56" r="10" fill="#e91e8c" opacity=".75"/><circle cx="80" cy="74" r="7" fill="#c2185b" opacity=".8"/>',
    "dragon_drink": '<rect x="20" y="18" width="80" height="96" rx="8" fill="#2a1a3d"/><rect x="20" y="18" width="80" height="96" rx="8" fill="#e040fb" opacity=".6"/><circle cx="36" cy="68" r="8" fill="#9c27b0" opacity=".8"/><circle cx="62" cy="56" r="10" fill="#9c27b0" opacity=".75"/>',
    "mango_dragonfruit":'<rect x="20" y="18" width="80" height="96" rx="8" fill="#3d1a00"/><rect x="20" y="18" width="80" height="96" rx="8" fill="#ff6d00" opacity=".6"/><circle cx="36" cy="68" r="8" fill="#e65100" opacity=".8"/><circle cx="62" cy="56" r="10" fill="#bf360c" opacity=".75"/>',
    "strawberry_lemonade":'<rect x="20" y="18" width="80" height="96" rx="8" fill="#3d1a1a"/><rect x="20" y="18" width="80" height="96" rx="8" fill="#ef5350" opacity=".55"/><circle cx="38" cy="70" r="7" fill="#c62828" opacity=".8"/><circle cx="60" cy="58" r="9" fill="#c62828" opacity=".75"/>',
}

def get_svg(key):
    content = DRINK_SVGS.get(key, DRINK_SVGS.get("americano", ""))
    return f"""<svg width="120" height="140" viewBox="0 0 120 140"
        xmlns="http://www.w3.org/2000/svg"
        style="display:block;margin:0 auto">{content}</svg>"""

def svg_to_b64(key):
    import base64
    svg = get_svg(key)
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

# ── feature builder ────────────────────────────────────────────────────────────
def build_features(drink_key, size, milk, syrup, extra_shot, extra_hot,
                   cold_foam, whipped_cream, no_ice, hour=14):
    drink = ALL_DRINKS.get(drink_key, {})
    raw = {
        "category":      drink.get("cat", "espresso"),
        "milk":          milk,
        "syrup":         "none" if syrup == "None" else syrup,
        "size":          size,
        "cold_foam":     int(cold_foam),
        "iced":          0 if drink.get("hot", True) else 1,
        "extra_shot":    int(extra_shot),
        "extra_hot":     int(extra_hot),
        "whipped_cream": int(whipped_cream),
        "food_pairing":  0,
        "hour":          hour,
        "group_size":    1,
    }
    df = pd.DataFrame([raw])
    df = pd.get_dummies(df)
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0
    # Only keep columns that exist in feature_cols
    valid_cols = [c for c in feature_cols if c in df.columns]
    df = df.reindex(columns=feature_cols, fill_value=0)
    return df

# ── styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:2rem 2rem 2rem;max-width:1200px}
.top-bar{background:#1e3932;padding:20px 32px;border-radius:16px;margin-bottom:24px;display:flex;align-items:center;justify-content:space-between}
.top-bar h1{font-family:'Playfair Display',serif;font-size:2rem;color:#fff;margin:0}
.top-bar p{color:#7fad94;font-size:.85rem;margin:4px 0 0}
.badge{background:rgba(255,255,255,.12);color:#a8d5b5;border-radius:20px;padding:6px 16px;font-size:.75rem;font-weight:600;text-align:center}
.badge b{display:block;font-size:1.4rem;color:#fff}
.drink-card{background:#fff;border:1.5px solid #e8e8e8;border-radius:16px;padding:14px 10px;text-align:center;margin-bottom:6px}
.drink-card-name{font-size:11px;font-weight:600;color:#1e3932;line-height:1.3;margin-top:6px}
.drink-card-cal{font-size:10px;color:#aaa;margin-top:2px}
.vibe-result{border-radius:20px;padding:26px 22px;color:#fff;margin-top:8px}
.vibe-emoji{font-size:2.8rem;display:block;margin-bottom:8px}
.vibe-title{font-family:'Playfair Display',serif;font-size:1.7rem;font-weight:700;font-style:italic;margin-bottom:8px}
.vibe-desc{font-size:.9rem;line-height:1.7;opacity:.88;margin-bottom:16px}
.vibe-conf{display:inline-block;background:rgba(255,255,255,.15);border-radius:20px;padding:4px 16px;font-size:.8rem;font-weight:600}
.model-note{background:#eaf4ef;border-left:3px solid #00704a;border-radius:10px;padding:14px 18px;font-size:.82rem;color:#2d5a3d;line-height:1.6;margin-top:14px}
.stSelectbox label{font-size:.75rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:.08em!important;color:#5c7f6e!important}
.stButton>button{background:#00704a!important;color:#fff!important;border:none!important;border-radius:500px!important;padding:14px 40px!important;font-size:.9rem!important;font-weight:700!important;width:100%!important}
</style>""", unsafe_allow_html=True)

# ── header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <div>
    <h1>🌿 Quench Café · Vibe Predictor</h1>
    <p>Random Forest · Trained live on 8,083 synthetic orders · UW Center Table · Winter 2026</p>
  </div>
  <div style="display:flex;gap:12px">
    <div class="badge"><b>8,083</b>Orders</div>
    <div class="badge"><b>60%</b>Accuracy</div>
    <div class="badge"><b>6</b>Vibes</div>
  </div>
</div>""", unsafe_allow_html=True)

left, right = st.columns([1.2, 1], gap="large")

with left:
    st.markdown("#### Build your order")
    category = st.selectbox("Category", list(MENU.keys()))
    drinks_in_cat = MENU[category]

    if "selected_drink" not in st.session_state:
        st.session_state["selected_drink"] = drinks_in_cat[0]["key"]

    # Show SVG drink cards in grid
    cols = st.columns(4)
    for i, drink in enumerate(drinks_in_cat):
        with cols[i % 4]:
            is_sel = drink["key"] == st.session_state["selected_drink"]
            cal = drink["cal"].get("grande", 0)
            st.markdown(f"""
            <div class="drink-card" style="border-color:{'#00704a' if is_sel else '#e8e8e8'};{'background:#eaf4ef' if is_sel else ''}">
              {get_svg(drink["key"])}
              <div class="drink-card-name">{drink['name']}</div>
              <div class="drink-card-cal">{f'{cal} cal' if cal else ''}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"{'✓' if is_sel else '+'} Select", key=f"b_{drink['key']}", use_container_width=True):
                st.session_state["selected_drink"] = drink["key"]
                st.rerun()

    drink_info = ALL_DRINKS.get(st.session_state["selected_drink"], drinks_in_cat[0])
    st.markdown(f"**Selected:** *{drink_info['name']}*")
    st.markdown("---")
    st.markdown("#### Customise")

    c1, c2 = st.columns(2)
    with c1:
        size  = st.selectbox("Size",  ["tall", "grande", "venti"], index=1)
        milk  = st.selectbox("Milk",  ["whole", "oat", "almond", "soy", "nonfat", "none"])
        syrup = st.selectbox("Syrup", ["None", "vanilla", "caramel", "hazelnut", "brown_sugar", "cinnamon_dolce"])
    with c2:
        extra_shot    = st.checkbox("Extra shot")
        extra_hot     = st.checkbox("Extra hot")
        cold_foam     = st.checkbox("Cold foam")
        whipped_cream = st.checkbox("Whipped cream")
        no_ice        = st.checkbox("No ice")

    cal_show = drink_info["cal"].get(size, 0)
    st.caption(f"{cal_show} cal · {size} · {'iced' if not drink_info['hot'] else 'hot'}")
    predict_btn = st.button("🔮  Read My Vibe", use_container_width=True)

with right:
    st.markdown("#### Vibe Reading")
    if predict_btn:
        features  = build_features(
            st.session_state["selected_drink"], size, milk, syrup,
            extra_shot, extra_hot, cold_foam, whipped_cream, no_ice
        )
        probs     = model.predict_proba(features)[0]
        classes   = le.inverse_transform(range(len(probs)))
        prob_dict = dict(sorted(zip(classes, probs), key=lambda x: -x[1]))
        top_vibe  = list(prob_dict.keys())[0]
        top_prob  = list(prob_dict.values())[0]
        meta      = VIBE_META.get(top_vibe, {"emoji":"🎭","color":"#1e3932","desc":""})

        st.markdown(f"""
        <div class="vibe-result" style="background:{meta['color']}">
          <span class="vibe-emoji">{meta['emoji']}</span>
          <div class="vibe-title">{top_vibe.replace('_',' ').title()}</div>
          <div class="vibe-desc">{meta['desc']}</div>
          <span class="vibe-conf">{top_prob*100:.0f}% model confidence</span>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Full breakdown**")
        for vibe, prob in list(prob_dict.items())[:6]:
            vmeta = VIBE_META.get(vibe, {})
            st.markdown(f"""
            <div style="margin:8px 0">
              <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                <span>{vmeta.get('emoji','')} {vibe.replace('_',' ').title()}</span>
                <span style="font-weight:700;color:#00704a">{prob*100:.0f}%</span>
              </div>
              <div style="height:6px;background:#e8f3ef;border-radius:3px;overflow:hidden">
                <div style="height:100%;width:{prob*100:.0f}%;background:#00704a;border-radius:3px"></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="model-note">
          <strong>Model:</strong> Random Forest · 300 trees · balanced class weights<br>
          <strong>Input features:</strong> {drink_info['name']} · {size} · {milk} milk
          {' · extra shot' if extra_shot else ''}
          {' · extra hot' if extra_hot else ''}
          {' · cold foam' if cold_foam else ''}<br>
          <strong>Strongest signal:</strong>
          {'extra_hot → moody_intense (~99% when combined with extra shot)' if extra_hot and extra_shot else
           'oat milk + cold foam → sunny_social' if milk == 'oat' and cold_foam else
           'drink category + milk type drove this prediction'}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#f7f7f7;border-radius:16px;padding:40px;text-align:center;margin-top:8px">
          <div style="font-size:3rem;margin-bottom:12px">🔮</div>
          <div style="font-size:1rem;font-weight:600;color:#1e3932;margin-bottom:8px">
            Select a drink and hit Read My Vibe
          </div>
          <div style="font-size:.85rem;color:#aaa;line-height:1.6">
            The Random Forest model reads your personality from drink choices —
            milk type, temperature, customizations and more.<br><br>
            <em>Model trains live from the synthetic dataset on startup.</em>
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<div style="text-align:center;font-size:.8rem;color:#aaa;padding:8px 0">
  Quench Café · Vibe Predictor · Hariharan Sureshkumar · UW MS Data Science · Winter 2026<br>
  Random Forest · 8,083 synthetic orders · 60% accuracy · 6-class personality prediction
</div>""", unsafe_allow_html=True)