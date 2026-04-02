"""
wrapped.py — Quench Wrapped
Your barista year in drinks. Dec 2024 – Mar 2026.
Based on real regulars and real patterns from Quench at UW.
"""

import streamlit as st
import random

# ── real regulars (based on Hari's actual memory) ──────────────────────────────
REGULARS = [
    {
        "id":        "regular_1",
        "nickname":  "The Strawberry Person",
        "emoji":     "🍓",
        "drink":     "Strawberry Açaí Refresher",
        "drink_key": "strawberry_acai",
        "detail":    "Water base. Inclusions always. Same size every time.",
        "frequency": "Almost every shift",
        "note":      "You could start making it the moment you saw them walk through the door.",
        "color":     "#e91e63",
        "bg":        "#2d0a14",
    },
    {
        "id":        "regular_2",
        "nickname":  "The London Fog Person",
        "emoji":     "🫖",
        "drink":     "London Fog Latte",
        "drink_key": "london_fog_latte",
        "detail":    "Earl Grey + vanilla + steamed whole milk.",
        "frequency": "Weekly, like clockwork",
        "note":      "The kind of person who knows exactly what they want and has known for years.",
        "color":     "#c8b890",
        "bg":        "#0d0a04",
    },
    {
        "id":        "regular_3",
        "nickname":  "The Hot Chocolate Person",
        "emoji":     "🍫",
        "drink":     "Hot Chocolate with Whipped Cream",
        "drink_key": "hot_chocolate",
        "detail":    "Chocolate pumps, steamed milk, always with whip.",
        "frequency": "Snow days especially",
        "note":      "Never skips the whipped cream. You stopped asking.",
        "color":     "#c8906a",
        "bg":        "#0a0400",
    },
    {
        "id":        "regular_4",
        "nickname":  "The Half-Pump Person",
        "emoji":     "🤎",
        "drink":     "Brown Sugar Shaken Espresso",
        "drink_key": "brown_sugar_shaken_espresso",
        "detail":    "Half pump of brown sugar only. Precise.",
        "frequency": "Regular",
        "note":      "Half pump. Not one pump, not none. Half. They knew what they wanted down to the decimal.",
        "color":     "#c8a050",
        "bg":        "#0d0600",
    },
]

# ── wrapped stats (Dec 2024 – Mar 2026) ────────────────────────────────────────
WRAPPED_STATS = {
    "period":          "December 2024 – March 2026",
    "shifts":          "2 shifts/week · Mondays & Fridays · 3:45–7:30 PM",
    "total_shifts":    68,
    "drinks_made":     "1,700–2,400",   # 25–35 per shift × 68
    "top_drink":       "Matcha Latte",
    "top_category":    "Lattes",
    "peak_hour":       "5:00–6:00 PM",
    "busiest_day":     "Finals week, March 2026",
    "snow_days":       2,               # mid-march seattle snow
    "soft_serve_days": "Thursdays mostly",

    "fun_facts": [
        "You made roughly 400–600 matcha lattes over your time at Quench.",
        "Snow hit Seattle in mid-March 2026. Hot chocolate orders tripled.",
        "Finals week was your busiest stretch — 40%+ more orders than a normal week.",
        "The afternoon rush hit hardest between 5 and 6 PM, right in the middle of your shift.",
        "Oat milk was requested more than whole milk on your shifts — the UW crowd.",
        "You learned to read the room. Headphones in = cold brew, no eye contact = americano.",
    ],

    "vibe_breakdown": {
        "☀️ Sunny Social":        28,
        "📚 Chill Studious":      25,
        "💼 Rushed Professional": 20,
        "🖤 Moody Intense":       15,
        "🧸 Cozy Comfort":        8,
        "🌀 Adventurous":         4,
    },

    "seasonal": [
        {"season": "Winter 2024–25", "top": "Hot Chocolate", "mood": "Warm, slow, getting started"},
        {"season": "Spring 2025",    "top": "Strawberry Açaí", "mood": "Rush of refreshers as sun came back"},
        {"season": "Summer 2025",    "top": "Cold Brew",    "mood": "Iced everything, always"},
        {"season": "Autumn 2025",    "top": "Chai Latte",   "mood": "Pumpkin spice requests returned"},
        {"season": "Winter 2025–26", "top": "Matcha Latte", "mood": "Your most confident season"},
    ],
}


def render_wrapped() -> None:
    """Render the full Quench Wrapped section in Streamlit."""

    # ── hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#1e3932;border-radius:24px;padding:48px 40px 40px;
                margin-bottom:32px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-30px;right:-30px;width:200px;height:200px;
                  background:radial-gradient(circle,rgba(0,112,74,0.3) 0%,transparent 70%);
                  border-radius:50%;"></div>
      <div style="font-size:0.7rem;color:#5c7f6e;text-transform:uppercase;
                  letter-spacing:0.18em;font-weight:700;margin-bottom:12px;">
        🌿 QUENCH WRAPPED
      </div>
      <div style="font-family:'Playfair Display',serif;font-size:2.8rem;color:#fff;
                  font-weight:700;line-height:1.05;margin-bottom:12px;">
        Your year<br><em style="color:#8fae9e;">in coffee.</em>
      </div>
      <div style="font-size:0.92rem;color:#8fae9e;line-height:1.7;max-width:480px;">
        December 2024 to March 2026. Two shifts a week. Mondays and Fridays.
        Every matcha, every americano, every half-pump brown sugar shaken espresso.
        Here's what your time at Quench looked like.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── the numbers ────────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.3rem;color:#1e3932;font-weight:700;margin-bottom:16px;">The Numbers</div>', unsafe_allow_html=True)

    n1, n2, n3, n4 = st.columns(4)
    def big_stat(val, label, sub=""):
        return f"""<div style="background:#fff;border-radius:16px;padding:24px 20px;
                      text-align:center;border-top:3px solid #00704a;
                      box-shadow:0 1px 8px rgba(0,0,0,0.05);">
          <div style="font-family:'Playfair Display',serif;font-size:2.4rem;
                      color:#1e3932;font-weight:700;line-height:1;">{val}</div>
          <div style="font-size:0.7rem;color:#8fae9e;text-transform:uppercase;
                      letter-spacing:0.1em;font-weight:700;margin-top:6px;">{label}</div>
          <div style="font-size:0.78rem;color:#aabfb5;margin-top:3px;">{sub}</div>
        </div>"""

    with n1: st.markdown(big_stat("68", "Shifts", "Mon & Fri"), unsafe_allow_html=True)
    with n2: st.markdown(big_stat("~2K", "Drinks Made", "est. 25–35/shift"), unsafe_allow_html=True)
    with n3: st.markdown(big_stat("15+", "Months", "Dec '24 – Mar '26"), unsafe_allow_html=True)
    with n4: st.markdown(big_stat("4", "Regulars", "you could spot instantly"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── your regulars ──────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.3rem;color:#1e3932;font-weight:700;margin-bottom:6px;">Your Regulars</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.88rem;color:#8fae9e;margin-bottom:20px;">The ones you recognized before they reached the counter.</div>', unsafe_allow_html=True)

    for reg in REGULARS:
        col_a, col_b = st.columns([1, 3], gap="large")
        with col_a:
            from drink_cards import get_card_html
            card_html = get_card_html(reg["drink_key"])
            st.markdown(f'<div style="display:flex;justify-content:center;">{card_html}</div>',
                        unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div style="background:#fff;border-radius:20px;padding:28px 32px;
                        height:100%;box-shadow:0 1px 8px rgba(0,0,0,0.05);
                        border-left:5px solid {reg['color']};">
              <div style="font-size:1.8rem;margin-bottom:8px;">{reg['emoji']}</div>
              <div style="font-family:'Playfair Display',serif;font-size:1.4rem;
                          color:#1e3932;font-weight:700;margin-bottom:4px;">
                {reg['nickname']}
              </div>
              <div style="font-size:0.88rem;color:#00704a;font-weight:600;margin-bottom:8px;">
                {reg['drink']}
              </div>
              <div style="font-size:0.82rem;color:#8fae9e;margin-bottom:6px;">
                {reg['detail']}
              </div>
              <div style="font-size:0.82rem;color:#5c7f6e;font-weight:600;margin-bottom:10px;">
                {reg['frequency']}
              </div>
              <div style="font-size:0.9rem;color:#3d5a4c;font-style:italic;
                          line-height:1.6;border-top:1px solid #e8f3ef;padding-top:12px;">
                "{reg['note']}"
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── your most made drink ───────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.3rem;color:#1e3932;font-weight:700;margin:8px 0 20px;">Your Most Made Drink</div>', unsafe_allow_html=True)

    mc1, mc2 = st.columns([1, 2], gap="large")
    with mc1:
        from drink_cards import get_card_html
        st.markdown(f'<div style="display:flex;justify-content:center;">{get_card_html("matcha_latte", cold_foam=True, iced=True)}</div>',
                    unsafe_allow_html=True)
    with mc2:
        st.markdown("""
        <div style="background:#1e3932;border-radius:20px;padding:32px 36px;color:#fff;">
          <div style="font-size:0.7rem;color:#5c7f6e;text-transform:uppercase;
                      letter-spacing:0.14em;font-weight:700;margin-bottom:8px;">#1 ALL TIME</div>
          <div style="font-family:'Playfair Display',serif;font-size:2rem;
                      font-weight:700;margin-bottom:8px;">Matcha Latte</div>
          <div style="font-size:0.88rem;color:#8fae9e;line-height:1.7;margin-bottom:16px;">
            Vanilla syrup · Oat milk · Matcha powder · Shaken with ice ·
            Vanilla sweet cream cold foam on top.
          </div>
          <div style="font-size:0.85rem;color:#5c7f6e;line-height:1.7;">
            You made somewhere between 400 and 600 of these.
            The shaker, the pour, the foam — you had it down to muscle memory.
            Probably your most requested drink on Friday afternoons.
          </div>
          <div style="margin-top:20px;padding-top:16px;border-top:1px solid #2d5a3d;">
            <span style="background:#00704a;color:#fff;border-radius:500px;
                         padding:5px 16px;font-size:0.78rem;font-weight:700;">
              Est. 400–600 made
            </span>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── seasonal journey ───────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.3rem;color:#1e3932;font-weight:700;margin-bottom:20px;">Season by Season</div>', unsafe_allow_html=True)

    season_cols = st.columns(5)
    season_colors = ["#1e3932","#2d5a3d","#1a3d2d","#2a4a1e","#1e3932"]
    season_drink_keys = ["hot_chocolate","strawberry_acai","cold_brew","chai_latte","matcha_latte"]

    for i, (col, season) in enumerate(zip(season_cols, WRAPPED_STATS["seasonal"])):
        with col:
            from drink_cards import get_card_html
            card = get_card_html(season_drink_keys[i])
            st.markdown(f"""
            <div style="background:{season_colors[i]};border-radius:16px;
                        padding:16px 12px 20px;text-align:center;">
              <div style="display:flex;justify-content:center;margin-bottom:10px;">
                {card.replace('width:160px', 'width:120px')}
              </div>
              <div style="font-size:0.68rem;color:#5c7f6e;text-transform:uppercase;
                          letter-spacing:0.1em;font-weight:700;margin-bottom:4px;">
                {season['season']}
              </div>
              <div style="font-size:0.82rem;color:#a8d5b5;font-weight:600;margin-bottom:6px;">
                {season['top']}
              </div>
              <div style="font-size:0.75rem;color:#5c7f6e;font-style:italic;line-height:1.4;">
                {season['mood']}
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── vibe breakdown ─────────────────────────────────────────────────────────
    st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.3rem;color:#1e3932;font-weight:700;margin-bottom:16px;">The Vibes You Served</div>', unsafe_allow_html=True)

    vb1, vb2 = st.columns([1, 1], gap="large")
    with vb1:
        st.markdown("""
        <div style="background:#fff;border-radius:20px;padding:28px 32px;
                    box-shadow:0 1px 8px rgba(0,0,0,0.05);">
          <div style="font-size:0.8rem;color:#8fae9e;line-height:1.7;margin-bottom:16px;">
            Based on drink orders and customization patterns across your shifts.
            The Vibe Index model's best read of who was walking through that door.
          </div>""", unsafe_allow_html=True)

        for vibe, pct in WRAPPED_STATS["vibe_breakdown"].items():
            st.markdown(f"""
          <div style="margin:10px 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
              <span style="font-size:0.83rem;color:#1e3932;font-weight:500;">{vibe}</span>
              <span style="font-size:0.83rem;color:#00704a;font-weight:700;">{pct}%</span>
            </div>
            <div style="height:6px;background:#e8f3ef;border-radius:3px;overflow:hidden;">
              <div style="height:100%;width:{pct}%;background:linear-gradient(90deg,#00704a,#1abc7e);border-radius:3px;"></div>
            </div>
          </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with vb2:
        st.markdown("""
        <div style="background:#fff;border-radius:20px;padding:28px 32px;
                    box-shadow:0 1px 8px rgba(0,0,0,0.05);">
          <div style="font-size:0.72rem;color:#8fae9e;text-transform:uppercase;
                      letter-spacing:0.1em;font-weight:700;margin-bottom:16px;">
            Things You Learned
          </div>""", unsafe_allow_html=True)

        for fact in WRAPPED_STATS["fun_facts"]:
            st.markdown(f"""
          <div style="display:flex;gap:12px;margin:12px 0;align-items:flex-start;">
            <div style="width:6px;height:6px;background:#00704a;border-radius:50%;
                        flex-shrink:0;margin-top:7px;"></div>
            <div style="font-size:0.86rem;color:#3d5a4c;line-height:1.6;">{fact}</div>
          </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── closing card ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:#1e3932;border-radius:24px;padding:40px;text-align:center;">
      <div style="font-size:2rem;margin-bottom:16px;">🌿</div>
      <div style="font-family:'Playfair Display',serif;font-size:1.6rem;color:#fff;
                  font-weight:700;margin-bottom:12px;">
        Thanks for the shifts, Hari.
      </div>
      <div style="font-size:0.92rem;color:#8fae9e;line-height:1.8;max-width:480px;margin:0 auto;">
        Every matcha shaken right. Every half-pump measured exactly.
        Every hot chocolate with whip because you already knew.
        Quench was better for it.
      </div>
    </div>
    """, unsafe_allow_html=True)