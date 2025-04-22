import pandas as pd
import streamlit as st
import pydeck as pdk

# Use st.cache_data instead of st.cache
@st.cache_data
def load_and_process_data():
    # Load pre-aggregated data
    df = pd.read_csv("avg_trips_by_hour.csv")
    return df

# Load data (using cache to speed up subsequent loads)
df = load_and_process_data()

# Filter for trips with more than 20 average trips
df_filtered = df[df["Average_Trips"] > 20]

# Ensure proper numeric conversion for latitudes and longitudes
df_filtered["LAT_Inicio_Viaje"] = pd.to_numeric(df_filtered["LAT_Inicio_Viaje"], errors="coerce")
df_filtered["LON_Inicio_Viaje"] = pd.to_numeric(df_filtered["LON_Inicio_Viaje"], errors="coerce")

# Function to map trips to a color range from light blue (low) to red (high)
def map_color(trips, min_value, max_value):
    # Normalize the value between 0 and 1
    norm_value = (trips - min_value) / (max_value - min_value)
    
    # New color scale from light blue (1, 152, 189) to red (213, 2, 85)
    light_blue = (1, 152, 189)  # RGB for light blue
    red = (213, 2, 85)         # RGB for red
    
    # Interpolate between light blue and red
    r = int(light_blue[0] * (1 - norm_value) + red[0] * norm_value)
    g = int(light_blue[1] * (1 - norm_value) + red[1] * norm_value)
    b = int(light_blue[2] * (1 - norm_value) + red[2] * norm_value)
    
    return [r, g, b, 255]  # Add alpha (255 for full opacity)

# Streamlit slider for selecting hour
hour = st.slider("Select Hour", 0, 23, 12)

# Filter data based on the selected hour
df_hour = df_filtered[df_filtered["Hour"] == hour]

# Find the min and max Average_Trips values for color normalization
min_trips = df_hour["Average_Trips"].min()
max_trips = df_hour["Average_Trips"].max()

# Add a new column for the color based on Average_Trips
df_hour["color"] = df_hour["Average_Trips"].apply(lambda x: map_color(x, min_trips, max_trips))

# Set up the pydeck column layer
layer = pdk.Layer(
    "ColumnLayer",
    data=df_hour,
    get_position=["LON_Inicio_Viaje", "LAT_Inicio_Viaje"],
    get_elevation="Average_Trips",  # Height based on trips
    elevation_scale=10,  # Adjust scale for performance
    radius=100,  # Adjust radius for performance
    get_fill_color="color",  # Use the color based on the mapped scale
    pickable=True,
    auto_highlight=True,
)

# Define the initial view state (centered around Buenos Aires)
view_state = pdk.ViewState(
    latitude=-34.61,
    longitude=-58.41,
    zoom=11,  # Zoom in to reduce rendered points
    pitch=45,  # 3D angle for visual effect
)

# Create the pydeck deck
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"html": "<b>{Nombre_Inicio_Viaje}</b><br>Trips: {Average_Trips}"},
)

# Display the map with Streamlit and custom height and width
st.pydeck_chart(deck, use_container_width=True)
