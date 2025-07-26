import torch
import PIL
import datetime
import dotenv
from diffusers import AutoPipelineForInpainting

dotenv.load_dotenv()
dot_env_file = dotenv.find_dotenv()
DEBUG_LEVEL = dotenv.get_key(dot_env_file, "DEBUG_LEVEL")

PRETRAINED_DDPM_MODELS = [
    "runwayml/stable-diffusion-inpainting",
    "kandinsky-community/kandinsky-2-2-decoder-inpaint",
    "CompVis/stable-diffusion-v1-4",
]


class PretrainedDDPM:
    def __init__(self, pretrained_model_name=0, model_params=None):
        self.model_params = model_params
        self.model_name = PRETRAINED_DDPM_MODELS[pretrained_model_name]
        self.pipe = AutoPipelineForInpainting.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
        )
        self.pipe.enable_model_cpu_offload()
        self.pipe.to("cuda")

    def forward(self, input_image, mask_image, prompt=None):
        if prompt is None or prompt == "":
            prompt = "remove the object and fill based on environment"
        return self.pipe(
            prompt=prompt,
            image=input_image,
            mask_image=mask_image,
            num_inference_steps=50,
            guidance_scale=7.5,
        ).images[0]

    def inference(self, input_data):
        model_output = self.forward(
            input_data['image'], input_data['mask'], prompt=input_data.get('prompt', None))
        model_output = self.scale_back_to_original(
            model_output, input_data['image'])
        if DEBUG_LEVEL == "DEBUG":
            print(
                f"Model output type: {type(model_output)}, size: {model_output.size if isinstance(model_output, PIL.Image.Image) else model_output.shape}")
            time_as_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            input_data['image'].save(f"debug_ddpm_{time_as_str}_input.png")
            input_data['mask'].save(f"debug_ddpm_{time_as_str}_mask.png")
            model_output.save(f"debug_ddpm_{time_as_str}_output.png")
        return model_output

    def scale_back_to_original(self, output, img):
        if isinstance(output, PIL.Image.Image):
            return output.resize(img.size, resample=PIL.Image.LANCZOS)
        elif isinstance(output, torch.Tensor):
            return torch.nn.functional.interpolate(
                output.unsqueeze(0), size=img.size[::-1], mode='bilinear', align_corners=False
            ).squeeze(0)
        else:
            raise ValueError("Unsupported output type")


class CustomDDPM:
    def __init__(self, model_params):
        self.model_params = model_params
        # Initialize the model architecture here

    def forward(self, x):
        # Define the forward pass for the DDPM
        pass

    def train(self, train_data):
        # Implement the training loop for the DDPM
        pass

    def inference(self, input_data):
        # Implement the inference method for generating samples
        pass

    def save_model(self, filepath):
        # Save the model to the specified filepath
        pass

    def load_model(self, filepath):
        # Load the model from the specified filepath
        pass
