import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json

class TorchvisionRCNN() :
    def __init__(self, model_name='maskrcnn_resnet50_fpn', device='cuda'):
        self.device = device
        self.model = maskrcnn_resnet50_fpn(pretrained=True).to(self.device)
        self.model.eval()
        self.idx_to_label = json.load(open("annotations/coco_category_mapping.json"))
        self.label_to_idx = {v: k for k, v in self.idx_to_label.items()}

    def predict(self, image):
        image_tensor = F.to_tensor(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.model(image_tensor)
        return outputs  
    
    def get_all_objects(self, image, outputs, threshold=0.5, image_name=None, output_path=None):
        
        fig, ax = plt.subplots(1, figsize=(12, 8))
        image_np = np.array(image).copy()
        detected_labels = set()
        ax.imshow(image_np)
        for i in range(len(outputs[0]['scores'])):
            score = outputs[0]['scores'][i].item()
            if score < threshold:
                continue
            else :
                detected_labels.add(self.idx_to_label[str(outputs[0]['labels'][i].item())])
            idx = outputs[0]['labels'][i].item()
            label = self.idx_to_label[str(idx)]
            box = outputs[0]['boxes'][i].cpu().numpy()
            x1, y1, x2, y2 = box

            # Draw bounding box
            rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                    linewidth=2, edgecolor='red', facecolor='none')
            ax.add_patch(rect)

            # Add label + score text
            ax.text(x1, y1 - 5,
                    f"Label: {label}, Score: {score:.2f}",
                    bbox=dict(facecolor='yellow', alpha=0.5),
                    fontsize=9, color='black')
        
        plt.axis('off')
        plt.title("All Detected objects")
        plt.savefig(f"{output_path}/{image_name}_all_abj.png", bbox_inches='tight')
        plt.close()
        print(f"Detected labels: {detected_labels}")
        # return detected_labels
        
    
    def get_specific_object(self, image, outputs,  detect_idx=None, threshold=0.5, image_name=None, output_path=None):
        if detect_idx is None:
            print("No specific object index provided. Saving nothing.")
            return 
        
        fig, ax = plt.subplots(1, figsize=(12, 8))
        image_np = np.array(image).copy()
        
        ax.imshow(image_np)
        for i in range(len(outputs[0]['scores'])):
            score = outputs[0]['scores'][i].item()
            if score < threshold or outputs[0]['labels'][i].item() not in detect_idx:
                continue
            
            idx = outputs[0]['labels'][i].item()
            label = self.idx_to_label[str(idx)]
            box = outputs[0]['boxes'][i].cpu().numpy()
            x1, y1, x2, y2 = box

            # Draw bounding box
            rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                    linewidth=2, edgecolor='red', facecolor='none')
            ax.add_patch(rect)

            # Add label + score text
            ax.text(x1, y1 - 5,
                    f"Label: {label}, Score: {score:.2f}",
                    bbox=dict(facecolor='yellow', alpha=0.5),
                    fontsize=9, color='black')
        
        plt.axis('off')
        plt.title("All Detected objects")
        plt.savefig(f"{output_path}/{image_name}_spec_obj.png", bbox_inches='tight')
        plt.close()

    def get_partial_masked_image(self, image, outputs, detect_idx=None, threshold=0.5, image_name=None, output_path=None):
        if detect_idx is None:
            print("No specific object index provided. Saving nothing.")
            return 
        image_np = np.array(image).copy()  # Original image as NumPy array (H, W, 3)

        # Loop through detections
        for i in range(len(outputs[0]['scores'])):
            if outputs[0]['scores'][i] > threshold and outputs[0]['labels'][i].item() in detect_idx:
                # Get binary mask for the object
                mask = outputs[0]['masks'][i, 0].mul(255).byte().cpu().numpy()
                binary_mask = mask > 127  # Convert to boolean

                # Set masked region to black
                image_np[binary_mask] = [0, 0, 0]

        # Show the edited image
        plt.figure(figsize=(10, 10))
        plt.imshow(image_np)
        plt.axis('off')
        plt.savefig(f"{output_path}/{image_name}_partial_masked_img.png", bbox_inches='tight')
        plt.close()
        
    def get_masked_image_1(self, image, outputs,  detect_idx = None, threshold=0.5, image_name=None, output_path=None):
        if detect_idx is None:
            print("No specific object index provided. Saving nothing.")
            return 
        image_np = np.array(image).copy()  # Original image as NumPy array (H, W, 3)
        image_np.fill(255)  # Set all pixels to white
        for i in range(len(outputs[0]['scores'])):
            if outputs[0]['scores'][i] > threshold and outputs[0]['labels'][i].item() in detect_idx:
                mask = outputs[0]['masks'][i, 0].mul(255).byte().cpu().numpy()
                binary_mask = mask > 127
                # set masked region to black and rest white
                image_np[binary_mask] = [0, 0, 0]
                
        plt.imshow(image_np)
        plt.axis('off')
        plt.savefig(f"{output_path}/{image_name}_masked_1.png", bbox_inches='tight', pad_inches=0)
        plt.close()
    
    def get_masked_image_2(self, image, outputs,  detect_idx = None, threshold=0.5, image_name=None, output_path=None):
        if detect_idx is None:
            print("No specific object index provided. Saving nothing.")
            return 
        image_np = np.array(image).copy()  # Original image as NumPy array (H, W, 3)
        image_np.fill(0)  # Set all pixels to white
        for i in range(len(outputs[0]['scores'])):
            if outputs[0]['scores'][i] > threshold and outputs[0]['labels'][i].item() in detect_idx:
                mask = outputs[0]['masks'][i, 0].mul(255).byte().cpu().numpy()
                binary_mask = mask > 127
                # set masked region to black and rest white
                image_np[binary_mask] = [255, 255, 255]
                
        plt.imshow(image_np)
        plt.axis('off')
        plt.savefig(f"{output_path}/{image_name}_masked_2.png", bbox_inches='tight', pad_inches=0)
        plt.close()

    def get_masked_image(self, image, detect_label=['bed'], threshold=0.5, image_name = None, output_path=None):
        
        detect_idx = [int(self.label_to_idx[label]) for label in detect_label if label in self.label_to_idx]

        # detect_idx = int(self.label_to_idx[detect_label])
        
        # image_tensor = F.to_tensor(image).unsqueeze(0)
        outputs = self.predict(image)

        for label in detect_label:
            if label not in self.label_to_idx:
                print(f"Label '{label}' not found in the mapping.")
            else :
                detect_idx.append(int(self.label_to_idx[label]))
            
        # detected_labels = self.get_all_objects(image, outputs, threshold) 
        print(f"Detected labels: {detect_label}")
        self.get_all_objects(image, outputs, threshold, image_name, output_path) 
        print(f"Detecting specific objects: {detect_label}")
        self.get_specific_object(image, outputs, detect_idx, threshold, image_name, output_path)
        print(f"Getting partial masked image for: {detect_label}")
        self.get_partial_masked_image(image, outputs, detect_idx, threshold, image_name, output_path)
        print(f"Getting masked image 1 for: {detect_label}")
        self.get_masked_image_1(image, outputs, detect_idx, threshold, image_name, output_path)
        print(f"Getting masked image 2 for: {detect_label}")
        self.get_masked_image_2(image, outputs, detect_idx, threshold, image_name, output_path)

        

        


        
