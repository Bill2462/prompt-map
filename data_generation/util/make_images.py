import io
import os
import json
import torch
import argparse
import pandas as pd
import webdataset as wds

from math import ceil
from tqdm import tqdm
from diffusers import StableDiffusionPipeline, AutoPipelineForText2Image, StableDiffusionXLPipeline, StableDiffusion3Pipeline

class DataBatcher:
    def __init__(self, data, batch_size):
        self.data = data
        self.batch_size = batch_size
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        else:
            batch = self.data[self.index:min(self.index + self.batch_size, len(self.data))]
            self.index += self.batch_size
            return batch
    
    def reset(self):
        self.index = 0
    
    def __len__(self):
        return ceil(len(self.data) / self.batch_size)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt_filepath", required=True, type=str, help="Path to .json file with prompts.")
    parser.add_argument("--output_filepath", required=True, type=str, help="Path where outputs will be saved as tar file.")
    parser.add_argument("--sd_path", required=True, type=str, help="Path to SD model.")
    parser.add_argument("--use_turbo", action="store_true", help="Use sdxl pipeline.")
    parser.add_argument("--use_xl", action="store_true", help="Use sdxl pipeline.")
    parser.add_argument("--use_sd3", action="store_true", help="Use sdxl pipeline.")
    parser.add_argument("--batch_size", default=16, type=int, help="Batch size for inference.")
    parser.add_argument("--prompt_column", default="prompt", type=str, help="Column name for prompts.")
    parser.add_argument("--use_index_column_as_filename", action="store_true", help="Use index column as filename.")
    parser.add_argument("--index_column", default="index", type=str, help="Column name for index.")
    parser.add_argument("--width", default=512, type=int, help="Width of generated images.")
    parser.add_argument("--height", default=512, type=int, help="Height of generated images.")
    parser.add_argument("--guidance_scale", default=7.5, type=float, help="Guidance scale for diffusion.")
    parser.add_argument("--num_inference_steps", default=40, type=int, help="Number of inference steps.")

    return parser.parse_args()

def get_sd_model(args):
    if args.use_xl:
        return StableDiffusionXLPipeline.from_pretrained(args.sd_path,
                                                         torch_dtype=torch.float16,
                                                         safety_checker=None).to("cuda")
    elif args.use_sd3:
        return StableDiffusion3Pipeline.from_pretrained(args.sd_path,
                                                         torch_dtype=torch.float16).to("cuda")
    if args.use_turbo:
        return AutoPipelineForText2Image.from_pretrained(args.sd_path,
                                                         torch_dtype=torch.float16,
                                                         variant="fp16").to("cuda")
    else:
        return StableDiffusionPipeline.from_pretrained(args.sd_path,
                                                       torch_dtype=torch.float16,
                                                       safety_checker=None).to("cuda")

def main():
    args = get_args()

    if args.use_index_column_as_filename:
        prompts = prompts = pd.read_parquet(args.prompt_filepath)[args.prompt_column].tolist()
        indexes = pd.read_parquet(args.prompt_filepath)[args.index_column].tolist()

        prompts = [(str(i), p) for i, p in zip(indexes, prompts)]
    else:
        prompts = pd.read_parquet(args.prompt_filepath)[args.prompt_column].tolist()

    sd_model = get_sd_model(args)

    if args.use_turbo:
        print("Using Turbo Diffusion. Setting guidance scale to 0.0 and num_inference_steps to 3.")
        args.guidance_scale = 0.0
        args.num_inference_steps = 3
    if args.use_sd3:
        print("Using SD3 Diffusion. Setting guidance scale to 7.0 and num_inference_steps to 28.")
        args.guidance_scale = 7.0
        args.num_inference_steps = 28

    batcher = DataBatcher(prompts, args.batch_size)

    os.makedirs(os.path.dirname(args.output_filepath), exist_ok=True)
    writer = wds.TarWriter(args.output_filepath)

    i = 0
    for batch in tqdm(batcher):
        if args.use_index_column_as_filename:
            prompt_batch = [p[1] for p in batch]
            index_batch = [p[0] for p in batch]   
        else:
            prompt_batch = batch
        
        with torch.no_grad():
            out = sd_model(prompt=prompt_batch,
                           num_inference_steps=args.num_inference_steps,
                           guidance_scale=args.guidance_scale,
                           width=args.width,
                           height=args.height)

            for img_idx, (p, img) in enumerate(zip(prompt_batch, out.images)):
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="WebP")

                metadata = {"prompt": p,
                            "guidance_scale": args.guidance_scale,
                            "num_inference_steps": args.num_inference_steps,
                            "width": args.width,
                            "height": args.height,
                            "sd_path": args.sd_path}

                if args.use_index_column_as_filename:
                    key = index_batch[img_idx]
                else:
                    key = i
    
                sample = {"__key__": f"{key}",
                          "webp": img_bytes.getvalue(),
                          "json": json.dumps(metadata),}
                writer.write(sample)

                i += 1

    writer.close()

if __name__ == "__main__":
    main()
