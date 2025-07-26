import torchvision
import torchvision.transforms as T
from PIL import Image
import torch 

# Load pretrained Faster R-CNN
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

# Example inference
image = Image.open("your_image.jpg").convert("RGB")
transform = T.Compose([T.ToTensor()])
image_tensor = transform(image).unsqueeze(0)

with torch.no_grad():
    output = model(image_tensor)[0]

# output['boxes'], output['labels'], output['scores']
