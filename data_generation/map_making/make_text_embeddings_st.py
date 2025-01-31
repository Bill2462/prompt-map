import os
import torch
import argparse
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer

def get_args():
    parser = argparse.ArgumentParser(description="Make image embeddings for database.")
    parser.add_argument("--input_filepath", type=str, required=True, help="Path to the parquet file")
    parser.add_argument("--column_name", type=str, required=True, help="Name of the column to process")
    parser.add_argument("--output_filepath", type=str, required=True, help="Path to the output file")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the model path.")
    parser.add_argument("--device", type=str, default="cuda", help="Device to run the model on")
    parser.add_argument("--batch_size", type=int, default=2048, help="Batch size")
    parser.add_argument("--matmul_precision", type=str, default="medium", help="Matmul precision to set")
    return parser.parse_args()

def main():
    args = get_args()
    
    if args.matmul_precision:
        torch.set_float32_matmul_precision(args.matmul_precision)

    os.makedirs(os.path.dirname(args.output_filepath), exist_ok=True)
    
    documents = pd.read_parquet(args.input_filepath)[args.column_name].to_list()

    model = SentenceTransformer(args.model_path, device=args.device)

    embeddings = model.encode(documents, batch_size=args.batch_size)

    np.save(args.output_filepath, embeddings)

if __name__ == "__main__":
    main()
