"""
simulate.py — Quench Café Stochastic Demand Simulation Engine
==============================================================
Run any scenario 1000 times and get the full distribution of outcomes.
Not "expect 140 orders" — but "here's every version of this day."

Usage:
    from simulate import Scenario, run_simulation, summarize, print_report
    scenario = Scenario(weather="rainy", is_finals=True, soft_serve=True)
    results  = run_simulation(scenario, n_simulations=1000)
    print_report(results, scenario)
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from scipy import stats

# --------------------------------------------------
# CONSTANTS — mirrors your data generator
# --------------------------------------------------

CATEGORIES = ["espresso", "latte", "refresher", "coffee", "tea", "food", "hot_special"]

PERSONALITY_TYPES  = ["sunny_social", "chill_studious", "rushed_professional",
                      "moody_intense", "adventurous", "cozy_comfort"]
PERSONALITY_PROBS  = [0.20, 0.25, 0.20, 0.15, 0.10, 0.10]

# Prep + cleaning time per category (seconds)
# Latte = 90s prep + 25s clean, Refresher = 40s + 25s, etc.
SERVICE_TIME = {
    "espresso":   55,
    "latte":      115,
    "refresher":  65,
    "coffee":     25,
    "tea":        30,
    "food":       10,
    "hot_special": 85,
}

# One barista can handle ~3600s/hr of service
# but realistically peaks at ~2700s/hr (75% efficiency)
BARISTA_CAPACITY_PER_HOUR = 2700   # seconds

# Peak hours for volume distribution
MORNING_PEAK  = [8, 9, 10]
AFTERNOON_PEAK = [16, 17, 18, 19]
ALL_HOURS     = list(range(7, 22))

# --------------------------------------------------
# SCENARIO DEFINITION
# --------------------------------------------------

@dataclass
class Scenario:
    """
    Define the conditions for a simulated day.

    Examples:
        Scenario(weather="rainy", is_finals=True, soft_serve=True)
        Scenario(weather="snow", day_of_week="Monday")
        Scenario(weather="sunny", is_pre_finals=True, soft_serve=False)
    """
    weather:        str   = "rainy"       # rainy | cloudy | sunny | snow
    day_of_week:    str   = "Monday"      # Monday–Sunday
    soft_serve:     bool  = False
    is_finals:      bool  = False
    is_pre_finals:  bool  = False
    is_quarter_start: bool = False

    def label(self) -> str:
        tags = [self.weather, self.day_of_week]
        if self.is_finals:      tags.append("FINALS WEEK")
        if self.is_pre_finals:  tags.append("pre-finals")
        if self.is_quarter_start: tags.append("quarter start")
        if self.soft_serve:     tags.append("soft serve ON")
        return " · ".join(tags)


# --------------------------------------------------
# CORE PROBABILITY MODELS
# (learned from your data generator's behavioral rules)
# --------------------------------------------------

def sample_daily_volume(scenario: Scenario) -> int:
    """Sample how many orders happen today."""
    base = np.random.randint(70, 110)

    if scenario.soft_serve:
        base += np.random.randint(15, 30)
    if scenario.weather == "snow":
        base += np.random.randint(30, 50)
    if scenario.is_finals:
        base += np.random.randint(35, 55)
    if scenario.is_pre_finals:
        base += np.random.randint(15, 30)
    if scenario.is_quarter_start:
        base += np.random.randint(10, 20)

    return base


def sample_hour() -> int:
    """Sample which hour an order arrives — peak-weighted."""
    r = np.random.rand()
    if r < 0.35:
        return np.random.choice(MORNING_PEAK)
    elif r < 0.70:
        return np.random.choice(AFTERNOON_PEAK)
    else:
        return np.random.randint(7, 22)


def sample_personality() -> str:
    return np.random.choice(PERSONALITY_TYPES, p=PERSONALITY_PROBS)


def sample_category(weather: str, hour: int, personality: str) -> str:
    """
    Category probability — mirrors get_category() in your generator.
    Same behavioral rules, same personality logic.
    """
    if weather == "snow":
        if personality in ["moody_intense", "rushed_professional"]:
            return np.random.choice(["espresso", "hot_special", "latte"], p=[0.5, 0.3, 0.2])
        return np.random.choice(["hot_special", "latte", "tea", "espresso"], p=[0.4, 0.35, 0.15, 0.10])

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
        return np.random.choice(["latte", "refresher", "tea", "espresso", "food"],
                                p=[0.30, 0.25, 0.20, 0.15, 0.10])

    # chill_studious — time-based default
    if 7 <= hour <= 11:
        return np.random.choice(["espresso", "coffee", "latte"], p=[0.45, 0.35, 0.20])
    if 12 <= hour <= 17:
        return np.random.choice(["refresher", "coffee", "latte", "food"], p=[0.35, 0.25, 0.25, 0.15])
    if 18 <= hour <= 21:
        return np.random.choice(["latte", "tea", "espresso", "food"], p=[0.40, 0.30, 0.20, 0.10])

    return np.random.choice(CATEGORIES)


# --------------------------------------------------
# SINGLE DAY SIMULATION
# --------------------------------------------------

def simulate_one_day(scenario: Scenario) -> dict:
    """
    Simulate a full day. Returns metrics for that one day.
    """
    n_orders = sample_daily_volume(scenario)

    category_counts = {c: 0 for c in CATEGORIES}
    hourly_load     = {h: 0 for h in ALL_HOURS}   # seconds of work per hour
    personality_counts = {p: 0 for p in PERSONALITY_TYPES}

    total_service_seconds = 0

    for _ in range(n_orders):
        hour        = sample_hour()
        personality = sample_personality()
        category    = sample_category(scenario.weather, hour, personality)

        # Snow → some orders become hot_special
        if scenario.weather == "snow" and np.random.rand() < 0.35:
            category = "hot_special"

        svc_time = SERVICE_TIME.get(category, 30)

        category_counts[category]    += 1
        hourly_load[hour]            += svc_time
        personality_counts[personality] += 1
        total_service_seconds        += svc_time

    # Stress score per hour: workload / barista capacity (>1.0 = overwhelmed)
    hourly_stress = {
        h: round(load / BARISTA_CAPACITY_PER_HOUR, 3)
        for h, load in hourly_load.items()
    }

    peak_stress_hour  = max(hourly_stress, key=hourly_stress.get)
    peak_stress_score = hourly_stress[peak_stress_hour]

    # What fraction of the day is the barista above capacity?
    hours_overwhelmed = sum(1 for s in hourly_stress.values() if s > 1.0)

    return {
        "total_orders":        n_orders,
        "total_service_min":   round(total_service_seconds / 60, 1),
        "category_counts":     category_counts,
        "hourly_load_sec":     hourly_load,
        "hourly_stress":       hourly_stress,
        "peak_stress_score":   peak_stress_score,
        "peak_stress_hour":    peak_stress_hour,
        "hours_overwhelmed":   hours_overwhelmed,
        "personality_counts":  personality_counts,
    }


# --------------------------------------------------
# MONTE CARLO: RUN N SIMULATIONS
# --------------------------------------------------

def run_simulation(scenario: Scenario, n_simulations: int = 1000) -> pd.DataFrame:
    """
    Run the scenario n times. Returns a DataFrame where each row
    is one simulated day — ready for distribution analysis.
    """
    print(f"Running {n_simulations} simulations for: {scenario.label()} ...")

    rows = []
    for _ in range(n_simulations):
        day = simulate_one_day(scenario)

        row = {
            "total_orders":       day["total_orders"],
            "total_service_min":  day["total_service_min"],
            "peak_stress_score":  day["peak_stress_score"],
            "peak_stress_hour":   day["peak_stress_hour"],
            "hours_overwhelmed":  day["hours_overwhelmed"],
        }

        # Flatten category counts
        for cat, cnt in day["category_counts"].items():
            row[f"cat_{cat}"] = cnt

        # Flatten personality counts
        for pers, cnt in day["personality_counts"].items():
            row[f"pers_{pers}"] = cnt

        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"Done. Shape: {df.shape}")
    return df


# --------------------------------------------------
# SUMMARY STATS
# --------------------------------------------------

def summarize(results: pd.DataFrame) -> dict:
    """
    Compute key summary statistics from simulation results.
    Returns a clean dict — easy to display or pass to Streamlit.
    """
    orders = results["total_orders"]

    summary = {
        # Order volume distribution
        "orders_mean":   round(orders.mean(), 1),
        "orders_median": round(orders.median(), 1),
        "orders_std":    round(orders.std(), 1),
        "orders_p5":     round(orders.quantile(0.05), 0),
        "orders_p25":    round(orders.quantile(0.25), 0),
        "orders_p75":    round(orders.quantile(0.75), 0),
        "orders_p95":    round(orders.quantile(0.95), 0),

        # Stress
        "stress_mean":        round(results["peak_stress_score"].mean(), 3),
        "stress_p95":         round(results["peak_stress_score"].quantile(0.95), 3),
        "pct_overwhelmed_days": round(
            (results["hours_overwhelmed"] > 0).mean() * 100, 1
        ),

        # Most common peak hour
        "most_common_peak_hour": int(results["peak_stress_hour"].mode()[0]),

        # Category breakdown (mean orders per category)
        "category_means": {
            cat: round(results[f"cat_{cat}"].mean(), 1)
            for cat in CATEGORIES
        },

        # Personality breakdown (mean per sim)
        "personality_means": {
            p: round(results[f"pers_{p}"].mean(), 1)
            for p in PERSONALITY_TYPES
        },
    }

    return summary


# --------------------------------------------------
# SCENARIO COMPARISON
# --------------------------------------------------

def compare_scenarios(scenarios: list[Scenario], n_simulations: int = 1000) -> pd.DataFrame:
    """
    Run multiple scenarios and return a comparison DataFrame.
    Great for: sunny vs rainy, finals vs normal, etc.
    """
    rows = []
    for sc in scenarios:
        results = run_simulation(sc, n_simulations)
        s = summarize(results)
        row = {
            "scenario":          sc.label(),
            "mean_orders":       s["orders_mean"],
            "p5_orders":         s["orders_p5"],
            "p95_orders":        s["orders_p95"],
            "stress_mean":       s["stress_mean"],
            "stress_p95":        s["stress_p95"],
            "pct_overwhelmed":   s["pct_overwhelmed_days"],
            "peak_hour":         s["most_common_peak_hour"],
        }
        # Add top category
        cat_means = s["category_means"]
        row["top_category"] = max(cat_means, key=cat_means.get)
        rows.append(row)

    return pd.DataFrame(rows)


# --------------------------------------------------
# HUMAN-READABLE REPORT
# --------------------------------------------------

def print_report(results: pd.DataFrame, scenario: Scenario):
    s = summarize(results)

    print("\n" + "="*60)
    print(f"  SIMULATION REPORT — {scenario.label()}")
    print("="*60)

    print(f"\n📦 ORDER VOLUME (across {len(results)} simulated days)")
    print(f"   Average:        {s['orders_mean']} orders")
    print(f"   Typical range:  {s['orders_p25']}–{s['orders_p75']} orders  (25th–75th pct)")
    print(f"   Best case  (5th pct):  {s['orders_p5']:.0f} orders")
    print(f"   Worst case (95th pct): {s['orders_p95']:.0f} orders")

    print(f"\n⚡ STRESS & CAPACITY")
    print(f"   Avg peak stress score:  {s['stress_mean']}  (>1.0 = overwhelmed)")
    print(f"   95th pct stress score:  {s['stress_p95']}")
    print(f"   Days with any overload: {s['pct_overwhelmed_days']}%")
    print(f"   Most common crunch hour: {s['most_common_peak_hour']}:00")

    print(f"\n☕ EXPECTED DRINK MIX (avg per day)")
    for cat, mean in sorted(s["category_means"].items(), key=lambda x: -x[1]):
        bar = "█" * int(mean / 3)
        print(f"   {cat:<12} {mean:>5.1f}  {bar}")

    print(f"\n🧠 CUSTOMER VIBE BREAKDOWN (avg per day)")
    for pers, mean in sorted(s["personality_means"].items(), key=lambda x: -x[1]):
        bar = "█" * int(mean / 5)
        print(f"   {pers:<22} {mean:>5.1f}  {bar}")

    print()


# --------------------------------------------------
# QUICK DEMO — run directly to test
# --------------------------------------------------

if __name__ == "__main__":

    print("\n🔬 SCENARIO 1: Normal rainy Monday")
    s1 = Scenario(weather="rainy", day_of_week="Monday")
    r1 = run_simulation(s1, n_simulations=1000)
    print_report(r1, s1)

    print("\n🔬 SCENARIO 2: Finals week, rainy, soft serve ON")
    s2 = Scenario(weather="rainy", day_of_week="Wednesday",
                  is_finals=True, soft_serve=True)
    r2 = run_simulation(s2, n_simulations=1000)
    print_report(r2, s2)

    print("\n🔬 SCENARIO 3: Snow day")
    s3 = Scenario(weather="snow", day_of_week="Tuesday")
    r3 = run_simulation(s3, n_simulations=1000)
    print_report(r3, s3)

    print("\n📊 SCENARIO COMPARISON TABLE")
    comparison = compare_scenarios([s1, s2, s3], n_simulations=500)
    print(comparison.to_string(index=False))