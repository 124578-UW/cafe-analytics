import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
START_DATE = datetime(2026, 1, 1)
NUM_DAYS = 80

# -----------------------------
# WEATHER
# -----------------------------
WEATHER_TYPES = ["rainy", "cloudy", "sunny", "snow"]
WEATHER_PROBS = [0.6, 0.25, 0.13, 0.02]

# -----------------------------
# MILK
# -----------------------------
MILK_TYPES = ["whole", "oat", "almond"]
MILK_PROBS = [0.5, 0.3, 0.2]

# -----------------------------
# SYRUPS (Fontana-style)
# -----------------------------
SYRUPS = [
    "none", "vanilla", "sugar_free_vanilla",
    "hazelnut", "caramel", "toffee_nut",
    "cinnamon_dolce", "brown_sugar"
]

# -----------------------------
# LATTE FLAVORS
# -----------------------------
LATTE_FLAVORS = [
    "none", "vanilla", "hazelnut", "caramel_brule",
    "pumpkin_spice", "irish_cream", "sugar_cookie",
    "chai", "matcha"
]

# -----------------------------
# REFRESHERS
# -----------------------------
REFRESHER_BASES = ["strawberry_acai", "dragonfruit", "pineapple_passionfruit"]
REFRESHER_LIQUIDS = ["water", "lemonade", "coconut_milk"]

# -----------------------------
# ESPRESSO DRINKS
# -----------------------------
ESPRESSO_DRINKS = [
    "caramel_macchiato",
    "mocha",
    "americano",
    "cappuccino",
    "cafe_misto",
    "flat_white",
    "brown_sugar_shaken_espresso",
    "cortado",
    "espresso_shot"
]

# -----------------------------
# COFFEE (BREWED)
# -----------------------------
COFFEE_DRINKS = [
    "drip_coffee",
    "cold_brew",
    "iced_coffee",
    "pour_over"
]

# -----------------------------
# TEA (Teavana-style)
# -----------------------------
TEA_DRINKS = [
    "english_breakfast_tea",
    "earl_grey_tea",
    "chamomile_tea",
    "citrus_tea",
    "iced_black_tea",
    "iced_green_tea",
    "hot_black_tea",
    "hot_green_tea",
    "london_fog_latte",
    "peach_green_tea",
    "passion_tango_tea"
]

# -----------------------------
# HOT DRINKS (cold weather)
# -----------------------------
HOT_SPECIALS = [
    "hot_chocolate",
    "peppermint_mocha",
    "caramel_apple_spice",
    "white_hot_chocolate"
]

# -----------------------------
# FOOD
# -----------------------------
FOOD_ITEMS = [
    "brownie", "cookie", "scone", "cake_pop",
    "banana_bread", "croissant", "bagel", "muffin"
]

# -----------------------------
# CUSTOMER PERSONALITY TYPES
# (inspired by real barista intuition)
# -----------------------------
PERSONALITY_TYPES = [
    "sunny_social",       # smiley, chatty, fun energy → refreshers, iced lattes, matcha
    "chill_studious",     # headphones, focused, polite → cold brew, iced coffee, plain latte
    "rushed_professional",# quick, no small talk → americano, drip, flat white
    "moody_intense",      # extra shot, extra hot, very specific → double espresso, cortado
    "adventurous",        # tries new things, asks questions → seasonal drinks, fancy lattes
    "cozy_comfort",       # wants warmth, often with food → hot chocolate, chai, scone
]

PERSONALITY_PROBS = [0.20, 0.25, 0.20, 0.15, 0.10, 0.10]

# -----------------------------
# CLEANING OVERHEAD (seconds)
# Equipment cleaned after each drink
# -----------------------------
CLEANING_OVERHEAD = {
    "latte":      {"pitcher": 15, "espresso_glass": 10},
    "espresso":   {"espresso_glass": 10},
    "refresher":  {"shaker": 20, "cup": 5},
    "coffee":     {"cup": 5},
    "tea":        {"cup": 5},
    "food":       {},
    "hot_special":{"pitcher": 10, "cup": 5},
}

# Prep time in seconds per drink category
PREP_TIME = {
    "latte":       90,
    "espresso":    45,
    "refresher":   40,
    "coffee":      20,
    "tea":         25,
    "food":        10,
    "hot_special": 70,
}

# -----------------------------
# DATES + SOFT SERVE SCHEDULE
# -----------------------------
dates = [START_DATE + timedelta(days=i) for i in range(NUM_DAYS)]

soft_serve_schedule = {}
for d in dates:
    if d.weekday() == 3:  # Thursday
        soft_serve_schedule[d.date()] = np.random.choice([1, 0], p=[0.7, 0.3])
    else:
        soft_serve_schedule[d.date()] = np.random.choice([1, 0], p=[0.3, 0.7])

# -----------------------------
# UW WINTER QUARTER 2026 ACADEMIC CALENDAR
# Source: https://www.washington.edu/students/reg/2526cal.html
# Instruction: Jan 5 – Mar 13, 2026
# Finals week: Mar 14–20, 2026
# Holidays (closed/no class): Jan 1, Jan 19 (MLK), Feb 16 (Presidents Day)
# -----------------------------

# Finals week — peak stress, peak orders
FINALS_DATES = set(
    (datetime(2026, 3, 14) + timedelta(days=i)).date()
    for i in range(7)  # Mar 14–20
)

# Pre-finals cramming week — elevated but not peak
PRE_FINALS_DATES = set(
    (datetime(2026, 3, 7) + timedelta(days=i)).date()
    for i in range(7)  # Mar 7–13 (last week of instruction)
)

# University holidays — Quench likely closed or very quiet
HOLIDAY_DATES = {
    datetime(2026, 1, 1).date(),   # New Year's Day
    datetime(2026, 1, 19).date(),  # MLK Day
    datetime(2026, 2, 16).date(),  # Presidents' Day
}

# Quarter start buzz — first week of classes, students exploring campus
QUARTER_START_DATES = set(
    (datetime(2026, 1, 5) + timedelta(days=i)).date()
    for i in range(5)  # Jan 5–9
)

# -----------------------------
# HELPERS
# -----------------------------
def get_weather():
    return np.random.choice(WEATHER_TYPES, p=WEATHER_PROBS)

def get_group_size():
    return np.random.choice([1, 2, 3, 4], p=[0.55, 0.28, 0.12, 0.05])

def get_personality():
    return np.random.choice(PERSONALITY_TYPES, p=PERSONALITY_PROBS)

# -----------------------------
# CATEGORY LOGIC
# Driven by time + weather + personality (the vibe matters!)
# -----------------------------
def get_category(weather, hour, personality):

    # Snow → everyone wants warmth
    if weather == "snow":
        if personality in ["moody_intense", "rushed_professional"]:
            return np.random.choice(["espresso", "hot_special", "latte"], p=[0.5, 0.3, 0.2])
        return np.random.choice(["hot_special", "latte", "tea", "espresso"], p=[0.4, 0.35, 0.15, 0.10])

    # Personality-driven overrides
    if personality == "sunny_social":
        if 12 <= hour <= 21:
            return np.random.choice(["refresher", "latte", "food"], p=[0.55, 0.35, 0.10])
        return np.random.choice(["latte", "espresso", "refresher"], p=[0.5, 0.3, 0.2])

    if personality == "moody_intense":
        return np.random.choice(["espresso", "coffee", "latte"], p=[0.6, 0.25, 0.15])

    if personality == "rushed_professional":
        return np.random.choice(["espresso", "coffee", "latte"], p=[0.5, 0.35, 0.15])

    if personality == "cozy_comfort":
        if weather in ["rainy", "cloudy", "snow"]:
            return np.random.choice(["hot_special", "latte", "tea", "food"], p=[0.35, 0.30, 0.20, 0.15])
        return np.random.choice(["latte", "tea", "food", "espresso"], p=[0.35, 0.30, 0.20, 0.15])

    if personality == "adventurous":
        return np.random.choice(
            ["latte", "refresher", "tea", "espresso", "food"],
            p=[0.30, 0.25, 0.20, 0.15, 0.10]
        )

    # chill_studious — time-based
    if 7 <= hour <= 11:
        return np.random.choice(["espresso", "coffee", "latte"], p=[0.45, 0.35, 0.20])
    if 12 <= hour <= 17:
        return np.random.choice(["refresher", "coffee", "latte", "food"], p=[0.35, 0.25, 0.25, 0.15])
    if 18 <= hour <= 21:
        return np.random.choice(["latte", "tea", "espresso", "food"], p=[0.40, 0.30, 0.20, 0.10])

    return np.random.choice(
        ["espresso", "latte", "refresher", "coffee", "tea", "food"],
        p=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
    )

# -----------------------------
# TIMESTAMP GENERATION
# Peak hours weighted: 8-10am and 4-7pm (your shift!)
# -----------------------------
def generate_timestamp(date):
    r = np.random.rand()
    if r < 0.35:
        hour = np.random.choice([8, 9, 10])        # morning rush
    elif r < 0.70:
        hour = np.random.choice([16, 17, 18, 19])  # afternoon peak (your shift)
    else:
        hour = np.random.randint(7, 22)             # rest of day

    minute = np.random.randint(0, 60)
    return datetime(date.year, date.month, date.day, hour, minute)

# -----------------------------
# DRINK GENERATORS
# -----------------------------
def generate_refresher():
    base = random.choice(REFRESHER_BASES)
    liquid = np.random.choice(REFRESHER_LIQUIDS, p=[0.4, 0.35, 0.25])
    return base, liquid

def generate_latte(personality):
    if personality == "sunny_social":
        return np.random.choice(["matcha", "vanilla", "chai", "caramel_brule"], p=[0.35, 0.30, 0.20, 0.15])
    if personality == "adventurous":
        return np.random.choice(LATTE_FLAVORS)
    if personality == "cozy_comfort":
        return np.random.choice(["chai", "vanilla", "pumpkin_spice", "none"], p=[0.35, 0.30, 0.25, 0.10])
    return np.random.choice(LATTE_FLAVORS)

def generate_espresso(personality):
    if personality == "moody_intense":
        return np.random.choice(["americano", "espresso_shot", "cortado", "flat_white"], p=[0.35, 0.30, 0.20, 0.15])
    if personality == "rushed_professional":
        return np.random.choice(["americano", "flat_white", "cappuccino", "cafe_misto"], p=[0.40, 0.25, 0.20, 0.15])
    return random.choice(ESPRESSO_DRINKS)

def generate_hot_special():
    return random.choice(HOT_SPECIALS)

def generate_coffee():
    return random.choice(COFFEE_DRINKS)

def generate_tea(personality):
    if personality == "cozy_comfort":
        return np.random.choice(["chamomile_tea", "english_breakfast_tea", "london_fog_latte", "earl_grey_tea"],
                                p=[0.30, 0.30, 0.25, 0.15])
    if personality == "sunny_social":
        return np.random.choice(["iced_green_tea", "peach_green_tea", "passion_tango_tea", "iced_black_tea"],
                                p=[0.35, 0.30, 0.20, 0.15])
    return random.choice(TEA_DRINKS)

def generate_food(personality):
    if personality == "cozy_comfort":
        return np.random.choice(["brownie", "scone", "muffin", "croissant"], p=[0.35, 0.30, 0.20, 0.15])
    if personality == "chill_studious":
        return np.random.choice(["bagel", "banana_bread", "muffin", "cookie"], p=[0.35, 0.25, 0.25, 0.15])
    return random.choice(FOOD_ITEMS)

# -----------------------------
# CUSTOMIZATION LOGIC
# -----------------------------
def get_size(category, group_size, personality):
    if category == "refresher":
        return np.random.choice(["venti", "grande"], p=[0.70, 0.30])

    if personality == "moody_intense":
        return np.random.choice(["tall", "grande"], p=[0.6, 0.4])  # no venti nonsense

    if group_size >= 3:
        return np.random.choice(["grande", "venti"], p=[0.45, 0.55])
    if group_size == 2:
        return np.random.choice(["grande", "venti"], p=[0.60, 0.40])

    return np.random.choice(["tall", "grande", "venti"], p=[0.35, 0.45, 0.20])

def get_milk(category, drink_name, personality):
    if drink_name in ["brown_sugar_shaken_espresso"]:
        return "oat"
    if "tea" in drink_name and drink_name not in ["london_fog_latte", "peach_green_tea", "passion_tango_tea"]:
        return "none"
    if category in ["coffee", "espresso"]:
        if drink_name in ["americano", "espresso_shot", "cortado", "drip_coffee", "pour_over", "cold_brew"]:
            return "none"
    # personality-based milk preferences
    if personality == "sunny_social":
        return np.random.choice(MILK_TYPES, p=[0.3, 0.5, 0.2])   # oat milk is their thing
    if personality == "adventurous":
        return np.random.choice(MILK_TYPES, p=[0.3, 0.35, 0.35])
    return np.random.choice(MILK_TYPES, p=MILK_PROBS)

def get_syrup(category, drink_name, latte_flavor, personality):
    if drink_name in ["americano", "espresso_shot", "cortado", "drip_coffee", "pour_over"]:
        return "none"
    if "tea" in drink_name and drink_name not in ["london_fog_latte"]:
        return "none"
    if category == "latte":
        if latte_flavor and latte_flavor != "none":
            return latte_flavor
        # sunny social loves vanilla
        if personality == "sunny_social":
            return np.random.choice(["vanilla", "none", "brown_sugar"], p=[0.5, 0.3, 0.2])
        return np.random.choice(["none", "vanilla", "caramel"], p=[0.5, 0.3, 0.2])
    if personality == "moody_intense":
        return "none"
    return np.random.choice(SYRUPS)

def get_extra_shot(personality, category):
    """moody_intense and rushed_professional sometimes want extra shots"""
    if category not in ["latte", "espresso", "coffee"]:
        return 0
    if personality == "moody_intense":
        return np.random.choice([1, 0], p=[0.55, 0.45])
    if personality == "rushed_professional":
        return np.random.choice([1, 0], p=[0.30, 0.70])
    return 0

def get_extra_hot(personality):
    """moody_intense specifically asks for extra hot"""
    if personality == "moody_intense":
        return np.random.choice([1, 0], p=[0.60, 0.40])
    return 0

def get_cold_foam(category, drink_name, personality):
    if drink_name in ["matcha_latte", "none_latte", "vanilla_latte"]:
        if personality == "sunny_social":
            return np.random.choice([1, 0], p=[0.75, 0.25])
        return np.random.choice([1, 0], p=[0.65, 0.35])
    if category == "latte":
        if personality in ["sunny_social", "adventurous"]:
            return np.random.choice([1, 0], p=[0.55, 0.45])
        return np.random.choice([1, 0], p=[0.40, 0.60])
    return 0

def get_whipped_cream(drink_name, personality):
    if drink_name in HOT_SPECIALS:
        return np.random.choice([1, 0], p=[0.85, 0.15])
    if drink_name == "mocha":
        return np.random.choice([1, 0], p=[0.75, 0.25])
    if personality == "cozy_comfort" and drink_name in ["peppermint_mocha", "white_hot_chocolate"]:
        return 1
    return 0

def get_iced(category, drink_name, personality, weather):
    if category == "refresher":
        return 1
    if "iced" in drink_name:
        return 1
    if drink_name in HOT_SPECIALS or "hot" in drink_name:
        return 0
    if weather == "snow":
        return 0
    if personality == "sunny_social":
        return np.random.choice([1, 0], p=[0.70, 0.30])
    if personality == "moody_intense":
        return np.random.choice([1, 0], p=[0.30, 0.70])  # prefers hot
    if weather == "sunny":
        return np.random.choice([1, 0], p=[0.65, 0.35])
    return np.random.choice([1, 0], p=[0.45, 0.55])

def get_food_pairing(drink_name, personality):
    """Chance of also ordering food alongside drink — your brownie insight!"""
    if personality == "cozy_comfort":
        prob = 0.45
    elif personality == "chill_studious":
        prob = 0.30
    elif drink_name in ["hot_chocolate", "chai_latte", "london_fog_latte", "peppermint_mocha"]:
        prob = 0.35  # hot comfort drink → brownie tendency
    else:
        prob = 0.12
    return np.random.choice([1, 0], p=[prob, 1 - prob])

def get_cleaning_time(category):
    overhead = CLEANING_OVERHEAD.get(category, {})
    return sum(overhead.values())

def get_total_service_time(category):
    prep = PREP_TIME.get(category, 30)
    clean = get_cleaning_time(category)
    return prep + clean

# -----------------------------
# MAIN LOOP
# -----------------------------
data = []
order_id = 0

for d in dates:
    weather = get_weather()
    date = d.date()

    is_finals        = 1 if date in FINALS_DATES else 0
    is_pre_finals    = 1 if date in PRE_FINALS_DATES else 0
    is_quarter_start = 1 if date in QUARTER_START_DATES else 0

    # UW holidays — Quench closed, skip entirely
    if date in HOLIDAY_DATES:
        continue

    # Realistic daily volume
    base_orders = np.random.randint(70, 110)

    if soft_serve_schedule[date] == 1:
        base_orders += np.random.randint(15, 30)

    if weather == "snow":
        base_orders += np.random.randint(30, 50)

    if is_finals:
        base_orders += np.random.randint(35, 55)   # peak stress = peak caffeine

    if is_pre_finals:
        base_orders += np.random.randint(15, 30)   # cramming week surge

    if is_quarter_start:
        base_orders += np.random.randint(10, 20)   # first-week curiosity buzz

    for _ in range(base_orders):
        ts = generate_timestamp(d)
        group_size = get_group_size()
        personality = get_personality()
        category = get_category(weather, ts.hour, personality)

        base = None
        liquid = None
        latte_flavor = None
        drink_name = None

        # Snow → hot specials spike
        if weather == "snow" and np.random.rand() < 0.35:
            drink_name = generate_hot_special()
            category = "hot_special"

        elif category == "refresher":
            base, liquid = generate_refresher()
            drink_name = f"{base}_{liquid}"

        elif category == "latte":
            latte_flavor = generate_latte(personality)
            if latte_flavor == "matcha":
                drink_name = "matcha_latte"
            elif latte_flavor != "none":
                drink_name = f"{latte_flavor}_latte"
            else:
                drink_name = "latte"

        elif category == "hot_special":
            drink_name = generate_hot_special()

        elif category == "coffee":
            drink_name = generate_coffee()

        elif category == "tea":
            drink_name = generate_tea(personality)

        elif category == "food":
            drink_name = generate_food(personality)

        else:  # espresso
            drink_name = generate_espresso(personality)

        row = {
            "order_id":           order_id,
            "timestamp":          ts,
            "day_of_week":        ts.strftime("%A"),
            "hour":               ts.hour,
            "weather":            weather,
            "is_outlier_event":   1 if weather == "snow" else 0,
            "is_finals_week":     is_finals,
            "is_pre_finals":      is_pre_finals,
            "is_quarter_start":   is_quarter_start,
            "group_size":         group_size,
            "personality_type":   personality,
            "category":           category,
            "drink_name":         drink_name,
            "base":               base,
            "liquid":             liquid,
            "latte_flavor":       latte_flavor,
            "size":               get_size(category, group_size, personality),
            "milk":               get_milk(category, drink_name, personality),
            "syrup":              get_syrup(category, drink_name, latte_flavor, personality),
            "extra_shot":         get_extra_shot(personality, category),
            "extra_hot":          get_extra_hot(personality),
            "cold_foam":          get_cold_foam(category, drink_name, personality),
            "whipped_cream":      get_whipped_cream(drink_name, personality),
            "iced":               get_iced(category, drink_name, personality, weather),
            "food_pairing":       get_food_pairing(drink_name, personality),
            "soft_serve_active":  soft_serve_schedule[ts.date()],
            "prep_time_sec":      PREP_TIME.get(category, 30),
            "cleaning_time_sec":  get_cleaning_time(category),
            "total_service_time": get_total_service_time(category),
        }

        data.append(row)
        order_id += 1

df = pd.DataFrame(data)
df.to_csv("data/cafe_orders_synthetic.csv", index=False)

print("Dataset generated:", df.shape)
print(f"Date range: {df['timestamp'].min()} → {df['timestamp'].max()}")
print(f"\nPersonality distribution:\n{df['personality_type'].value_counts()}")
print(f"\nCategory distribution:\n{df['category'].value_counts()}")
print(f"\nTop 10 drinks:\n{df['drink_name'].value_counts().head(10)}")
print(f"\nFinalsweek orders: {df['is_finals_week'].sum()}")
print(f"\nAvg service time by category:\n{df.groupby('category')['total_service_time'].mean().round(1)}")