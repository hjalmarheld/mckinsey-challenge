#
# This script consists of 5 parts
#
# 1. Loading and setting states
#   - Import models
#   - Set site states 
#   - Set site configs
#
# 2. Sidebar
#   - Info
#   - Image upload
#
# 3. Map
#   - Draw map
#   - Get coordinates for download
#   - Download image
#
# 4. Image processing
#   - Download image from map OR scale upload
#   - Convert to array
#   - Display image
#   - Await confirmation for modelling
#
# 5. Modeling
#   - Download image from map OR scale upload
#   - Convert to array
#   - Display image
#   - Await confirmation for modelling
#

import config
import torch
import tempfile
import streamlit as st
import tensorflow as tf
from tensorflow import keras
from keras.utils import array_to_img
from picture_fetch import *
from models.unet_model import UNet
from models.map_utils import final_pred
from streamlit_folium import st_folium


# 1. Loading and setting states
# ------------------------------

# load keras classification model
model = keras.models.load_model(config.keras_model)

# import torch mppaing architechture
mapping_model = UNet(
    in_channels=3,
    out_channels=2,
    n_blocks=4,
    start_filters=32,
    activation="relu",
    normalization="batch",
    conv_mode="same",
    dim=2,
)

# load weights for mapping model
model_weights = torch.load(config.mapping_weights)
mapping_model.load_state_dict(model_weights)

# expand sidebar
st.set_page_config(initial_sidebar_state="expanded")

# set statefulness to negative
# - download confirms that a picture has been
#   been uploaded or downloaded via map
# 
# - accepted confirms whether a user 
#   clicks yes to analyse a picture
for state in ["download", "accepted"]:
    if state not in st.session_state:
        st.session_state[state] = False


# 2. Sidebar
# ------------------------------

st.sidebar.markdown(
    """
    # Foodix

    Use deep learning to find silos.

    Silos are essential for food storage and famine reduction.

    The interface to right allows you see to search for silos using 
    satelite pictures. Follow the steps to download a picture from anywhere in France.

    You may also upload an image of your choice below. 

    A size corresponding to 128x128 meters is recomended. 
""")

# picture upload, set state if yes
if picture_path := st.sidebar.file_uploader(label=""):
    st.session_state.download = True


# 3. Map
# ------------------------------

col1, col2 = st.columns([7, 2])

with col1:
    # draw map zoomed on france
    m = draw_map()

    # if download=False return coordinates
    if not st.session_state.download:
        output = st_folium(
            fig=m,
            width=800,
            height=600,
            returned_objects=["last_active_drawing"]
        )
    # otherwise just diplay map
    else:
        st_folium(
            fig=m,
            width=800,
            height=600,
            returned_objects=["last_active_drawing"]
        )

with col2:
    st.markdown(
        """Place a pin 📍
        on the map to 
        analyse an area
        for silos.
        """
    )

# try setting square for picture download
# if succesful, set download=True
if not st.session_state.download:
    try:
        bbox = draw_square(
            output["last_active_drawing"]["geometry"]["coordinates"])
        st.session_state.download = True
    except:
        st.session_state.download = False


# 4. Image processing
# ------------------------------

if st.session_state.download:
    # create tempdir for image storage 
    with tempfile.TemporaryDirectory() as temp_dir:
        # if nothing uploaded, download from map
        if not picture_path:
            picture_path = download_picture(
                bbox=bbox,
                dir_name=temp_dir + "/")
        # load image to np array
        image = tf.keras.preprocessing.image.load_img(picture_path)

        # display image
        col3, col4 = st.columns([7, 2])
        with col3:
            st.image(image.resize((4000, 4000)))

        with col4:
            st.markdown(
                """Click **Yes** if you
                want to analyse 
                this area."""
            )

            st.markdown(
                """Otherwise, place 
                a new pin on
                the map or upload
                another image."""
            )

            # await confirmation
            if st.button("Yes"):
                st.session_state.accepted = True

    # throw away image and unset state if user keeps scrolling
    # on map or removes uploaded picture
    st.session_state.download = False


# 5. Modeling
# ------------------------------

if st.session_state.accepted:
    # resize to fit models
    image = image.resize((256, 256))

    # convert to np.array
    input_arr = tf.keras.preprocessing.image.img_to_array(image)

    # spinning waiter while modelling
    with st.spinner("Wait for it..."):
        # classification model
        predictions = model.predict(
            [np.array([input_arr])])[0][0]

        # mapping model
        covered, area, category = final_pred(
            img=input_arr / 255,
            model=mapping_model,
            device=torch.device("cpu"))

    col5, col6 = st.columns([7, 2])

    # show picture with overlaid map
    with col5:
        st.image(array_to_img(covered).resize((4000, 4000)))

    # show our predictions
    with col6:
        if predictions > 0.5:
            st.balloons()
            st.markdown("It's a silo ! 🌾")
            st.markdown("With silo probablity %.2f" % predictions)

            st.markdown(
                """
            We classify the silo
            storage %s, covering %.1f
            square meters.
            """
                % (category, area)
            )
        else:
            st.snow()
            st.markdown("It's not a silo ! 😞")
            st.markdown("With silo probablity %.2f" % predictions)

    if st.button("❄️"):
        st.video("https://youtu.be/E8gmARGvPlI")
    st.session_state.accepted = False
