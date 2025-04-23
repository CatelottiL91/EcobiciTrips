import pandas as pd
import streamlit as st
import pydeck as pdk

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .main {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_and_process_data():
    
    df = pd.read_csv("avg_trips_by_hour.csv")
    return df

df = load_and_process_data()

df_filtered = df[df["Average_Trips"] > 20]

df_filtered["LAT_Inicio_Viaje"] = pd.to_numeric(df_filtered["LAT_Inicio_Viaje"], errors="coerce")
df_filtered["LON_Inicio_Viaje"] = pd.to_numeric(df_filtered["LON_Inicio_Viaje"], errors="coerce")

def map_color(trips, min_value, max_value):
    
    norm_value = (trips - min_value) / (max_value - min_value)
    
    light_blue = (1, 152, 189)  
    red = (213, 2, 85)         
    
    r = int(light_blue[0] * (1 - norm_value) + red[0] * norm_value)
    g = int(light_blue[1] * (1 - norm_value) + red[1] * norm_value)
    b = int(light_blue[2] * (1 - norm_value) + red[2] * norm_value)
    
    return [r, g, b, 255]  

hour = st.slider("Select Hour", 0, 23, 12)

df_hour = df_filtered[df_filtered["Hour"] == hour]

min_trips = df_hour["Average_Trips"].min()
max_trips = df_hour["Average_Trips"].max()

df_hour["color"] = df_hour["Average_Trips"].apply(lambda x: map_color(x, min_trips, max_trips))

layer = pdk.Layer(
    "ColumnLayer",
    data=df_hour,
    get_position=["LON_Inicio_Viaje", "LAT_Inicio_Viaje"],
    get_elevation="Average_Trips",  
    elevation_scale=10,  
    radius=100,  
    get_fill_color="color",  
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=-34.6148,
    longitude=-58.4387,
    zoom=11,  
    pitch=45,  
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"html": "<b>{Nombre_Inicio_Viaje}</b><br>Trips: {Average_Trips}"},
)

st.pydeck_chart(deck, use_container_width=True, height=670)
