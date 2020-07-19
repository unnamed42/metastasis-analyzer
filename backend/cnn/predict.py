import cv2
import torch
import numpy as np

from os.path import join, dirname, abspath

from torch.nn import AvgPool2d
from torch.nn.functional import softmax

#from torchvision.transforms import Compose, Normalize
from albumentations import PadIfNeeded, CenterCrop, Normalize, Compose
from albumentations.pytorch.functional import img_to_tensor

from .model import get_model

def model(path: str = None):
    path = path or join(dirname(abspath(__file__)), "best_model.pt")
    model_ = get_model(num_classes=2, model_type="vgg16", mode="finetune", pretrained="tumor", model_path=path)
    # remove AdaptiveAvgPool
    model_.avgpool = AvgPool2d(1)
    return model_

def process_image(data):
    # data: H * W * 3, uint8, 0-255
    # 测试数据处理的操作
    data = cv2.resize(data, (64, 64))
    means = 0.46229809522628784
    stdevs = 0.05426296219229698
    return Compose([
        #PadIfNeeded(min_height=64, min_width=64, p=1),
        #CenterCrop(height=64, width=64, p=1),
        Normalize(mean=means, std=stdevs, p=1)
    ])(image=data)["image"]

def image_to_batch(image):
    image = img_to_tensor(image).contiguous()
    return image.unsqueeze(0) # 1 * 3 * H * W

def preprocess(data):
    return image_to_batch(process_image(data))

def predict(model, image):
    with torch.no_grad():
        # 放入cuda
        if torch.cuda.is_available():
            image = image.cuda(non_blocking=True)
        outputs = model(image) # size为[1, num_classes]
        # dim=1表示在每一行上分别做softmax,[:,1]得到是转移的概率
        prob = softmax(outputs, dim=1)[:, 1].detach().tolist()
    return prob
