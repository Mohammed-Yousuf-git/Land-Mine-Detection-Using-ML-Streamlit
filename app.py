import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# --- Mine icon emoji and CSS for extra polish ---
st.set_page_config(page_title="Mine Detection AI", layout="centered")
memoji = "💣"
st.markdown(
    """
    <style>
    .result {background: #222E24; border-radius: 10px; color:#65FC60; font-weight: bold; padding: 1em 1.2em; margin: 1em 0;}
    .classname {color: #FFD700;}
    .mine-banner {font-size: 2.2em; font-weight: bold; text-align: center; color: #E04D01;}
    .footer {font-size: 0.9em; color: #aaa; text-align: right;}
    /* Hide Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Parameter explanations ---
SOIL_TYPE_MAP = {
    0.0: "Dry and Sandy", 0.2: "Dry and Humus", 0.4: "Dry and Limy",
    0.6: "Humid and Sandy", 0.8: "Humid and Humus", 1.0: "Humid and Limy"
}
MINE_TYPE_MAP = {
    1: "Null", 2: "Anti-Tank", 3: "Anti-personnel", 4: "Booby Trapped Anti-personnel", 5: "M14 Anti-personnel"
}

# --- Fancy Title Card ---
st.markdown('<div class="mine-banner">💣 PASSIVE MINE DETECTION & CLASSIFICATION</div>', unsafe_allow_html=True)
st.caption("Powered by Machine Learning and FLC Sensor Simulations")

# --- Parameter Info Card ---
with st.expander("🛈 DATA PARAMETERS & CLASSES"):
    st.markdown("""
| Parameter       | Description                                | Range / Classes |
|:--------------- |:-------------------------------------------|:--------------- |
| Voltage (V)     | Magnetic sensor output (normalized)        | 0.198 – 1.00    |
| Height (H)      | Sensor elevation (normalized)              | 0.0 – 1.0       |
| Soil Type (S)   | Categorical - 6 soil types                 | 0.0–1.0         |
| Mine Type (M)   | Output class                               | 1–5             |
""")
    st.markdown("**Soil Type Mapping:** " + ", ".join([f"{k} ({v})" for k,v in SOIL_TYPE_MAP.items()]))
    st.markdown("**Mine Class Mapping:**<br>" + "<br>".join([f"{k}: {v}" for k,v in MINE_TYPE_MAP.items()]), unsafe_allow_html=True)

# --- Load your data/model (replace with @st.cache_data if loading is slow) ---
df = pd.read_csv("Mine_Dataset.csv").dropna().drop_duplicates()
X = df[["V", "H", "S"]]
y = df["M"].astype(int)
model = RandomForestClassifier(random_state=42)
model.fit(X, y)

v_min, v_max = float(df["V"].min()), float(df["V"].max())
h_min, h_max = float(df["H"].min()), float(df["H"].max())
soil_options = sorted(df["S"].unique())

st.markdown("<hr>", unsafe_allow_html=True)

# --- Input Section with custom labels/icons ---
with st.container():
    st.subheader("🎛️ Enter Sensor Measurements")
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        voltage = st.slider("Voltage (V)", v_min, v_max, (v_min+v_max)/2, 0.0001, format="%.4f")
        st.caption("🧲 Sensor magnetic response")
    with c2:
        height = st.slider("Height (H)", h_min, h_max, (h_min+h_max)/2, 0.0001, format="%.4f")
        st.caption("↕️ Height above ground")
    with c3:
        soil_key = st.selectbox("Soil Type", options=soil_options, format_func=lambda x: SOIL_TYPE_MAP[x])
        st.caption("🌱 Moisture/soil condition")

    st.markdown("")

    # --- Prediction Button ---
    predict = st.button("🔍 Detect Mine")
    if predict:
        input_row = np.array([[voltage, height, soil_key]])
        out_of_range = (voltage < v_min or voltage > v_max or height < h_min or height > h_max or soil_key not in soil_options)
        if out_of_range:
            st.warning("⚠️ Some input values are out of training range — prediction may be less reliable.")
        pred = model.predict(input_row)[0]
        st.markdown(
            f'<div class="result">{memoji} PREDICTED MINE TYPE: '
            f'<span class="classname">{MINE_TYPE_MAP[int(pred)]} ({int(pred)})</span></div>',
            unsafe_allow_html=True
        )
    else:
        st.info("Adjust settings above and click 'Detect Mine' to predict")

st.markdown("<hr>", unsafe_allow_html=True)

# --- Optionally, show data statistics or class charts ---
with st.expander("📊 Class Distribution in Training Data"):
    st.bar_chart(df["M"].value_counts().sort_index())
    for i, ct in df["M"].value_counts().sort_index().items():
        st.write(f"{int(i)}: {MINE_TYPE_MAP[int(i)]} — {ct} samples")

st.markdown('<div class="footer">Demo App for Passive Mine Detection & Classification | 2025</div>', unsafe_allow_html=True)
