import numpy as np

from matplotlib import cm
from skimage import color

from .visualizations import GradCAM, BackPropagation, GuidedBackPropagation
from .predict import preprocess

def _visualize(model, data, method: str, target_layer=None):
    if method == "gradcam":
        algo = GradCAM(model=model)
    elif method == "gbp":
        algo = GuidedBackPropagation(model=model)
    bp = BackPropagation(model=model)
    # preprocess data to feed into model
    data = preprocess(data).cuda()
    probs, ids = bp.forward(data)
    prob = probs[:, [0]].item()
    # visualization method
    _ = algo.forward(data)
    algo.backward(ids=ids[:, [0]])
    # get gradients
    if method == "gradcam":
        gradients = algo.generate(target_layer=target_layer)
    elif method == "gbp":
        gradients = algo.generate()
    return gradients, prob

def _GBPVisualize(gradients):
    gradients = gradients.squeeze().cpu().numpy().transpose(1, 2, 0)
    gradients -= gradients.min()
    gradients /= gradients.max()
    return (gradients * 255.0).astype(np.uint8)
    # saliency = (np.maximum(0, gradients) / gradients.max())
    # saliency = (saliency * 255.0).astype(np.uint8)
    # return color.rgb2gray(saliency)

def _GradCAMVisualize(gradients, threshold: float):
    # the return image is RGBA format
    gradients = gradients.cpu().numpy()
    print(gradients.min(), gradients.max())
    cmap = (cm.jet(gradients)[..., :3] * 255.0).astype(np.uint8)
    alpha = np.zeros(cmap.shape[:2], dtype=np.uint8)
    alpha[gradients >= threshold] = 255
    return np.dstack([cmap, alpha])

def heatmapAndProb(model, data, threshold=0.6, target_layer="features.28"):
    grads, prob = _visualize(model, data, "gradcam", target_layer)
    grads = grads[0, 0]
    return _GradCAMVisualize(grads, threshold), prob

def GBPAndProb(model, data):
    grads, prob = _visualize(model, data, "gbp")
    return _GBPVisualize(grads), prob
