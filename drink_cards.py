"""
drink_cards.py
SVG drink card illustrations for Quench Café.
Each card shows the drink's actual layers, inclusions, foam, ice.

Streamlit strips inline SVG from st.markdown even with unsafe_allow_html=True.
Fix: base64-encode the SVG and embed as <img src="data:image/svg+xml;base64,...">
which Streamlit allows through.
"""

import base64

def _svg_to_img(svg_content: str, width: int = 120, height: int = 170) -> str:
    """Wrap SVG content in a full SVG tag and return as base64 img tag."""
    full_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{svg_content}</svg>'
    encoded  = base64.b64encode(full_svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{encoded}" width="{width}" height="{height}" style="display:block;margin:0 auto 12px;">'

# ── card shell ────────────────────────────────────────────────────────────────
def _card(svg_content: str, label: str, sublabel: str,
          bg: str = "#1e3932", label_color: str = "#a8d5b5",
          sub_color: str = "#5d9970", height: int = 240) -> str:
    img_tag = _svg_to_img(svg_content)
    return f"""
<div style="background:{bg};border-radius:20px;padding:20px 16px 16px;
            text-align:center;width:160px;flex-shrink:0;
            box-shadow:0 4px 24px rgba(0,0,0,0.18);">
  {img_tag}
  <div style="font-family:Georgia,serif;font-size:11px;font-weight:700;
              color:{label_color};letter-spacing:0.08em;line-height:1.3;">
    {label}
  </div>
  <div style="font-size:10px;color:{sub_color};margin-top:3px;
              font-family:Georgia,serif;letter-spacing:0.06em;">
    {sublabel}
  </div>
</div>"""

# ── individual drink SVGs ──────────────────────────────────────────────────────

def _straw(x=88, y1=10, y2=120, color="#5d9970"):
    return f'<rect x="{x}" y="{y1}" width="5" height="{y2-y1}" rx="2.5" fill="{color}" opacity="0.9"/>'

def _ice(*positions, color="rgba(255,255,255,0.28)"):
    out = []
    for (x,y,w,h) in positions:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{color}"/>')
    return "".join(out)

def matcha_latte(cold_foam=True, iced=True):
    svg = """
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#2d5a3d"/>
    <rect x="10" y="70" width="100" height="95" rx="0" fill="#4a7c59"/>
    <rect x="10" y="35" width="100" height="50" fill="#c8e6c9"/>
    """ + _ice((18,75,14,10),(40,83,12,9),(65,77,15,10),(85,82,11,8)) + """
    <ellipse cx="60" cy="37" rx="52" ry="12" fill="#e8f5e9"/>
    <ellipse cx="60" cy="35" rx="46" ry="8" fill="#f1f8f1"/>
    """ + _straw(88, 8, 115, "#5d9970")
    return _card(svg, "MATCHA", "LATTE", "#1e3932", "#a8d5b5", "#5d9970")

def strawberry_acai(liquid="water"):
    liquid_color = "#e91e63" if liquid == "water" else \
                   "#e91e63" if liquid == "lemonade" else "#f48fb1"
    top_color    = "#f48fb1" if liquid != "coconut milk" else "#fce4ec"
    svg = f"""
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#4a1a2a"/>
    <rect x="10" y="55" width="100" height="110" fill="{liquid_color}" opacity="0.7"/>
    <rect x="10" y="35" width="100" height="35" fill="{top_color}" opacity="0.8"/>
    <circle cx="28" cy="105" r="5" fill="#c2185b" opacity="0.9"/>
    <circle cx="44" cy="118" r="4" fill="#ad1457" opacity="0.8"/>
    <circle cx="62" cy="100" r="6" fill="#c2185b" opacity="0.85"/>
    <circle cx="79" cy="115" r="4" fill="#880e4f" opacity="0.9"/>
    <circle cx="95" cy="104" r="5" fill="#c2185b" opacity="0.8"/>
    <circle cx="36" cy="132" r="4" fill="#ad1457" opacity="0.75"/>
    <circle cx="74" cy="130" r="5" fill="#c2185b" opacity="0.85"/>
    """ + _ice((16,62,16,11),(40,68,14,10),(78,64,13,9)) + """
    <ellipse cx="60" cy="37" rx="52" ry="10" fill="#fce4ec"/>
    <ellipse cx="60" cy="35" rx="46" ry="7" fill="#fce4ec"/>
    """ + _straw(87, 5, 120, "#e91e63")
    return _card(svg, "STRAWBERRY AÇAÍ", "REFRESHER", "#2d0a14", "#f48fb1", "#ad5070")

def dragonfruit_refresher(liquid="water"):
    base = "#7b1fa2" if liquid == "water" else "#9c27b0"
    svg = f"""
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#3a0a4a"/>
    <rect x="10" y="55" width="100" height="110" fill="{base}" opacity="0.65"/>
    <rect x="10" y="35" width="100" height="35" fill="#ce93d8" opacity="0.8"/>
    <rect x="22" y="98" width="12" height="15" rx="2" fill="#e040fb" opacity="0.5"/>
    <rect x="45" y="108" width="14" height="12" rx="2" fill="#ce93d8" opacity="0.6"/>
    <rect x="70" y="100" width="11" height="14" rx="2" fill="#e040fb" opacity="0.5"/>
    <rect x="88" y="112" width="10" height="11" rx="2" fill="#ce93d8" opacity="0.45"/>
    <circle cx="35" cy="125" r="4" fill="#e040fb" opacity="0.5"/>
    <circle cx="75" cy="128" r="4" fill="#ab47bc" opacity="0.55"/>
    """ + _ice((15,62,15,10),(50,68,13,9),(82,64,12,9)) + """
    <ellipse cx="60" cy="37" rx="52" ry="10" fill="#f3e5f5"/>
    <ellipse cx="60" cy="35" rx="46" ry="7" fill="#fce4ec"/>
    """ + _straw(87, 5, 120, "#ab47bc")
    return _card(svg, "MANGO DRAGONFRUIT", "REFRESHER", "#1a0028", "#ce93d8", "#7b4a90")

def latte(iced=True, syrup="none", milk="oat", cold_foam=False):
    milk_color = "#f5e6c8" if milk == "whole" else \
                 "#e8d5a8" if milk == "oat" else "#f0e8d8"
    espresso = "#2c1400"
    svg = f"""
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#3d2010"/>
    <rect x="10" y="90" width="100" height="75" fill="{espresso}"/>
    <rect x="10" y="50" width="100" height="50" fill="{milk_color}" opacity="0.85"/>
    """ + (_ice((15,60,16,11),(42,67,13,9),(68,62,15,10),(88,68,11,8)) if iced else "") + f"""
    <ellipse cx="60" cy="37" rx="52" ry="11" fill="{'#f8f4ee' if cold_foam else milk_color}"/>
    <ellipse cx="60" cy="35" rx="45" ry="7" fill="{'#ffffff' if cold_foam else milk_color}"/>
    """ + _straw(88, 5, 118, "#c8a050")
    return _card(svg, "LATTE", "ICED" if iced else "HOT", "#1e1008", "#d4a870", "#7a5a30")

def chai_latte(iced=False):
    svg = f"""
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#4a2810"/>
    <rect x="10" y="80" width="100" height="85" fill="#8b4513" opacity="0.8"/>
    <rect x="10" y="35" width="100" height="55" fill="#d4956a" opacity="0.7"/>
    """ + (_ice((15,55,15,10),(42,62,13,9),(70,57,14,9)) if iced else "") + """
    <ellipse cx="60" cy="37" rx="52" ry="11" fill="#e8c9a0"/>
    <ellipse cx="60" cy="35" rx="45" ry="7" fill="#f0d8b8"/>
    <circle cx="35" cy="43" r="2" fill="#8b4513" opacity="0.5"/>
    <circle cx="50" cy="40" r="1.5" fill="#8b4513" opacity="0.4"/>
    <circle cx="75" cy="42" r="2" fill="#8b4513" opacity="0.5"/>
    """ + _straw(87, 5, 118, "#8b4513")
    return _card(svg, "CHAI", "LATTE", "#1a0a04", "#d4956a", "#7a4828")

def london_fog():
    svg = """
    <rect x="18" y="50" width="84" height="110" rx="10" fill="#3d3020"/>
    <path d="M102 70 Q118 70 118 95 Q118 120 102 120" fill="none"
          stroke="#4d4030" stroke-width="7" stroke-linecap="round"/>
    <rect x="18" y="80" width="84" height="80" fill="#6b5a3d" opacity="0.7"/>
    <rect x="18" y="50" width="84" height="40" fill="#e8d5b0" opacity="0.6"/>
    <ellipse cx="60" cy="52" rx="44" ry="11" fill="#f0e8d0"/>
    <ellipse cx="60" cy="50" rx="38" ry="8" fill="#f8f4ee"/>
    <path d="M30 35 Q33 24 30 15" fill="none" stroke="#c8b890" stroke-width="1.5"
          stroke-linecap="round" opacity="0.5"/>
    <path d="M60 33 Q63 20 60 10" fill="none" stroke="#c8b890" stroke-width="1.5"
          stroke-linecap="round" opacity="0.4"/>
    <path d="M88 35 Q91 23 88 14" fill="none" stroke="#c8b890" stroke-width="1.5"
          stroke-linecap="round" opacity="0.5"/>
    """
    return _card(svg, "LONDON FOG", "LATTE", "#0d0a04", "#d4c8a0", "#7a6848")

def caramel_macchiato(iced=True):
    svg = f"""
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#3d2800"/>
    <rect x="10" y="80" width="100" height="85" fill="#f5e6c8" opacity="0.85"/>
    <rect x="10" y="35" width="100" height="55" fill="#1a0a00" opacity="0.9"/>
    """ + _ice((15,88,15,10),(42,95,13,9),(68,90,15,10),(88,96,11,8)) + """
    <ellipse cx="60" cy="37" rx="52" ry="11" fill="#f5e6c8"/>
    <path d="M25 40 Q40 33 55 40 Q70 47 85 40 Q95 35 105 40"
          fill="none" stroke="#8b4513" stroke-width="1.5" opacity="0.8"/>
    <path d="M15 45 Q30 38 50 44 Q65 50 80 44 Q95 38 110 45"
          fill="none" stroke="#c8860a" stroke-width="1.2" opacity="0.7"/>
    """ + _straw(88, 5, 118, "#c8860a")
    return _card(svg, "CARAMEL", "MACCHIATO", "#1a0f00", "#d4a850", "#7a5820")

def americano(iced=False):
    svg = f"""
    <rect x="18" y="50" width="84" height="110" rx="10" fill="#1a0a00"/>
    {'<path d="M102 70 Q118 70 118 95 Q118 120 102 120" fill="none" stroke="#2d1800" stroke-width="7" stroke-linecap="round"/>' if not iced else ''}
    <rect x="18" y="{'90' if iced else '80'}" width="84" height="70" fill="#0d0500" opacity="0.9"/>
    <rect x="18" y="50" width="84" height="{'48' if iced else '35'}" fill="{'#8B7355' if not iced else 'rgba(255,255,255,0.15'}" opacity="0.4"/>
    """ + (_ice((24,60,16,11),(48,68,13,9),(74,62,14,9)) if iced else "") + f"""
    <ellipse cx="60" cy="52" rx="44" ry="9" fill="#3d2000" opacity="0.8"/>
    <ellipse cx="60" cy="50" rx="38" ry="6" fill="#5d3810" opacity="0.6"/>
    """ + (_straw(87, 5, 118, "#4d3018") if iced else "")
    label = "ICED AMERICANO" if iced else "AMERICANO"
    return _card(svg, label, "ESPRESSO", "#0d0500", "#8B7355", "#4d3018")

def mocha(iced=False, whip=True):
    svg = f"""
    <rect x="{'10' if iced else '18'}" y="{'35' if iced else '50'}" width="{'100' if iced else '84'}" height="{'130' if iced else '110'}" rx="{'8' if iced else '10'}" fill="#1a0800"/>
    {'<path d="M102 70 Q118 70 118 95 Q118 120 102 120" fill="none" stroke="#2d1200" stroke-width="7" stroke-linecap="round"/>' if not iced else ''}
    <rect x="{'10' if iced else '18'}" y="{'90' if iced else '85'}" width="{'100' if iced else '84'}" height="{'75' if iced else '75'}" fill="#2d0f00" opacity="0.9"/>
    <rect x="{'10' if iced else '18'}" y="{'35' if iced else '50'}" width="{'100' if iced else '84'}" height="{'62' if iced else '42'}" fill="#5d2800" opacity="0.7"/>
    """ + (_ice((15,62,15,10),(42,70,13,9),(68,64,14,9)) if iced else "") + """
    <ellipse cx="60" cy="37" rx="52" ry="13" fill="#f8f4ee"/>
    <ellipse cx="60" cy="35" rx="44" ry="9" fill="#fff"/>
    <ellipse cx="48" cy="32" rx="20" ry="7" fill="#fff"/>
    <ellipse cx="72" cy="33" rx="18" ry="6" fill="#fefefe"/>
    <path d="M25 38 Q38 30 50 38 Q62 46 75 38 Q85 32 95 38"
          fill="none" stroke="#3d1800" stroke-width="1.5" opacity="0.7"/>
    """
    return _card(svg, "MOCHA", "ICED" if iced else "HOT", "#0d0400", "#c8906a", "#7a4820")

def brown_sugar_espresso():
    svg = """
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#2d1400"/>
    <rect x="10" y="105" width="100" height="60" fill="#0d0500" opacity="0.95"/>
    <rect x="10" y="55" width="100" height="58" fill="#c8a050" opacity="0.75"/>
    <rect x="10" y="35" width="100" height="30" fill="#d4a855" opacity="0.55"/>
    """ + _ice((15,112,18,13),(40,120,15,11),(65,114,17,12),(88,121,13,10)) + """
    <circle cx="28" cy="45" r="2" fill="#5d2800" opacity="0.6"/>
    <circle cx="45" cy="42" r="1.5" fill="#5d2800" opacity="0.5"/>
    <circle cx="62" cy="44" r="2" fill="#5d2800" opacity="0.6"/>
    <circle cx="78" cy="41" r="1.5" fill="#5d2800" opacity="0.5"/>
    <circle cx="92" cy="43" r="2" fill="#5d2800" opacity="0.55"/>
    """ + _straw(87, 5, 118, "#c8a050")
    return _card(svg, "BROWN SUGAR", "SHAKEN ESPRESSO", "#0d0600", "#c8a050", "#7a5820")

def hot_chocolate(whip=True):
    svg = """
    <rect x="18" y="50" width="84" height="110" rx="10" fill="#1a0800"/>
    <path d="M102 70 Q120 70 120 95 Q120 120 102 120" fill="none"
          stroke="#2d1200" stroke-width="8" stroke-linecap="round"/>
    <rect x="18" y="88" width="84" height="72" fill="#3d1200" opacity="0.9"/>
    <rect x="18" y="50" width="84" height="48" fill="#f8f4ee"/>
    <ellipse cx="60" cy="52" rx="44" ry="14" fill="#f5f0e8"/>
    <ellipse cx="60" cy="48" rx="38" ry="10" fill="#fff"/>
    <ellipse cx="46" cy="44" rx="22" ry="8" fill="#fff"/>
    <ellipse cx="74" cy="45" rx="19" ry="7" fill="#fefefe"/>
    <path d="M22 55 Q35 46 48 55 Q60 64 72 55 Q84 46 96 55"
          fill="none" stroke="#4d1a00" stroke-width="1.5" opacity="0.65"/>
    <path d="M30 33 Q33 22 30 12" fill="none" stroke="#c8b090"
          stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
    <path d="M60 31 Q63 18 60 8" fill="none" stroke="#c8b090"
          stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
    <path d="M88 33 Q91 21 88 11" fill="none" stroke="#c8b090"
          stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
    """
    return _card(svg, "HOT", "CHOCOLATE", "#0a0400", "#c8906a", "#7a4820")

def peppermint_mocha():
    svg = """
    <rect x="18" y="50" width="84" height="110" rx="10" fill="#0d1a0d"/>
    <path d="M102 70 Q118 70 118 95 Q118 120 102 120" fill="none"
          stroke="#1a2d1a" stroke-width="7" stroke-linecap="round"/>
    <rect x="18" y="88" width="84" height="72" fill="#1a0800" opacity="0.95"/>
    <rect x="18" y="50" width="84" height="48" fill="#f8f4ee"/>
    <ellipse cx="60" cy="52" rx="44" ry="14" fill="#f5f0e8"/>
    <ellipse cx="60" cy="48" rx="38" ry="10" fill="#fff"/>
    <ellipse cx="46" cy="44" rx="22" ry="8" fill="#fff"/>
    <path d="M25 56 Q38 48 50 56 Q62 64 74 56 Q86 48 96 56"
          fill="none" stroke="#1a0800" stroke-width="1.5" opacity="0.6"/>
    <circle cx="38" cy="46" r="3" fill="#e91e63" opacity="0.7"/>
    <circle cx="55" cy="42" r="2.5" fill="#f44336" opacity="0.65"/>
    <circle cx="72" cy="44" r="3" fill="#e91e63" opacity="0.7"/>
    <circle cx="86" cy="42" r="2" fill="#f44336" opacity="0.6"/>
    <path d="M30 30 Q33 19 30 10" fill="none" stroke="#a0c8a0"
          stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
    <path d="M60 28 Q63 16 60 6" fill="none" stroke="#a0c8a0"
          stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
    """
    return _card(svg, "PEPPERMINT", "MOCHA", "#04100a", "#a8d5a8", "#4a7a4a")

def flat_white():
    svg = """
    <rect x="18" y="55" width="84" height="105" rx="10" fill="#2d1800"/>
    <path d="M102 73 Q116 73 116 95 Q116 118 102 118" fill="none"
          stroke="#3d2800" stroke-width="7" stroke-linecap="round"/>
    <rect x="18" y="80" width="84" height="80" fill="#1a0a00" opacity="0.9"/>
    <rect x="18" y="55" width="84" height="35" fill="#d4a870" opacity="0.6"/>
    <ellipse cx="60" cy="57" rx="44" ry="10" fill="#e8c8a0"/>
    <ellipse cx="60" cy="55" rx="38" ry="7" fill="#f0d8b8"/>
    <circle cx="60" cy="60" r="15" fill="none" stroke="#c8906a"
            stroke-width="1" opacity="0.5"/>
    <circle cx="60" cy="60" r="8" fill="none" stroke="#c8906a"
            stroke-width="0.8" opacity="0.4"/>
    """
    return _card(svg, "FLAT", "WHITE", "#0d0600", "#d4a870", "#7a5830")

def cold_brew(foam=False):
    svg = """
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#150800"/>
    <rect x="10" y="55" width="100" height="110" fill="#0d0500" opacity="0.95"/>
    """ + _ice((15,62,18,13),(42,70,15,11),(68,64,17,12),(88,72,12,10)) + f"""
    <rect x="10" y="35" width="100" height="28" fill="{'#f8f4ee' if foam else '#2d1400'}" opacity="{'1' if foam else '0.5'}"/>
    <ellipse cx="60" cy="37" rx="52" ry="10" fill="{'#f5f0e8' if foam else '#3d1800'}" opacity="0.9"/>
    """ + _straw(88, 5, 118, "#3d1800")
    return _card(svg, "COLD BREW", "COFFEE", "#080300", "#8B7050", "#4d3818")

def drip_coffee():
    svg = """
    <rect x="18" y="50" width="84" height="110" rx="10" fill="#1a0800"/>
    <path d="M102 68 Q118 68 118 93 Q118 118 102 118" fill="none"
          stroke="#2d1400" stroke-width="7" stroke-linecap="round"/>
    <rect x="18" y="70" width="84" height="90" fill="#0d0500" opacity="0.95"/>
    <rect x="18" y="50" width="84" height="28" fill="#3d2000" opacity="0.7"/>
    <ellipse cx="60" cy="52" rx="44" ry="9" fill="#4d2800" opacity="0.8"/>
    <path d="M30 32 Q33 22 30 14" fill="none" stroke="#b09070"
          stroke-width="1.5" stroke-linecap="round" opacity="0.45"/>
    <path d="M60 30 Q63 19 60 10" fill="none" stroke="#b09070"
          stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
    <path d="M88 32 Q91 21 88 13" fill="none" stroke="#b09070"
          stroke-width="1.5" stroke-linecap="round" opacity="0.45"/>
    """
    return _card(svg, "DRIP", "COFFEE", "#080400", "#a08060", "#5a3820")

def english_breakfast():
    svg = """
    <rect x="18" y="55" width="84" height="105" rx="10" fill="#2d1808"/>
    <path d="M102 73 Q116 73 116 95 Q116 118 102 118" fill="none"
          stroke="#3d2818" stroke-width="7" stroke-linecap="round"/>
    <rect x="18" y="78" width="84" height="82" fill="#8b4513" opacity="0.75"/>
    <rect x="18" y="55" width="84" height="32" fill="#d4826a" opacity="0.5"/>
    <ellipse cx="60" cy="57" rx="44" ry="10" fill="#c87850" opacity="0.7"/>
    <path d="M28 32 Q31 22 28 14" fill="none" stroke="#c8a080"
          stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
    <path d="M60 30 Q63 20 60 12" fill="none" stroke="#c8a080"
          stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
    <path d="M90 32 Q93 21 90 13" fill="none" stroke="#c8a080"
          stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
    """
    return _card(svg, "ENGLISH BREAKFAST", "TEA", "#100804", "#d4a880", "#7a5840")

def peach_green_tea():
    svg = """
    <rect x="10" y="35" width="100" height="130" rx="8" fill="#1a2810"/>
    <rect x="10" y="60" width="100" height="105" fill="#4a8a30" opacity="0.6"/>
    <rect x="10" y="35" width="100" height="35" fill="#f4a460" opacity="0.6"/>
    <circle cx="32" cy="100" r="6" fill="#ffa07a" opacity="0.7"/>
    <circle cx="58" cy="115" r="5" fill="#ff8c69" opacity="0.65"/>
    <circle cx="80" cy="98" r="6" fill="#ffa07a" opacity="0.7"/>
    <circle cx="45" cy="130" r="4" fill="#ff8c69" opacity="0.6"/>
    """ + _ice((15,65,15,10),(42,72,12,9),(70,66,14,9),(88,73,11,8)) + """
    <ellipse cx="60" cy="37" rx="52" ry="10" fill="#fce4c0"/>
    <ellipse cx="60" cy="35" rx="46" ry="7" fill="#fdebd0"/>
    """ + _straw(88, 5, 118, "#4a8a30")
    return _card(svg, "PEACH GREEN", "TEA", "#0a1208", "#a8d080", "#4a7830")


def get_card_html(drink_key: str, **kwargs) -> str:
    """Return the card HTML for a given drink key."""
    mapping = {
        "matcha_latte":              lambda: matcha_latte(**{k:v for k,v in kwargs.items() if k in ["cold_foam","iced"]}),
        "strawberry_acai":           lambda: strawberry_acai(**{k:v for k,v in kwargs.items() if k in ["liquid"]}),
        "dragonfruit":               lambda: dragonfruit_refresher(**{k:v for k,v in kwargs.items() if k in ["liquid"]}),
        "pineapple_passionfruit":    lambda: dragonfruit_refresher(),
        "latte":                     lambda: latte(**{k:v for k,v in kwargs.items() if k in ["iced","syrup","milk","cold_foam"]}),
        "chai_latte":                lambda: chai_latte(**{k:v for k,v in kwargs.items() if k in ["iced"]}),
        "london_fog_latte":          lambda: london_fog(),
        "caramel_macchiato":         lambda: caramel_macchiato(**{k:v for k,v in kwargs.items() if k in ["iced"]}),
        "americano":                 lambda: americano(**{k:v for k,v in kwargs.items() if k in ["iced"]}),
        "mocha":                     lambda: mocha(**{k:v for k,v in kwargs.items() if k in ["iced","whip"]}),
        "white_chocolate_mocha":     lambda: mocha(iced=kwargs.get("iced",False)),
        "peppermint_mocha":          lambda: peppermint_mocha(),
        "brown_sugar_shaken_espresso": lambda: brown_sugar_espresso(),
        "flat_white":                lambda: flat_white(),
        "hot_chocolate":             lambda: hot_chocolate(),
        "white_hot_chocolate":       lambda: hot_chocolate(),
        "caramel_apple_spice":       lambda: hot_chocolate(),
        "cold_brew":                 lambda: cold_brew(**{k:v for k,v in kwargs.items() if k in ["foam"]}),
        "drip_coffee":               lambda: drip_coffee(),
        "iced_coffee":               lambda: cold_brew(),
        "english_breakfast_tea":     lambda: english_breakfast(),
        "earl_grey_tea":             lambda: english_breakfast(),
        "chamomile_tea":             lambda: english_breakfast(),
        "peach_green_tea":           lambda: peach_green_tea(),
        "passion_tango_tea":         lambda: peach_green_tea(),
    }
    fn = mapping.get(drink_key)
    return fn() if fn else ""


def drink_row(drink_keys: list, kwargs_list: list = None) -> str:
    """Render a horizontal scrollable row of drink cards."""
    cards = []
    for i, key in enumerate(drink_keys):
        kw = (kwargs_list[i] if kwargs_list and i < len(kwargs_list) else {}) or {}
        cards.append(get_card_html(key, **kw))
    inner = "".join(cards)
    return f"""
<div style="display:flex;gap:16px;overflow-x:auto;padding:8px 4px 16px;
            scrollbar-width:thin;scrollbar-color:#00704a #1e3932;">
  {inner}
</div>"""