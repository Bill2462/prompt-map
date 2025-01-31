import io
import os
import torch
import numpy as np
import argparse
import pandas as pd
import webdataset as wds

from PIL import Image

from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from transformers import CLIPImageProcessor

class DataBatcher:
    def __init__(self, data_iter, batch_size):
        self.data_iter = iter(data_iter)
        self.batch_size = batch_size
        self.current_batch = []
        self.end_of_data = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.end_of_data:
            raise StopIteration
        
        self.current_batch = []
        try:
            for _ in range(self.batch_size):
                self.current_batch.append(next(self.data_iter))
        except StopIteration:
            self.end_of_data = True

        if not self.current_batch:
            raise StopIteration
        return self.current_batch

    def reset(self, data_iter=None):
        if data_iter is not None:
            self.data_iter = iter(data_iter)
        else:
            self.data_iter = iter(self.data_iter)
        self.current_batch = []
        self.end_of_data = False

def webp_decoder(key, value):
    if not key.endswith(".webp"):
        return None
    assert isinstance(value, bytes)
    return Image.open(io.BytesIO(value))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_filepath", type=str, required=True)   
    parser.add_argument("--output_filepath", type=str, required=True)
    parser.add_argument("--model_path", type=str, required=True)

    parser.add_argument("--device", type=str, default="cuda", help="Device to run the model on")
    parser.add_argument("--batch_size", type=int, default=2048, help="Batch size")
    parser.add_argument("--matmul_precision", type=str, default="medium", help="Matmul precision to set")
    return parser.parse_args()

def main():
    args = get_args()
    if args.matmul_precision:
        torch.set_float32_matmul_precision(args.matmul_precision)
    
    os.makedirs(os.path.dirname(args.output_filepath), exist_ok=True)

    processor = CLIPImageProcessor.from_pretrained(args.model_path)
    checker = StableDiffusionSafetyChecker.from_pretrained(args.model_path).to(args.device)

    ds = (
        wds.WebDataset(args.input_filepath)
        .decode(webp_decoder)
        .to_tuple("webp", "__key__")
    )

    all_nsfw_flags = []
    all_filenames = []

    for batch in DataBatcher(ds, args.batch_size):
        images, filenames = zip(*batch)

        checker_input = processor(images, return_tensors="pt").to(args.device).pixel_values
        fake_images = np.zeros((len(filenames), 1, 1, 1), dtype=np.float32)
        _, flags = checker.forward(checker_input, fake_images)

        all_nsfw_flags.extend(flags)
        all_filenames.extend(filenames)

        if len(all_nsfw_flags) % 64*10 == 0:
            print(f"Processed {len(all_nsfw_flags)} images", flush=True)

    df = pd.DataFrame({
        "filename": all_filenames,
        "nsfw_flag": all_nsfw_flags
    })

    df.to_parquet(args.output_filepath)

if __name__ == "__main__":
    main()
