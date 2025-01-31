import os
import torch
import argparse
import open_clip
import numpy as np
import pandas as pd
from math import ceil
from tqdm import tqdm

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
    parser = argparse.ArgumentParser(description="Make image embeddings for database.")
    parser.add_argument("--input_filepath", type=str, required=True, help="Path to the parquet file")
    parser.add_argument("--column_name", type=str, required=True, help="Name of the column to process")
    parser.add_argument("--output_filepath", type=str, required=True, help="Path to the output file")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the dreamsim model")
    parser.add_argument("--model_type", type=str, default="clip", choices=["clip", "openclip"], help="Type of model")
    parser.add_argument("--device", type=str, default="cuda", help="Device to run the model on")
    parser.add_argument("--batch_size", type=int, default=2048, help="Batch size")
    parser.add_argument("--matmul_precision", type=str, default="medium", help="Matmul precision to set")
    return parser.parse_args()

def get_model(args):
    if args.model_type == "clip":
        model = open_clip.create_model("ViT-L-14",
                                       pretrained="openai",
                                       precision="fp32",
                                       device=args.device,
                                       jit=False,
                                       cache_dir=args.model_path)
        tokenizer = open_clip.get_tokenizer("ViT-L-14")

    elif args.model_type == "openclip":
        model = open_clip.create_model("ViT-bigG-14",
                                       pretrained="laion2b_s39b_b160k",
                                       precision="fp32",
                                       device=args.device,
                                       jit=False,
                                       cache_dir=args.model_path)
        tokenizer = open_clip.get_tokenizer("ViT-bigG-14")
    else:
        raise ValueError(f"Unknown model type: {args.model_type}")
    
    return model, tokenizer

def main():
    args = get_args()
    if args.matmul_precision:
        torch.set_float32_matmul_precision(args.matmul_precision)

    model, tokenizer = get_model(args)

    os.makedirs(os.path.dirname(args.output_filepath), exist_ok=True)
    
    documents = pd.read_parquet(args.input_filepath)[args.column_name].to_list()
    print(f"Number of documents: {len(documents)}")

    dl = DataBatcher(documents, args.batch_size)

    device = torch.device(args.device)

    embeddings = []

    for document_batch in tqdm(dl):
        with torch.no_grad():
            tokens = tokenizer(document_batch).to(device)
            embeds = model.encode_text(tokens, normalize=False)
        
        for e in embeds:
            embeddings.append(e.cpu().numpy())
    
    np.save(args.output_filepath, np.array(embeddings))

if __name__ == "__main__":
    main()
