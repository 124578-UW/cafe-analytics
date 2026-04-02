"""
vibe_model.py — The Vibe Index
================================
Two models, one idea: personality and drink choice are two sides
of the same coin.

MODEL A — Forward (Barista Intuition):
    context + vibe → predict drink category
    "A sunny_social walks in at 4pm on a rainy day... refresher."

MODEL B — Reverse (Vibe Inference):
    drink order fingerprint → infer personality type
    "Oat milk, vanilla cold foam, iced, grande... that's a sunny_social."

Both get feature importance analysis so you can see *why* the model
thinks what it thinks — and compare it to your real barista intuition.

Usage:
    python vibe_model.py
    
Or import:
    from vibe_model import train_forward_model, train_reverse_model
    from vibe_model import predict_vibe, predict_drink, vibe_report
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings("ignore")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data(path: str = "data/cafe_orders_synthetic.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Time features
    df["is_morning"]   = df["hour"].between(7, 11).astype(int)
    df["is_afternoon"] = df["hour"].between(12, 17).astype(int)
    df["is_evening"]   = df["hour"].between(18, 21).astype(int)
    df["is_peak_hour"] = df["hour"].isin([8, 9, 16, 17, 18]).astype(int)
    df["is_weekend"]   = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

    # Drink complexity score — how "fancy" is the order?
    # (This is a proxy for personality — moody_intense = simple,
    #  sunny_social = elaborate)
    df["customization_score"] = (
        df["cold_foam"] +
        df["whipped_cream"] +
        df["extra_shot"] +
        df["extra_hot"] +
        (df["syrup"] != "none").astype(int) +
        (df["milk"].isin(["oat", "almond"])).astype(int)
    )

    # Is the drink a "comfort" drink?
    comfort_drinks = ["hot_chocolate", "chai_latte", "peppermint_mocha",
                      "london_fog_latte", "white_hot_chocolate", "caramel_apple_spice"]
    df["is_comfort_drink"] = df["drink_name"].isin(comfort_drinks).astype(int)

    # Is it a "vibe" drink? (the ones sunny_social orders)
    vibe_drinks = ["matcha_latte", "strawberry_acai_lemonade", "dragonfruit_lemonade",
                   "vanilla_latte", "strawberry_acai_water", "dragonfruit_coconut_milk"]
    df["is_vibe_drink"] = df["drink_name"].isin(vibe_drinks).astype(int)

    # Is it a "straight" drink? (moody_intense / rushed_professional)
    straight_drinks = ["americano", "espresso_shot", "cortado", "drip_coffee",
                       "pour_over", "flat_white", "cold_brew"]
    df["is_straight_drink"] = df["drink_name"].isin(straight_drinks).astype(int)

    # Group interaction: group_size × is_peak_hour
    df["group_x_peak"] = df["group_size"] * df["is_peak_hour"]

    # Hot vs cold preference
    df["prefers_cold"] = df["iced"].astype(int)

    return df


def encode_categoricals(df: pd.DataFrame, fit_encoders: dict = None):
    """
    One-hot encode categoricals.
    Pass fit_encoders=None on training, pass the fitted encoders for inference.
    Returns (encoded_df, encoders_dict)
    """
    cat_cols = ["weather", "category", "milk", "syrup", "size",
                "day_of_week", "drink_name"]

    df_enc = df.copy()
    encoders = fit_encoders or {}

    for col in cat_cols:
        if col not in df_enc.columns:
            continue
        dummies = pd.get_dummies(df_enc[col], prefix=col, drop_first=False)
        df_enc  = pd.concat([df_enc.drop(columns=[col]), dummies], axis=1)

    return df_enc, encoders


# --------------------------------------------------
# MODEL A — FORWARD: context + vibe → drink category
# --------------------------------------------------

FORWARD_FEATURES = [
    # Context
    "hour", "is_morning", "is_afternoon", "is_evening",
    "is_peak_hour", "is_weekend", "group_size", "group_x_peak",
    "soft_serve_active", "is_finals_week", "is_pre_finals",
    # Weather (one-hot added after encoding)
    # Vibe
    "personality_type",
]

def prepare_forward_data(df: pd.DataFrame):
    df_fe = engineer_features(df)

    # One-hot: weather + personality
    feature_df = pd.get_dummies(
        df_fe[["hour", "is_morning", "is_afternoon", "is_evening",
               "is_peak_hour", "is_weekend", "group_size", "group_x_peak",
               "soft_serve_active", "is_finals_week", "is_pre_finals",
               "weather", "personality_type"]],
        columns=["weather", "personality_type"],
        drop_first=False
    )

    target = df_fe["category"]
    return feature_df, target


def train_forward_model(df: pd.DataFrame, save_dir: str = "models"):
    """
    Train Model A: predict drink category from context + personality.
    Returns (model, label_encoder, feature_columns, metrics)
    """
    print("\n" + "="*60)
    print("  MODEL A — FORWARD: Vibe → Drink Category")
    print("="*60)

    X, y = prepare_forward_data(df)
    feature_cols = X.columns.tolist()

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Cross-val score
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y_enc, cv=cv, scoring="accuracy")

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred,
                                   target_names=le.classes_,
                                   output_dict=True)

    print(f"\n  CV Accuracy:  {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(f"  Test Accuracy: {report['accuracy']:.3f}")
    print(f"\n  Per-class performance:")
    for cls in le.classes_:
        r = report[cls]
        print(f"    {cls:<22}  precision={r['precision']:.2f}  recall={r['recall']:.2f}  f1={r['f1-score']:.2f}")

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    top_features = importances.sort_values(ascending=False).head(15)
    print(f"\n  Top 15 features driving drink category:")
    for feat, imp in top_features.items():
        bar = "█" * int(imp * 300)
        print(f"    {feat:<45} {imp:.4f}  {bar}")

    # Save
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(model,        f"{save_dir}/forward_model.pkl")
    joblib.dump(le,           f"{save_dir}/forward_label_encoder.pkl")
    joblib.dump(feature_cols, f"{save_dir}/forward_feature_cols.pkl")
    print(f"\n  ✅ Saved to {save_dir}/")

    metrics = {
        "cv_mean": round(cv_scores.mean(), 3),
        "cv_std":  round(cv_scores.std(), 3),
        "test_acc": round(report["accuracy"], 3),
        "report":  report,
        "feature_importance": importances.sort_values(ascending=False),
    }
    return model, le, feature_cols, metrics


# --------------------------------------------------
# MODEL B — REVERSE: drink fingerprint → personality
# --------------------------------------------------

REVERSE_FEATURES = [
    "hour", "is_morning", "is_afternoon", "is_evening", "is_peak_hour",
    "group_size", "cold_foam", "whipped_cream", "extra_shot", "extra_hot",
    "iced", "customization_score", "is_comfort_drink", "is_vibe_drink",
    "is_straight_drink", "prefers_cold", "food_pairing",
    # encoded: category, milk, syrup, size, weather
]

def prepare_reverse_data(df: pd.DataFrame):
    df_fe = engineer_features(df)

    base_cols = [
        "hour", "is_morning", "is_afternoon", "is_evening", "is_peak_hour",
        "group_size", "cold_foam", "whipped_cream", "extra_shot", "extra_hot",
        "iced", "customization_score", "is_comfort_drink", "is_vibe_drink",
        "is_straight_drink", "prefers_cold", "food_pairing",
        "category", "milk", "syrup", "size", "weather"
    ]
    # only keep columns that exist
    base_cols = [c for c in base_cols if c in df_fe.columns]

    feature_df = pd.get_dummies(
        df_fe[base_cols],
        columns=["category", "milk", "syrup", "size", "weather"],
        drop_first=False
    )

    target = df_fe["personality_type"]
    return feature_df, target


def train_reverse_model(df: pd.DataFrame, save_dir: str = "models"):
    """
    Train Model B: infer personality from the drink order fingerprint.
    Returns (model, label_encoder, feature_columns, metrics)
    """
    print("\n" + "="*60)
    print("  MODEL B — REVERSE: Drink Fingerprint → Personality")
    print("="*60)

    X, y = prepare_reverse_data(df)
    feature_cols = X.columns.tolist()

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y_enc, cv=cv, scoring="accuracy")

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred,
                                   target_names=le.classes_,
                                   output_dict=True)

    print(f"\n  CV Accuracy:  {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(f"  Test Accuracy: {report['accuracy']:.3f}")
    print(f"\n  Per-class performance:")
    for cls in le.classes_:
        r = report[cls]
        print(f"    {cls:<22}  precision={r['precision']:.2f}  recall={r['recall']:.2f}  f1={r['f1-score']:.2f}")

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=feature_cols)
    top_features = importances.sort_values(ascending=False).head(15)
    print(f"\n  Top 15 features that reveal personality:")
    for feat, imp in top_features.items():
        bar = "█" * int(imp * 300)
        print(f"    {feat:<45} {imp:.4f}  {bar}")

    # --- Personality Archetypes: what does each type "look like"? ---
    print(f"\n  🧠 PERSONALITY ARCHETYPES (what each vibe looks like):")
    df_fe = engineer_features(df)
    for ptype in sorted(df["personality_type"].unique()):
        sub = df_fe[df_fe["personality_type"] == ptype]
        top_cat    = sub["category"].value_counts().index[0]
        top_drink  = sub["drink_name"].value_counts().index[0]
        top_milk   = sub["milk"].value_counts().index[0]
        avg_custom = sub["customization_score"].mean()
        pct_iced   = sub["iced"].mean() * 100
        pct_extra  = sub["extra_shot"].mean() * 100
        pct_foam   = sub["cold_foam"].mean() * 100
        print(f"\n    [{ptype}]")
        print(f"      Top drink:    {top_drink} ({top_cat})")
        print(f"      Milk:         {top_milk}")
        print(f"      Avg complexity score:  {avg_custom:.2f}")
        print(f"      % iced:       {pct_iced:.0f}%")
        print(f"      % extra shot: {pct_extra:.0f}%")
        print(f"      % cold foam:  {pct_foam:.0f}%")

    # Save
    os.makedirs(save_dir, exist_ok=True)
    joblib.dump(model,        f"{save_dir}/reverse_model.pkl")
    joblib.dump(le,           f"{save_dir}/reverse_label_encoder.pkl")
    joblib.dump(feature_cols, f"{save_dir}/reverse_feature_cols.pkl")
    print(f"\n  ✅ Saved to {save_dir}/")

    metrics = {
        "cv_mean":  round(cv_scores.mean(), 3),
        "cv_std":   round(cv_scores.std(), 3),
        "test_acc": round(report["accuracy"], 3),
        "report":   report,
        "feature_importance": importances.sort_values(ascending=False),
    }
    return model, le, feature_cols, metrics


# --------------------------------------------------
# INFERENCE FUNCTIONS (used by Streamlit later)
# --------------------------------------------------

def predict_drink(hour, weather, personality, group_size,
                  soft_serve=0, is_finals=0, is_pre_finals=0,
                  model_dir="models"):
    """
    Model A inference: given context + vibe, predict drink category
    with probability distribution.
    """
    model    = joblib.load(f"{model_dir}/forward_model.pkl")
    le       = joblib.load(f"{model_dir}/forward_label_encoder.pkl")
    feat_cols = joblib.load(f"{model_dir}/forward_feature_cols.pkl")

    is_morning   = int(7 <= hour <= 11)
    is_afternoon = int(12 <= hour <= 17)
    is_evening   = int(18 <= hour <= 21)
    is_peak      = int(hour in [8, 9, 16, 17, 18])
    is_weekend   = 0  # default weekday

    row = {
        "hour": hour, "is_morning": is_morning, "is_afternoon": is_afternoon,
        "is_evening": is_evening, "is_peak_hour": is_peak,
        "is_weekend": is_weekend, "group_size": group_size,
        "group_x_peak": group_size * is_peak,
        "soft_serve_active": soft_serve,
        "is_finals_week": is_finals, "is_pre_finals": is_pre_finals,
        f"weather_{weather}": 1,
        f"personality_type_{personality}": 1,
    }

    X = pd.DataFrame([row]).reindex(columns=feat_cols, fill_value=0)
    probs  = model.predict_proba(X)[0]
    labels = le.inverse_transform(np.arange(len(probs)))

    result = dict(zip(labels, probs.round(4)))
    return dict(sorted(result.items(), key=lambda x: -x[1]))


def predict_vibe(category, milk, syrup, size, cold_foam, iced,
                 extra_shot, extra_hot, whipped_cream, hour,
                 group_size, weather, food_pairing=0,
                 model_dir="models"):
    """
    Model B inference: given a drink fingerprint, infer personality.
    Returns probability distribution over personality types.
    """
    model     = joblib.load(f"{model_dir}/reverse_model.pkl")
    le        = joblib.load(f"{model_dir}/reverse_label_encoder.pkl")
    feat_cols = joblib.load(f"{model_dir}/reverse_feature_cols.pkl")

    custom_score = (
        cold_foam + whipped_cream + extra_shot + extra_hot +
        int(syrup != "none") +
        int(milk in ["oat", "almond"])
    )

    comfort = int(category in ["hot_special"])
    vibe    = int(category == "refresher" or
                  (category == "latte" and syrup in ["vanilla", "matcha"]))
    straight = int(category == "espresso" or category == "coffee")

    row = {
        "hour": hour, "is_morning": int(7<=hour<=11),
        "is_afternoon": int(12<=hour<=17), "is_evening": int(18<=hour<=21),
        "is_peak_hour": int(hour in [8,9,16,17,18]),
        "group_size": group_size,
        "cold_foam": cold_foam, "whipped_cream": whipped_cream,
        "extra_shot": extra_shot, "extra_hot": extra_hot,
        "iced": iced, "customization_score": custom_score,
        "is_comfort_drink": comfort, "is_vibe_drink": vibe,
        "is_straight_drink": straight, "prefers_cold": iced,
        "food_pairing": food_pairing,
        f"category_{category}": 1,
        f"milk_{milk}": 1,
        f"syrup_{syrup}": 1,
        f"size_{size}": 1,
        f"weather_{weather}": 1,
    }

    X = pd.DataFrame([row]).reindex(columns=feat_cols, fill_value=0)
    probs  = model.predict_proba(X)[0]
    labels = le.inverse_transform(np.arange(len(probs)))

    result = dict(zip(labels, probs.round(4)))
    return dict(sorted(result.items(), key=lambda x: -x[1]))


# --------------------------------------------------
# VIBE REPORT — human-readable personality profile
# --------------------------------------------------

VIBE_DESCRIPTIONS = {
    "sunny_social": (
        "☀️  Sunny Social",
        "Walks in smiling, probably with friends. Oat milk, vanilla cold foam, "
        "something iced and colorful. Will compliment your playlist."
    ),
    "chill_studious": (
        "📚  Chill Studious",
        "Headphones on, needs fuel not fun. Cold brew or plain iced latte. "
        "Polite, efficient, back to their laptop in 90 seconds."
    ),
    "rushed_professional": (
        "💼  Rushed Professional",
        "No time for questions. Americano or flat white. "
        "Out the door before you finish the sleeve."
    ),
    "moody_intense": (
        "🖤  Moody Intense",
        "Extra shot, extra hot, very specific. Probably has a strong opinion "
        "about espresso roast. Nods instead of saying thank you."
    ),
    "adventurous": (
        "🌀  Adventurous",
        "Asks 'what do you recommend?' and actually listens. "
        "Will try the seasonal thing. Might get two drinks."
    ),
    "cozy_comfort": (
        "🧸  Cozy Comfort",
        "Wants warmth in a cup. Chai, hot chocolate, london fog. "
        "Almost always gets a brownie. Stays a while."
    ),
}

def vibe_report(probs: dict) -> str:
    top_vibe  = list(probs.keys())[0]
    top_prob  = list(probs.values())[0]
    title, desc = VIBE_DESCRIPTIONS.get(top_vibe, (top_vibe, ""))

    lines = [
        f"\n  🔮 VIBE READING",
        f"  {'─'*50}",
        f"  {title}  ({top_prob*100:.0f}% confidence)",
        f"  {desc}",
        f"\n  Full probability breakdown:",
    ]
    for vibe, prob in probs.items():
        bar   = "█" * int(prob * 40)
        vtitle = VIBE_DESCRIPTIONS.get(vibe, (vibe,))[0]
        lines.append(f"    {vtitle:<28}  {prob*100:5.1f}%  {bar}")

    return "\n".join(lines)


# --------------------------------------------------
# MAIN — train both models and demo inference
# --------------------------------------------------

if __name__ == "__main__":
    print("Loading data...")
    df = load_data("data/cafe_orders_synthetic.csv")
    print(f"  {df.shape[0]} orders, {df['personality_type'].nunique()} personality types")

    # Train both models
    fwd_model, fwd_le, fwd_cols, fwd_metrics = train_forward_model(df)
    rev_model, rev_le, rev_cols, rev_metrics = train_reverse_model(df)

    # -------------------------------------------
    # DEMO 1 — Forward: who walks in → what do they get?
    # -------------------------------------------
    print("\n" + "="*60)
    print("  DEMO: Forward Inference")
    print("="*60)

    test_cases = [
        dict(hour=17, weather="rainy",  personality="sunny_social",       group_size=2),
        dict(hour=9,  weather="cloudy", personality="moody_intense",      group_size=1),
        dict(hour=14, weather="sunny",  personality="chill_studious",     group_size=1),
        dict(hour=19, weather="snow",   personality="cozy_comfort",       group_size=3),
        dict(hour=8,  weather="rainy",  personality="rushed_professional", group_size=1,
             is_finals=1),
    ]

    for tc in test_cases:
        preds = predict_drink(**tc)
        top   = list(preds.keys())[0]
        prob  = list(preds.values())[0]
        desc  = VIBE_DESCRIPTIONS.get(tc["personality"], (tc["personality"],))[0]
        print(f"\n  {desc} | {tc['weather']} | {tc['hour']}:00 | group={tc['group_size']}")
        print(f"  → Top prediction: {top} ({prob*100:.0f}%)")
        print(f"    Full: { {k: f'{v*100:.0f}%' for k,v in list(preds.items())[:4]} }")

    # -------------------------------------------
    # DEMO 2 — Reverse: drink order → who are they?
    # -------------------------------------------
    print("\n" + "="*60)
    print("  DEMO: Reverse Inference (Vibe Reading)")
    print("="*60)

    orders = [
        dict(category="latte",    milk="oat",   syrup="vanilla",   size="grande",
             cold_foam=1, iced=1,  extra_shot=0, extra_hot=0, whipped_cream=0,
             hour=17, group_size=2, weather="rainy",  food_pairing=0,
             label="Iced oat vanilla latte w/ cold foam"),

        dict(category="espresso", milk="none",  syrup="none",      size="tall",
             cold_foam=0, iced=0,  extra_shot=1, extra_hot=1, whipped_cream=0,
             hour=8,  group_size=1, weather="rainy",  food_pairing=0,
             label="Double shot extra hot americano"),

        dict(category="hot_special", milk="whole", syrup="none",   size="grande",
             cold_foam=0, iced=0,  extra_shot=0, extra_hot=0, whipped_cream=1,
             hour=19, group_size=1, weather="snow",   food_pairing=1,
             label="Hot chocolate w/ whip + brownie, snow day"),

        dict(category="refresher", milk="none", syrup="none",      size="venti",
             cold_foam=0, iced=1,  extra_shot=0, extra_hot=0, whipped_cream=0,
             hour=15, group_size=3, weather="sunny",  food_pairing=0,
             label="Venti strawberry refresher, sunny, group of 3"),
    ]

    for order in orders:
        label = order.pop("label")
        probs = predict_vibe(**order)
        print(f"\n  Order: {label}")
        print(vibe_report(probs))