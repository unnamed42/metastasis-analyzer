import math
import torch

from torch import nn
from torchvision import models

def initialize_vgg(m):
    # 预训练vgg的初始化
    # m为层
    # print(m)
    if isinstance(m, nn.Conv2d):
        n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
        m.weight.data.normal_(0, math.sqrt(2. / n))
        if m.bias is not None:
            m.bias.data.zero_()
    elif isinstance(m, nn.Linear):
        m.weight.data.normal_(0, 0.01)
        m.bias.data.zero_()

def initialize_resnet(m):
    # 预训练resnet的初始化(卷积层无bias)
    # m为层
    # print(m)
    if isinstance(m,nn.Conv2d):
        n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
        m.weight.data.normal_(0, math.sqrt(2. / n))
    elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()

# Bottleneck
class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride,
                               padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out

# for resnet
def make_layer(block, planes, blocks, stride=1):
    inplanes = 1024
    downsample = None
    if stride != 1 or inplanes != planes * block.expansion:
        downsample = nn.Sequential(
            nn.Conv2d(inplanes, planes * block.expansion,
                      kernel_size=1, stride=stride, bias=False),
            nn.BatchNorm2d(planes * block.expansion),
        )

    layers = []
    layers.append(block(inplanes, planes, stride, downsample))
    inplanes = planes * block.expansion
    for i in range(1, blocks):
        layers.append(block(inplanes, planes))

    return nn.Sequential(*layers)

def get_model(num_classes, model_type, mode="freeze", model_path=None, pretrained=False):
    """
    参数说明：
    num_classes： 分类类别数
    model_type：预训练模型类型(vgg16,vgg19,)
    mode： "freeze"和"finetune"模式，代表冻结模型还是微调模型, 默认为freeze模式
    model_path：测试时可用
    pretrained：权重加载方式
    """

    if model_type == "vgg16":
        model = models.__dict__[model_type](pretrained=pretrained)

        if mode == "freeze":
            # 将第5组卷积层前的网络参数冻结
            for i, param in enumerate(model.features.parameters()):
                if i < 20:
                    param.requires_grad = False

        # 以下是重训练的层
        model.features[24] = nn.Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        model.features[26] = nn.Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        model.features[28] = nn.Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        model.classifier[0] = nn.Linear(512 * 2 * 2, 1024)
        model.classifier[3] = nn.Linear(1024, 1024)
        model.classifier[6] = nn.Linear(1024, num_classes)
        # 为了保持和预训练vgg16一样的初始化方式，故进行新修改层的初始化
        initialize_vgg(model.features[24])
        initialize_vgg(model.features[26])
        initialize_vgg(model.features[28])
        initialize_vgg(model.classifier[0])
        initialize_vgg(model.classifier[3])
        initialize_vgg(model.classifier[6])

        # 获取测试时的模型
        if(pretrained == "tumor"):
            state = torch.load(str(model_path), map_location="cpu")
            # 去掉模型参数关键字中的module
            state = {key.replace("module.",""):value for key,value in state["model"].items()}
            # 加载模型参数
            model.load_state_dict(state)

            if torch.cuda.is_available():
                model.cuda()

            model.eval()
    elif model_type == "vgg19":
        model = models.__dict__[model_type](pretrained=pretrained)

        if mode == "freeze":
            # 将第5组卷积层前的网络参数冻结
            for i, param in enumerate(model.features.parameters()):
                if i < 24:
                    param.requires_grad = False
        # 以下是重训练的层
        model.features[28] = nn.Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        model.features[30] = nn.Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        model.features[32] = nn.Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        model.features[34] = nn.Conv2d(512, 512, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        model.classifier[0] = nn.Linear(512 * 2 * 2, 1024)
        model.classifier[3] = nn.Linear(1024, 1024)
        model.classifier[6] = nn.Linear(1024, num_classes)

        initialize_vgg(model.features[28])
        initialize_vgg(model.features[30])
        initialize_vgg(model.features[32])
        initialize_vgg(model.features[34])
        initialize_vgg(model.classifier[0])
        initialize_vgg(model.classifier[3])
        initialize_vgg(model.classifier[6])

        # 获取测试时的模型
        if(pretrained == "tumor"):
            state = torch.load(str(model_path), map_location="cpu")
            # 去掉关键字中的module
            state = {key.replace("module.",""):value for key,value in state["model"].items()}
            # 加载模型参数
            model.load_state_dict(state)

            if torch.cuda.is_available():
                model.cuda()

            model.eval()
    elif model_type == "resnet50":
        model = models.__dict__[model_type](pretrained=pretrained)

        # 设置重新训练的层（layer4的层全部重新训练）
        model.layer4 = make_layer(block=Bottleneck, planes=512, blocks=3, stride=2)
        model.avgpool = nn.AvgPool2d(2, stride=1)
        model.fc = nn.Linear(2048, 2)
        # 初始化
        for i in range(3):
            initialize_resnet(model.layer4[i].children())
    else:
        pass

    return model
