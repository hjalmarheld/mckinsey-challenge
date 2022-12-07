import urllib.request
import numpy as np
from PIL import Image
import folium
from folium.plugins import Draw
import pandas as pd

def draw_map():
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
    return m


def draw_square(coords: list):
    """
    Function drawing a coordiante square around a given point
    """
    long = coords[0]
    lat = coords[1]

    bbox = ",".join(
        [
            str(round(cord, 6))
            for cord in [
                lat - 0.0008,
                long - 0.0008,
                lat + 0.0008,
                long + 0.0008,
            ]
        ]
    )

    return bbox


def download_picture(bbox: str, dir_name: str):
    picture_path = dir_name + "pic.jpg"

    url = "https://wxs.ign.fr/ortho/geoportail/r/wms?LAYERS=HR.ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&STYLES=&CRS=EPSG:4326&WIDTH=4000&HEIGHT=4000&BBOX="
    url += bbox
    urllib.request.urlretrieve(url, picture_path)

    return picture_path


def load_image(picture_path):
    img = Image.open(picture_path)
    img.load()
    img = img.resize((256, 256))
    data = np.asarray(img, dtype="int32")
    return data
