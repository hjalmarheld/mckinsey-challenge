import torch
import numpy as np


def _preprocess(img: np.ndarray):
    img = np.moveaxis(img, -1, 0)  # from [H, W, C] to [C, H, W]
    img = (img - np.min(img)) / np.ptp(img)  # linear scaling to range [0-1]
    img = np.expand_dims(img, axis=0)  # add batch dimension [B, C, H, W]
    img = img.astype(np.float32)  # typecasting to float32
    return img


def _postprocess(img: torch.tensor):
    img = torch.argmax(img, dim=1)  # perform argmax to generate 1 channel
    img = img.cpu().numpy()  # send to cpu and transform to numpy.ndarray
    img = np.squeeze(img)  # remove batch dim and channel dim -> [H, W]

    return img


def _predict(
    img,
    model,
    device,
):
    model.eval()
    img = _preprocess(img)  # preprocess image
    x = torch.from_numpy(img).to(device)  # to torch, send to device
    with torch.no_grad():
        out = model(x)  # send through model/network

    out_softmax = torch.softmax(out, dim=1)  # perform softmax on outputs
    result = _postprocess(out_softmax)
    return result


def _calcul_area(array: np.array, size: int = 256):
    inputs = array.flatten()
    nb = sum(inputs)
    if size == 128:
        return nb
    else:
        return nb * 0.25


def _group(x):
    if x < 7.98742676e01:
        return "small"
    elif x < 1.57009277e02:
        return "medium"
    elif x < 3.72352295e02:
        return "big"
    else:
        return "huge"


def final_pred(img, model, device):
    # predict mask
    mask = _predict(img, model, device)

    # calculate area of mask
    area = _calcul_area(mask)

    # group area
    category = _group(area)

    # create image where mask is black
    covered = img + np.repeat(mask[:, :, np.newaxis], 3, axis=2)
    covered[covered > 1] = 0

    return covered, area, category
