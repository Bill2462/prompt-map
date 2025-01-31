import copy
import torch

from PIL import Image
from dataclasses import dataclass
from diffusers import AutoPipelineForText2Image

@dataclass
class GenerationConfig:
    width: int = 512
    height: int = 512
    n_steps: int = 5
    num_images_per_prompt: int = 1
    
class DummySDModel:
    def __init__(self, img_path="dummy_output.jpg"):
        self.img = Image.open(img_path)
    
    def generate_img(self, prompt: str, config: GenerationConfig = GenerationConfig()) -> list[Image.Image]:
        return [copy.deepcopy(self.img).resize((config.width, config.height))] * config.num_images_per_prompt
    
class SDModel:
    def __init__(self, path):
        self.pipe = AutoPipelineForText2Image.from_pretrained(path,
                                                              torch_dtype=torch.float16,
                                                              variant="fp16").to("cuda")
    
    @torch.no_grad()
    def generate_img(self, prompt: str, config: GenerationConfig = GenerationConfig()) -> list[Image.Image]:
        out = self.pipe(prompt=prompt,
                        num_inference_steps=config.n_steps,
                        guidance_scale=0.0,
                        width=config.width,
                        height=config.height,
                        num_images_per_promp=config.num_images_per_prompt)
        
        return out.images

def get_sd_model(path, is_dummpy=False):
    if is_dummpy:
        return DummySDModel()
    else:
        return SDModel(path)
