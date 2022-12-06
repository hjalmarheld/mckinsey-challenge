import folium
import tempfile
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
from picture_fetch import *


# draw map zoomed on france
m = folium.Map(location=[47.0810, 2.3988], zoom_start=6)

# allow drawing on map
Draw(
    draw_options={i:False for i in ['polygon', 'circle', 'rectangle', 'polyline', 'circlemarker']},
    export=True
    ).add_to(m)

# get dropped points on map and return coordinates
output = st_folium(m, width=800, height=600, returned_objects=["last_active_drawing"])

# set false statefulness until point selected
if "load_state" not in st.session_state:
        st.session_state.load_state = False

# keep session state if point selected
if output['last_active_drawing'] or st.session_state.load_state:

    # set state to true
    st.session_state.load_state = True

    # calculate square around point
    bbox = draw_square(output['last_active_drawing']['geometry']['coordinates'])

    # download picture
    with tempfile.TemporaryDirectory() as temp_dir:
        picture_path = download_picture(
            bbox=bbox,
            dir_name=temp_dir)

        #print(picture_path)

        st.image(picture_path)

    
