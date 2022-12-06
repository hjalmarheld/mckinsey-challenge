import urllib.request
import numpy as np
from PIL import Image


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
                lat - 0.001,
                long - 0.001,
                lat + 0.001,
                long + 0.001,
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
