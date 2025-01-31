import torch
import open_clip
import numpy as np

from sentence_transformers import SentenceTransformer

class TextEmbeddingModel:
    def __init__(self, model_path: str, device: str):
        pass

    def encode_text(self, text: str) -> np.ndarray:
        pass

class TextEmbeddingModelClip:
    def __init__(self, model_path: str, device: str):
        self.device = device

        self.model = open_clip.create_model("ViT-L-14",
                                pretrained="openai",
                                precision="fp32",
                                device=device,
                                jit=False,
                                cache_dir=model_path)

        self.tokenizer = open_clip.get_tokenizer("ViT-L-14")

    @torch.no_grad()
    def encode_text(self, text: str) -> np.ndarray:
        tokens = self.tokenizer([text]).to(self.device)
        embeds = self.model.encode_text(tokens, normalize=False)
        return embeds.cpu().numpy()

class TextEmbeddingModelSt:
    def __init__(self, model_path: str, device: str):
        self.device = device

        self.model = SentenceTransformer(model_path, device=device)
    
    def encode_text(self, text: str):
        return np.array([self.model.encode(text)])
