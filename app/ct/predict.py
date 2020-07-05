import torch
import numpy as np

from torch.nn import Softmax
from torch.autograd import Variable
from torchvision.transforms import Resize

from app.ct.gradcam import GradCam, heatmap

def _preprocess(data):
    data = data - np.mean(data)
    data = data / (np.std(data) + 1e-5)
    data *= 0.1
    data += 0.5
    data = np.clip(data, 0, 1)
    data = np.uint8(data * 255)
    data = Resize(size=(64, 64))(data)
    tensor = torch.Tensor(data).float()
    tensor = torch.stack((tensor, tensor, tensor))
    return tensor.unsqueeze(0)

def predict(model, data):
    model.cuda()
    tensor = _preprocess(data).cuda()
    softmax = Softmax()
    output = model(tensor)
    output = softmax(output)
    return output

def getCAM(model, data):
    model.cuda()
    gradcam = GradCam(model=model, feature_module=model.features, target_layer_names=["28"], use_cuda=True)
    return gradcam(_preprocess(data).cuda(), 0)
