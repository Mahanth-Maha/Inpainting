import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json

from object_detection import TorchvisionRCNN 
model = TorchvisionRCNN (
    model_name="maskrcnn_resnet50_fpn",
    device = "cuda" if torch.cuda.is_available() else "cpu"
)

img_path = "egs/IMG_20250726_004406.jpg"
image = Image.open(img_path).convert("RGB")

output_path = 'outputs'
image_name = 'eg_img_2'
model.get_masked_image(image, detect_label=['keyboard', 'mouse', 'chair'], image_name=image_name, output_path=output_path)