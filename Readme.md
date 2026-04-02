# Quench Cafe · Vibe Predictor and Wrapped feature

**I worked as a barista at Quench (Center Table, University of Washington) as part time last quarter**

At some point I started noticing patterns. The person who always ordered extra hot with an extra shot. The oat milk cold foam crowd. The cold brew minimalists who never changed their order. I started wondering: *can you predict someone's personality from their drink order?*

So I tried doing that here!

---

## What's here

### 1. Vibe Predictor 

A Random Forest classifier trained on 8,083 synthetic orders, built using real Quench recipe logic and the behavioral patterns I observed across a quarter of shifts.

**Features used:** drink category, milk type, syrup, size, ice preference, extra shots, cold foam, whipped cream, food pairing, time of day.

**Result:** Approximately 60% accuracy on 6-class personality prediction — compared to 16.7% random chance. The model's strongest single signal: `extra_hot = True` → Moody Intense (~99% confidence when combined with extra shot). Oat milk + cold foam reliably predicts Sunny Social. Cold brew with no modifications predicts Chill Studious. These patterns emerged from the data — they weren't hardcoded.

**Vibe types:** Moody Intense · Sunny Social · Chill Studious · Rushed Professional · Cozy Comfort · Adventurous · The Algorithm · Main Character Energy · Chaos Agent · Silent Regular

### 2. Quench Wrapped (the product concept)

A "what if?" feature concept: what if Starbucks told you your coffee personality at the end of every year — like Spotify Wrapped, but for your orders?

This is a fully interactive mockup of what that feature could look like, built on top of the ML model.

---

## Try it

open it live: **[quench-cafe.github.io](https://124578-uw.github.io/cafe-analytics/)** 

---

## Run the data science code

```bash
# Clone and set up
git clone https://github.com/yourusername/cafe-analytics
cd cafe-analytics
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Regenerate the synthetic dataset
python generate_data.py

# Train both models
python vibe_model.py

# Run the Streamlit app (technical version)
streamlit run app.py
```

---

## File structure

```
cafe-analytics/
├── quench_app.html          # Standalone demo — open in any browser
├── generate_data.py         # Synthetic order data generator
├── vibe_model.py            # Model training (forward + reverse)
├── app.py                   # Streamlit app (technical portfolio version)
├── drink_cards.py           # SVG drink card illustrations
├── drink_images_data.py     # Drink photos as base64
├── simulate.py              # Monte Carlo demand simulation
├── data/
│   └── cafe_orders_synthetic.csv
├── models/
│   ├── reverse_model.pkl        # Drink → Personality (core model)
│   ├── reverse_label_encoder.pkl
│   ├── reverse_feature_cols.pkl
│   ├── forward_model.pkl        # Personality + Context → Drink
│   ├── forward_label_encoder.pkl
│   └── forward_feature_cols.pkl
├── notebooks/
│   └── analysis.ipynb
└── requirements.txt
```

---

## The data

8,083 synthetic orders generated across 80 days (Winter Quarter 2026: Jan–Mar). Each order includes:

- Drink category, milk, syrup, size, temperature
- Customizations: extra shot, extra hot, cold foam, whipped cream, no ice
- Context: time of day, weather, group size, day type (finals, quarter start, holiday)
- Personality type (ground truth label, one of 10 types)

Synthetic data was generated using real Quench pump/shot counts from the laminated recipe card at the bar, and behavioral distributions built from shift observations.

---

## About

**Hari haran Suresh kumar** — MS Data Science at University of Washington, Seattle.  
[LinkedIn](https://www.linkedin.com/in/hariharan-sureshkumar-engineer/) · [Email](mail to: hhsk@uw.edu)
