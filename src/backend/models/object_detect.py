import PIL
import torch
import numpy as np
import json
import dotenv
import datetime
import matplotlib.pyplot as plt

from PIL import Image
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.transforms import functional as F


dotenv.load_dotenv()
dot_env_file = dotenv.find_dotenv()

ANNOTE_MAPPING_FILE_PATH = dotenv.get_key(dot_env_file, "ANNOTE_MAPPING_FILE_PATH")
DEBUG_LEVEL = dotenv.get_key(dot_env_file, "DEBUG_LEVEL")
VERBOSE = True if DEBUG_LEVEL == "DEBUG" else False


PRETRAINED_ODM_MODELS = [
    "maskrcnn_resnet50_fpn",
    # More models here
]


class PretrainedODM:
    def __init__(self, pretrained_model_name):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = PRETRAINED_ODM_MODELS[pretrained_model_name]
        self.model = maskrcnn_resnet50_fpn(pretrained=True).to(self.device)
        self.model.eval()
        self.idx_to_label = json.load(open(ANNOTE_MAPPING_FILE_PATH))
        self.label_to_idx = {v: k for k, v in self.idx_to_label.items()}

    def predict(self, image):
        image_tensor = F.to_tensor(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.model(image_tensor)
        return outputs

    def get_objects(self, image, threshold=0.5, verbose=VERBOSE) -> list:
        outputs = self.predict(image)
        
        detected_labels = set()
        for i in range(len(outputs[0]['scores'])):
            score = outputs[0]['scores'][i].item()
            if score < threshold:
                continue
            else:
                detected_labels.add(
                    self.idx_to_label[str(outputs[0]['labels'][i].item())])

        return list(detected_labels)

    def get_mask(self, image, detect_objects_list, threshold=0.5, verbose=VERBOSE):
        outputs = self.predict(image)
        image_np = np.array(image).copy()
        image_np.fill(0)

        try:
            detect_ids = []
            for label in detect_objects_list:
                norm_label = label.strip().lower()
                matched = next(
                    (k for k in self.label_to_idx if k.lower() == norm_label), None)
                if matched:
                    detect_ids.append(int(self.label_to_idx[matched]))
                else:
                    if verbose:
                        print(f"Label '{label}' not found in label_to_idx")
        except Exception as e:
            print(f"Error processing detect_objects_list: {e}")
            detect_ids = []

        if verbose:
            print(f"Type of image: {type(image)}, Size: {image.size}")
            print(f"To Detect objects: {detect_objects_list} → {detect_ids}")
            print(f"outputs: {type(outputs) = },\n\t {len(outputs) = }")
            print(
                f"outputs[0]: {type(outputs[0]) = },\n\t if dict keys {outputs[0].keys() if isinstance(outputs[0], dict) else 'N/A'}")
            print(
                f"outputs[0]['scores']: {type(outputs[0]['scores']) = },\n\t size if Torch Tensor: {outputs[0]['scores'].size() if isinstance(outputs[0]['scores'], torch.Tensor) else 'N/A'}")

        for idx, score in enumerate(outputs[0]['scores']):
            if score < threshold:
                continue

            label_id = outputs[0]['labels'][idx].item()
            if label_id not in detect_ids:
                continue

            mask = outputs[0]['masks'][idx, 0].mul(255).byte().cpu().numpy()
            image_np[mask > 127] = [255, 255, 255]

        if verbose:
            print(
                f"Type of image_np: {type(image_np)}, Size: {image_np.shape}")

        masked_image = Image.fromarray(image_np, mode='RGB')

        if verbose:
            print(
                f"Type of masked_image: {type(masked_image)}, Size: {masked_image.size}")
            plt.imshow(masked_image)
            plt.axis('off')
            time_as_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            plt.savefig(
                f"debug_obj_det_{time_as_str}_mask.png", bbox_inches='tight', pad_inches=0)
            plt.close()

        return masked_image


class CustomODM:
    def __init__(self, pretrained_model_name):
        pass

    def get_objects(self, image, threshold=0.5, verbose=VERBOSE) -> list:
        pass

    def get_mask(self, image, object, threshold=0.5, verbose=VERBOSE) -> PIL.Image.Image:
        pass
