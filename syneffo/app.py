import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from mappings import city_map, state_map, state_city_map

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="American Housing Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
if "prediction" not in st.session_state:
    st.session_state.prediction = None

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0F172A;
    color: white;
}

.block-container {
    padding-top: 0.5rem;
}

.project-header {
    background: linear-gradient(90deg,#1E3A8A,#2563EB);
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 20px;
}

.project-title {
    font-size: 42px;
    font-weight: bold;
    color: white;
}

.project-subtitle {
    font-size: 18px;
    color: #E5E7EB;
}

.property-card {
    background: #FFFFFF;
    color: black;
    padding: 20px;
    border-radius: 15px;
    font-size: 18px;
    line-height: 1.8;
}

div.stButton > button {
    background: linear-gradient(90deg,#2563EB,#1D4ED8);
    color: white !important;
    font-size: 22px;
    font-weight: 700;
    border-radius: 16px;
    height: 70px;
    border: none;
    box-shadow: 0px 6px 20px rgba(37,99,235,0.45);
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD MODEL
# =========================
model = joblib.load("housing_model.pkl")

# =========================
# GEOCODER
# =========================
@st.cache_data
def get_coordinates(city, state):
    geolocator = Nominatim(user_agent="housing_app")
    location = geolocator.geocode(f"{city}, {state}, USA")
    if location:
        return location.latitude, location.longitude
    return None, None

# =========================
# HEADER
# =========================
st.markdown("""
<div class="project-header">
    <div class="project-title">American Housing Price Prediction</div>
    <div class="project-subtitle">
        Machine Learning Powered Real Estate Valuation Platform
    </div>
</div>
""", unsafe_allow_html=True)

st.image("house_banner.jfif", use_container_width=True)

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("Property Inputs")

beds = st.sidebar.slider("Beds", 1, 20, 3)
baths = st.sidebar.slider("Baths", 1, 20, 2)
living_space = st.sidebar.slider(
    "Living Space (sq ft)",
    100, 20000, 1500, 50
)

selected_state_name = st.sidebar.selectbox(
    "State",
    list(state_map.keys())
)

selected_state_encoded = state_map[selected_state_name]

city_ids = state_city_map[selected_state_encoded]
reverse_city_map = {v: k for k, v in city_map.items()}
city_names = [reverse_city_map[i] for i in city_ids]

selected_city_name = st.sidebar.selectbox(
    "City",
    city_names
)

selected_city_encoded = city_map[selected_city_name]

zip_density = st.sidebar.slider(
    "Zip Code Density",
    0.0, 50000.0, 5000.0, 100.0
)

median_income = st.sidebar.slider(
    "Median Household Income",
    0.0, 300000.0, 60000.0, 1000.0
)

longitude = st.sidebar.slider(
    "Longitude",
    -180.0, 180.0, -118.0, 0.01
)

# =========================
# PROPERTY DETAILS
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Property Details")
    st.markdown(f"""
    <div class="property-card">
        🛏 Beds: <b>{beds}</b><br>
        🛁 Baths: <b>{baths}</b><br>
        🏡 Living Space: <b>{living_space} sq ft</b><br>
        🌆 City: <b>{selected_city_name}</b><br>
        🗺 State: <b>{selected_state_name}</b>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.subheader("Economic Details")
    st.markdown(f"""
    <div class="property-card">
        📌 Zip Density: <b>{zip_density}</b><br>
        💰 Median Income: <b>${median_income:,.0f}</b><br>
        🌍 Longitude: <b>{longitude}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# CENTERED BUTTON
# =========================
left_col, center_col, right_col = st.columns([1, 2, 1])

predict_clicked = False

with center_col:
    predict_clicked = st.button(
        "Predict House Price",
        use_container_width=True
    )

if predict_clicked:
    input_df = pd.DataFrame([[
        beds,
        baths,
        living_space,
        selected_city_encoded,
        selected_state_encoded,
        zip_density,
        median_income,
        longitude
    ]], columns=[
        'Beds',
        'Baths',
        'Living Space',
        'City',
        'State',
        'Zip Code Density',
        'Median Household Income',
        'Longitude'
    ])

    prediction = model.predict(input_df)[0]
    st.session_state.prediction = prediction

# =========================
# OUTPUT
# =========================
if st.session_state.prediction is not None:
    prediction = st.session_state.prediction

    if prediction < 300000:
        color = "#16A34A"
        category = "BUDGET PROPERTY"
    elif prediction < 700000:
        color = "#F59E0B"
        category = "MODERATE PROPERTY"
    else:
        color = "#DC2626"
        category = "LUXURY PROPERTY"

    st.markdown(f"""
    <div style="
        background:{color};
        padding:30px;
        border-radius:20px;
        text-align:center;
        color:white;
        margin-top:20px;">
        <h2>Predicted Price</h2>
        <h1>${prediction:,.2f}</h1>
        <h3>{category}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🗺 Property Location")

    latitude, real_longitude = get_coordinates(
        selected_city_name,
        selected_state_name
    )

    if latitude is not None:
        house_map = folium.Map(
            location=[latitude, real_longitude],
            zoom_start=11
        )

        popup_text = f"""
        City: {selected_city_name}<br>
        State: {selected_state_name}<br>
        Price: ${prediction:,.0f}
        """

        folium.Marker(
            [latitude, real_longitude],
            popup=popup_text,
            tooltip=selected_city_name
        ).add_to(house_map)

        st_folium(house_map, width=1000, height=500)
    else:
        st.warning("Location not found.")

st.markdown("---")
st.caption("Built with Streamlit + Machine Learning")