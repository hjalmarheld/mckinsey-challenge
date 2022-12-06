import folium
import time
import tempfile
import pandas as pd
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import st_folium
from picture_fetch import *

for state in ["download", "accepted"]:
    if state not in st.session_state:
        st.session_state[state] = False

st.sidebar.markdown('''
    # Foodix

    Use deep learning to find silos.

    Silos are essential for food storage and famine reduction.

    The interface to right allows you see to search for silos using 
    satelite pictures. Follow the steps to download a picture from anywhere in France.

    You may also upload an image of your choice below. 

    A size corresponding to 128x128 meters is recomended. 
''')

if picture_path:=st.sidebar.file_uploader(label=''):
    st.session_state.download=True

#
# Creates the folium map
#

col1, col2 = st.columns([7, 2])

with col1:
    # draw map zoomed on france
    m = folium.Map(location=[47.0810, 4.3988], zoom_start=5.7)

    # read data on food production in France
    data = pd.read_csv("data/regions_data.csv")
    folium.Choropleth(
        geo_data="data/regions.geojson",
        data=data,
        columns=("Regions", "Food Production"),
        key_on="feature.properties.Region",
        legend_name="Food Index",
    ).add_to(m)

    # allow drawing on map
    Draw(
        draw_options={
            i: False
            for i in ["polygon", "circle", "rectangle", "polyline", "circlemarker"]
        },
        export=True,
    ).add_to(m)

    # get dropped points on map and return coordinates
    if not st.session_state.download:
        output = st_folium(
            m, width=800, height=600, returned_objects=["last_active_drawing"]
        )
    else:
        st_folium(
            m, width=800, height=600, returned_objects=["last_active_drawing"]
        )

with col2:
    st.markdown(
        """Place a pin 📍
        on the map to 
        analyse an area
        for silos.
        """
    )


#
# Downloads image
#

# set true state if point selected and bbox found
if not st.session_state.download:
    try:
        bbox = draw_square(output["last_active_drawing"]["geometry"]["coordinates"])
        st.session_state.download = True
    except:
        st.session_state.download = False

# start if succesfully found square for image
if st.session_state.download:
    # download picture and save to temp dict
    with tempfile.TemporaryDirectory() as temp_dir:
        if not picture_path:
            picture_path = download_picture(bbox=bbox, dir_name=temp_dir + "/")
        image_array = load_image(picture_path=picture_path)

        # display image
        col3, col4 = st.columns([7, 2])
        with col3:
            st.image(picture_path)

        with col4:
            st.markdown(
                """Click yes if you
                want to analyse 
                this area."""
            )

            st.markdown(
                """Otherwise, place 
                a new pin on
                the map or upload
                another image."""
            )

            if st.button("Yes"):
                st.session_state.accepted = True

    # throw away image if user keeps scrolling
    st.session_state.download = False


#
# Apply deep learning
#

if st.session_state.accepted:
    print(image_array.shape)
    with st.spinner('Wait for it...'):
        time.sleep(5)
    st.balloons()
    st.markdown("We need a model now")
    st.video("https://youtu.be/E8gmARGvPlI")
    st.session_state.accepted = False
