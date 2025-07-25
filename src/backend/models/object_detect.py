import io 
import PIL
import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json

PRETRAINED_ODM_MODELS = [
    "maskrcnn_resnet50_fpn"
]

class PretrainedODM:
    def __init__(self, pretrained_model_name):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = PRETRAINED_ODM_MODELS[pretrained_model_name]
        self.model = maskrcnn_resnet50_fpn(pretrained=True).to(self.device)
        self.model.eval()
        self.idx_to_label = json.load(open("annotations/coco_category_mapping.json"))
        self.label_to_idx = {v: k for k, v in self.idx_to_label.items()}

    def get_objects(self, image) -> list:
        # Perform inference on the input image and return the predictions
        # fig, ax = plt.subplots(1, figsize=(12, 8))
        outputs = self.predict(image)
        threshold = 0.5
        # image_np = np.array(image).copy()
        detected_labels = set()
        # ax.imshow(image_np)
        for i in range(len(outputs[0]['scores'])):
            score = outputs[0]['scores'][i].item()
            if score < threshold:
                continue
            else :
                detected_labels.add(self.idx_to_label[str(outputs[0]['labels'][i].item())])
            # idx = outputs[0]['labels'][i].item()
            # label = self.idx_to_label[str(idx)]
            # box = outputs[0]['boxes'][i].cpu().numpy()
            # x1, y1, x2, y2 = box

            # Draw bounding box
            # rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1,
            #                         linewidth=2, edgecolor='red', facecolor='none')
            # ax.add_patch(rect)

            # Add label + score text
            # ax.text(x1, y1 - 5,
            #         f"Label: {label}, Score: {score:.2f}",
            #         bbox=dict(facecolor='yellow', alpha=0.5),
            #         fontsize=9, color='black')
        
        # plt.axis('off')
        # plt.title("All Detected objects")
        # plt.savefig(f"{output_path}/{image_name}_all_abj.png", bbox_inches='tight')
        # plt.close()
        # print(f"Detected labels: {detected_labels}")
        
        return list(detected_labels)

    def get_mask(self, image, object) -> PIL.Image.Image:
        # Preprocess the image before feeding it to the model
        outputs = self.predict(image)
        threshold = 0.5
        image_np = np.array(image).copy()  # Original image as NumPy array (H, W, 3)
        image_np.fill(0)  # Set all pixels to white
        for i in range(len(outputs[0]['scores'])):
            if outputs[0]['scores'][i] > threshold and outputs[0]['labels'][i].item() in detect_idx:
                mask = outputs[0]['masks'][i, 0].mul(255).byte().cpu().numpy()
                binary_mask = mask > 127
                # set masked region to black and rest white
                image_np[binary_mask] = [255, 255, 255]
        # Convert the modified NumPy array back to a PIL Image
        # plt.imshow(image_np)
        # plt.axis('off')
        # plt.savefig(f"{output_path}/{image_name}_masked_2.png", bbox_inches='tight', pad_inches=0)
        # plt.close()

        masked_image = Image.fromarray(image_np, mode='RGB')
        return masked_image

        
