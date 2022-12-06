import folium
import tempfile
import pandas as pd
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
from picture_fetch import *

# sets download session state to false

for state in ['download', 'accepted']:
    if state not in st.session_state:
        st.session_state[state] = False

#
# Creates the folium map
#

col1, col2 = st.columns([7,2])

with col1:
    # draw map zoomed on france
    m = folium.Map(location=[47.0810, 4.3988], zoom_start=5.7)

    # read data on food production in France
    data = pd.read_csv('data/regions_data.csv')
    folium.Choropleth(
        geo_data='data/regions.geojson',
        data = data,
        columns= ('Regions', 'Food Production'),
        key_on='feature.properties.Region',
        legend_name="Food Production",
        ).add_to(m)

    # allow drawing on map
    Draw(
        draw_options={i:False for i in ['polygon', 'circle', 'rectangle', 'polyline', 'circlemarker']},
        export=True
        ).add_to(m)

    # get dropped points on map and return coordinates
    if not st.session_state.download:
        output = st_folium(m, width=800, height=600, returned_objects=["last_active_drawing"])

with col2:
    st.markdown(
        '''Place a pin 📍
        on the map to 
        analyse an area
        for silos.
        ''')


#
# Downloads image
#

# set true state if point selected and bbox found
if not st.session_state.download:
    try:
        bbox = draw_square(output['last_active_drawing']['geometry']['coordinates'])
        st.session_state.download = True
    except:
        st.session_state.download = False

# start if succesfully found square for image
if st.session_state.download:
    # download picture and save to temp dict
    with tempfile.TemporaryDirectory() as temp_dir:
        picture_path = download_picture(
            bbox=bbox,
            dir_name=temp_dir)

        # display image
        col3, col4 = st.columns([7,2])
        with col3:
            st.image(picture_path)

        with col4:
            st.markdown(
                '''Click yes if you
                want to analyse 
                this area.''')

            st.markdown(
                '''Otherwise, place 
                a new pin on
                the map.''')
            
            if st.button('Yes'):
                st.session_state.accepted = True

    # throw away image if user keeps scrolling
    st.session_state.download = False


#
# Apply deep learning
#

if st.session_state.accepted:
    st.markdown('We need a model now')
    st.video('https://youtu.be/E8gmARGvPlI')