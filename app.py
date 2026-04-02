"""
app.py — Quench Cafe · Vibe Predictor
======================================
Streamlit app with:
- Live Random Forest training from synthetic dataset
- Ollama LLM integration for personalized vibe descriptions
- Real drink photos via drink_images_data.py

Run: streamlit run app.py
Requires: ollama serve running in a separate terminal
"""

import streamlit as st
import pandas as pd
import os, sys, requests, json

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drink_images_data import IMGS, get

st.set_page_config(
    page_title="Quench · Vibe Predictor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Train model on startup ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Training model on 8,083 orders...")
def train_model():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cafe_orders_synthetic.csv")
    df = pd.read_csv(data_path)
    available = [c for c in ["extra_hot","extra_shot","hour","group_size","food_pairing",
                              "size","milk","syrup","category","cold_foam","iced","whipped_cream"]
                 if c in df.columns]
    X = pd.get_dummies(df[available])
    le = LabelEncoder()
    y = le.fit_transform(df["personality_type"])
    model = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X, y)
    return model, le, list(X.columns)

model, le, feature_cols = train_model()

# ── Ollama LLM description generator ──────────────────────────────────────────
def generate_description(drink_name, size, milk, syrup, extra_shot,
                          extra_hot, cold_foam, whipped_cream, vibe_name, confidence):
    """
    Calls Ollama running locally to generate a personalized vibe description.
    Falls back to a default description if Ollama is not available.
    """
    # Build a natural language summary of the order
    mods = []
    if extra_shot:    mods.append("extra shot")
    if extra_hot:     mods.append("extra hot")
    if cold_foam:     mods.append("vanilla cold foam")
    if whipped_cream: mods.append("whipped cream")
    milk_str  = f"{milk} milk" if milk not in ["none",""] else "no milk"
    syrup_str = f"{syrup} syrup" if syrup not in ["None","none",""] else ""
    order_str = f"{size} {drink_name}"
    if milk_str != "no milk": order_str += f" with {milk_str}"
    if syrup_str:             order_str += f", {syrup_str}"
    if mods:                  order_str += f", {', '.join(mods)}"

    prompt = f"""Someone just ordered a {order_str} at a university cafe.
A machine learning model predicted their personality type as "{vibe_name}" with {confidence}% confidence.

Write exactly 2 short, witty, specific sentences (no more) describing this person based on their drink order.
Be observational and slightly funny. Reference the specific drink details.
Do not use emojis. Do not use hashtags. Do not introduce yourself. Just write the 2 sentences."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.8, "num_predict": 80}
            },
            timeout=15
        )
        if response.status_code == 200:
            text = response.json().get("response", "").strip()
            # Clean up any extra lines beyond 2 sentences
            sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
            result = ". ".join(sentences[:2])
            if result and not result.endswith("."):
                result += "."
            return result, True
    except requests.exceptions.ConnectionError:
        pass
    except Exception:
        pass

    # Fallback if Ollama not running
    return None, False

# ── Drink catalogue ────────────────────────────────────────────────────────────
MENU = {
    "Hot Coffee": [
        {"key":"americano",   "name":"Caffe Americano",         "cal":{"tall":15,"grande":25,"venti":30},    "img":"americano",      "cat":"espresso","hot":True},
        {"key":"cappuccino",  "name":"Cappuccino",               "cal":{"tall":80,"grande":140,"venti":200},  "img":"cappuccino",     "cat":"espresso","hot":True},
        {"key":"caffe_mocha", "name":"Caffe Mocha",              "cal":{"tall":290,"grande":370,"venti":470}, "img":"caffe_mocha",    "cat":"espresso","hot":True},
        {"key":"white_mocha", "name":"White Chocolate Mocha",    "cal":{"tall":360,"grande":470,"venti":580}, "img":"white_mocha",    "cat":"espresso","hot":True},
        {"key":"caramel_mac", "name":"Caramel Macchiato",        "cal":{"tall":190,"grande":250,"venti":330}, "img":"caramel_mac",    "cat":"espresso","hot":True},
        {"key":"flat_white",  "name":"Flat White",               "cal":{"tall":170,"grande":220,"venti":300}, "img":"flat_white",     "cat":"espresso","hot":True},
        {"key":"cafe_latte",  "name":"Caffe Latte",              "cal":{"tall":190,"grande":240,"venti":290}, "img":"cafe_latte",     "cat":"espresso","hot":True},
        {"key":"hot_choc",    "name":"Hot Chocolate",            "cal":{"tall":300,"grande":400,"venti":520}, "img":"hot_choc",       "cat":"hot",     "hot":True},
    ],
    "Cold Coffee": [
        {"key":"cold_brew",      "name":"Cold Brew",                               "cal":{"tall":5,"grande":5,"venti":5},       "img":"cold_brew",      "cat":"coffee",  "hot":False},
        {"key":"vscb",           "name":"Vanilla Sweet Cream Cold Brew",           "cal":{"tall":110,"grande":200,"venti":320}, "img":"vscb",           "cat":"coffee",  "hot":False},
        {"key":"iced_latte",     "name":"Iced Caffe Latte",                        "cal":{"tall":130,"grande":190,"venti":250}, "img":"iced_latte",     "cat":"espresso","hot":False},
        {"key":"iced_mac",       "name":"Iced Caramel Macchiato",                  "cal":{"tall":180,"grande":250,"venti":330}, "img":"iced_mac",       "cat":"espresso","hot":False},
        {"key":"brown_sugar",    "name":"Iced Brown Sugar Oatmilk Shaken Espresso","cal":{"tall":120,"grande":200,"venti":290}, "img":"brown_sugar",    "cat":"espresso","hot":False},
        {"key":"iced_mocha",     "name":"Iced Caffe Mocha",                        "cal":{"tall":250,"grande":350,"venti":450}, "img":"iced_mocha",     "cat":"espresso","hot":False},
        {"key":"iced_americano", "name":"Iced Caffe Americano",                    "cal":{"tall":15,"grande":25,"venti":30},    "img":"iced_americano", "cat":"espresso","hot":False},
    ],
    "Matcha & Tea": [
        {"key":"iced_matcha",     "name":"Iced Matcha Latte",          "cal":{"tall":200,"grande":280,"venti":360}, "img":"iced_matcha",     "cat":"latte","hot":False},
        {"key":"matcha_latte",    "name":"Matcha Latte",               "cal":{"tall":200,"grande":240,"venti":310}, "img":"matcha_latte",    "cat":"latte","hot":True},
        {"key":"lavender_matcha", "name":"Iced Lavender Cream Matcha", "cal":{"tall":230,"grande":310,"venti":400}, "img":"lavender_matcha", "cat":"latte","hot":False},
        {"key":"chai_latte",      "name":"Chai Latte",                 "cal":{"tall":240,"grande":310,"venti":380}, "img":"chai_latte",      "cat":"tea", "hot":True},
        {"key":"london_fog",      "name":"London Fog Latte",           "cal":{"tall":200,"grande":250,"venti":320}, "img":"london_fog",      "cat":"tea", "hot":True},
        {"key":"honey_citrus",    "name":"Honey Citrus Mint Tea",      "cal":{"tall":130,"grande":180,"venti":230}, "img":"honey_citrus",    "cat":"tea", "hot":True},
        {"key":"earl_grey",       "name":"Earl Grey Tea",              "cal":{"tall":0,"grande":0,"venti":0},       "img":"earl_grey",       "cat":"tea", "hot":True},
    ],
    "Refreshers": [
        {"key":"strawberry_acai",    "name":"Strawberry Acai Refresher",          "cal":{"tall":90,"grande":130,"venti":200},  "img":"strawberry_acai",    "cat":"refresher","hot":False},
        {"key":"pink_drink",         "name":"Pink Drink",                         "cal":{"tall":140,"grande":200,"venti":290}, "img":"pink_drink",         "cat":"refresher","hot":False},
        {"key":"dragon_drink",       "name":"Dragon Drink",                       "cal":{"tall":130,"grande":190,"venti":280}, "img":"dragon_drink",       "cat":"refresher","hot":False},
        {"key":"mango_dragonfruit",  "name":"Mango Dragonfruit Refresher",        "cal":{"tall":90,"grande":130,"venti":200},  "img":"mango_dragonfruit",  "cat":"refresher","hot":False},
        {"key":"strawberry_lemonade","name":"Strawberry Acai Lemonade Refresher", "cal":{"tall":120,"grande":190,"venti":280}, "img":"strawberry_lemonade","cat":"refresher","hot":False},
    ],
}
ALL_DRINKS = {d["key"]: d for cat in MENU.values() for d in cat}

VIBE_META = {
    "sunny_social":        {"color":"#0d5c2e", "label":"Sunny Social"},
    "chill_studious":      {"color":"#1a237e", "label":"Chill Studious"},
    "rushed_professional": {"color":"#33280a", "label":"Rushed Professional"},
    "moody_intense":       {"color":"#1a0d1a", "label":"Moody Intense"},
    "cozy_comfort":        {"color":"#3e1f00", "label":"Cozy Comfort"},
    "adventurous":         {"color":"#00363a", "label":"Adventurous"},
}

# ── Feature builder ────────────────────────────────────────────────────────────
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
    df = df.reindex(columns=feature_cols, fill_value=0)
    return df

# ── Styling ────────────────────────────────────────────────────────────────────
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
.drink-card{background:#fff;border:1.5px solid #e8e8e8;border-radius:16px;padding:12px 8px;text-align:center;margin-bottom:6px}
.drink-card img{width:78px;height:78px;border-radius:50%;object-fit:cover;display:block;margin:0 auto 8px;border:2px solid #1e3932}
.drink-card-name{font-size:11px;font-weight:600;color:#1e3932;line-height:1.3}
.drink-card-cal{font-size:10px;color:#aaa;margin-top:2px}
.vibe-result{border-radius:20px;padding:26px 22px;color:#fff;margin-top:8px}
.vibe-title{font-family:'Playfair Display',serif;font-size:1.7rem;font-weight:700;font-style:italic;margin-bottom:8px}
.vibe-conf{display:inline-block;background:rgba(255,255,255,.15);border-radius:20px;padding:4px 16px;font-size:.8rem;font-weight:600;margin-bottom:12px}
.vibe-desc{font-size:.95rem;line-height:1.75;opacity:.92;font-style:italic;margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,.15)}
.llm-badge{display:inline-block;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:20px;padding:3px 12px;font-size:.7rem;color:rgba(255,255,255,.6);margin-bottom:8px}
.model-note{background:#eaf4ef;border-left:3px solid #00704a;border-radius:10px;padding:14px 18px;font-size:.82rem;color:#2d5a3d;line-height:1.6;margin-top:14px}
.stSelectbox label{font-size:.75rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:.08em!important;color:#5c7f6e!important}
.stButton>button{background:#00704a!important;color:#fff!important;border:none!important;border-radius:500px!important;padding:14px 40px!important;font-size:.9rem!important;font-weight:700!important;width:100%!important}
</style>""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <div>
    <h1>Quench Cafe · Vibe Predictor</h1>
    <p>Random Forest classifier + Llama 3.2 via Ollama · UW Center Table · Winter 2026</p>
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

    cols = st.columns(4)
    for i, drink in enumerate(drinks_in_cat):
        with cols[i % 4]:
            img_src = get(drink["img"])
            cal = drink["cal"].get("grande", 0)
            is_sel = drink["key"] == st.session_state["selected_drink"]
            if img_src:
                st.markdown(f"""
                <div class="drink-card" style="border-color:{'#00704a' if is_sel else '#e8e8e8'};{'background:#eaf4ef' if is_sel else ''}">
                  <img src="{img_src}">
                  <div class="drink-card-name">{drink['name']}</div>
                  <div class="drink-card-cal">{f'{cal} cal' if cal else ''}</div>
                </div>""", unsafe_allow_html=True)
            if st.button(f"{'Selected' if is_sel else 'Select'}", key=f"b_{drink['key']}", use_container_width=True):
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
    predict_btn = st.button("Read My Vibe", use_container_width=True)

with right:
    st.markdown("#### Vibe Reading")
    if predict_btn:
        # ── ML prediction ──────────────────────────────────────────────────────
        features  = build_features(
            st.session_state["selected_drink"], size, milk, syrup,
            extra_shot, extra_hot, cold_foam, whipped_cream, no_ice
        )
        probs     = model.predict_proba(features)[0]
        classes   = le.inverse_transform(range(len(probs)))
        prob_dict = dict(sorted(zip(classes, probs), key=lambda x: -x[1]))
        top_vibe  = list(prob_dict.keys())[0]
        top_prob  = list(prob_dict.values())[0]
        meta      = VIBE_META.get(top_vibe, {"color":"#1e3932","label":top_vibe})
        conf      = int(top_prob * 100)
        label     = meta["label"]

        # ── LLM description via Ollama ─────────────────────────────────────────
        with st.spinner("Generating your vibe description..."):
            llm_desc, llm_ok = generate_description(
                drink_info["name"], size, milk,
                syrup if syrup != "None" else "",
                extra_shot, extra_hot, cold_foam, whipped_cream,
                label, conf
            )

        # ── Display result ─────────────────────────────────────────────────────
        llm_section = ""
        if llm_ok and llm_desc:
            llm_section = f"""
          <div class="llm-badge">Generated by Llama 3.2 via Ollama</div>
          <div class="vibe-desc">{llm_desc}</div>"""

        st.markdown(f"""
        <div class="vibe-result" style="background:{meta['color']}">
          <div class="vibe-title">{label}</div>
          <div class="vibe-conf">{conf}% model confidence</div>
          {llm_section}
        </div>""", unsafe_allow_html=True)

        if not llm_ok:
            st.caption("Ollama not running — start it with `ollama serve` for AI-generated descriptions.")

        # ── Probability breakdown ──────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Full breakdown**")
        for vibe, prob in list(prob_dict.items())[:6]:
            vmeta = VIBE_META.get(vibe, {"label": vibe})
            st.markdown(f"""
            <div style="margin:8px 0">
              <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                <span>{vmeta['label']}</span>
                <span style="font-weight:700;color:#00704a">{prob*100:.0f}%</span>
              </div>
              <div style="height:6px;background:#e8f3ef;border-radius:3px;overflow:hidden">
                <div style="height:100%;width:{prob*100:.0f}%;background:#00704a;border-radius:3px"></div>
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Model note ─────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="model-note">
          <strong>ML Model:</strong> Random Forest · 300 trees · balanced class weights<br>
          <strong>Input:</strong> {drink_info['name']} · {size} · {milk} milk
          {' · extra shot' if extra_shot else ''}
          {' · extra hot' if extra_hot else ''}
          {' · cold foam' if cold_foam else ''}<br>
          <strong>LLM:</strong> Llama 3.2 (3B) running locally via Ollama · prompt includes drink details + ML prediction
        </div>""", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="background:#f7f7f7;border-radius:16px;padding:40px;text-align:center;margin-top:8px">
          <div style="font-size:1rem;font-weight:600;color:#1e3932;margin-bottom:8px">
            Select a drink and hit Read My Vibe
          </div>
          <div style="font-size:.85rem;color:#aaa;line-height:1.6">
            Random Forest predicts your personality type.<br>
            Llama 3.2 via Ollama generates a personalized description.<br><br>
            Make sure <code>ollama serve</code> is running in a separate terminal.
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""<div style="text-align:center;font-size:.8rem;color:#aaa;padding:8px 0">
  Quench Cafe · Vibe Predictor · Hariharan Sureshkumar · UW MS Data Science · Winter 2026<br>
  Random Forest · 8,083 synthetic orders · Llama 3.2 via Ollama
</div>""", unsafe_allow_html=True)
