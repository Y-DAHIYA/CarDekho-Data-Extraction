import streamlit as st
import pickle
import pandas as pd
from datetime import datetime

# Load the stacking model
with open("stacking_model.pkl", "rb") as f:
    stacking_model = pickle.load(f)

# Load Encoders
with open("car_name_encoder.pkl", "rb") as f:
    car_name_encoder = pickle.load(f)

with open("city_encoder.pkl", "rb") as f:
    city_encoder = pickle.load(f)

with open("fuel_type_encoder.pkl", "rb") as f:
    fuel_type_encoder = pickle.load(f)

with open("ownership_encoder.pkl", "rb") as f:
    ownership_encoder = pickle.load(f)

with open("transmission_encoder.pkl", "rb") as f:
    transmission_encoder = pickle.load(f)

with open("drive_type_encoder.pkl", "rb") as f:
    drive_type_encoder = pickle.load(f)

with open("columns_order_cardekho.pkl", "rb") as f:
    columns_order_cardekho = pickle.load(f)

# ✅ Success Message
print("✅ Stacking model and encoders loaded successfully!")

# Streamlit App Title
st.title("🚗 Car Price Prediction App")
st.write("Enter the car details to predict its selling price.")

# ✅ **Initialize session state**
if "predicted_price" not in st.session_state:
    st.session_state.predicted_price = None
if "show_result" not in st.session_state:
    st.session_state.show_result = False  # Control UI behavior

# User Inputs
st.subheader("📋 Car Details")
car_name = st.selectbox("Car Name", car_name_encoder.classes_)
city = st.selectbox("City", city_encoder.classes_)
fuel_type = st.selectbox("Fuel Type", fuel_type_encoder.classes_)
ownership = st.selectbox("Ownership", ownership_encoder.classes_)
transmission = st.selectbox("Transmission Type", transmission_encoder.classes_)
drive_type = st.selectbox("Drive Type", drive_type_encoder.classes_)

manufacturing_year = st.number_input("Manufacturing Year", min_value=1980, max_value=2024, step=1)
engine = st.number_input("Engine (cc)", min_value=100, max_value=10000, step=1)
mileage = st.number_input("Mileage (kmpl)", min_value=5.0, max_value=50.0, step=0.1)
engine_power = st.number_input("Engine Power (bhp)", min_value=30, max_value=500, step=1)
seats = st.number_input("Number of Seats", min_value=2, max_value=10, step=1)
kilometers_driven = st.number_input("Kilometers Driven", min_value=100, max_value=300000, step=500)

st.divider()

# Compute Car Age
current_year = datetime.now().year
car_age = current_year - manufacturing_year

# Encode categorical inputs
car_name_encoded = car_name_encoder.transform([car_name])[0]
city_encoded = city_encoder.transform([city])[0]
fuel_type_encoded = fuel_type_encoder.transform([fuel_type])[0]
ownership_encoded = ownership_encoder.transform([ownership])[0]
transmission_encoded = transmission_encoder.transform([transmission])[0]
drive_type_encoded = drive_type_encoder.transform([drive_type])[0]

# Prepare Data for Model
input_data_dict = {
    "Car Name": [car_name_encoded],
    "City": [city_encoded],
    "Fuel Type": [fuel_type_encoded],
    "Seats": [seats],
    "Kms Driven": [kilometers_driven],
    "Ownership": [ownership_encoded],
    "Engine": [engine],  
    "Transmission": [transmission_encoded],
    "Power": [engine_power],
    "Drive Type": [drive_type_encoded],
    "Mileage": [mileage],
    "Year of Manufacture": [manufacturing_year],
    "Car Age": [car_age]
}

# Convert to DataFrame and ensure correct column order
input_data = pd.DataFrame(input_data_dict)[columns_order_cardekho]

# ✅ **Predict Price**
if st.button("Predict Price"):
    st.session_state.predicted_price = stacking_model.predict(input_data)[0]
    st.session_state.show_result = True  # Flag to control UI
    st.rerun()  # Force UI update

# ✅ **Display Prediction Result**
if st.session_state.show_result:
    st.success(f"💰 Estimated Selling Price: ₹{st.session_state.predicted_price:.2f} Lakhs")

    # ✅ **Button to Predict Again**
    if st.button("Predict Another"):
        st.session_state.predicted_price = None  # Reset
        st.session_state.show_result = False
        st.rerun()  # Reload page to show input form again
