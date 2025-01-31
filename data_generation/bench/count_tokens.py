import argparse
import open_clip
import numpy as np
import pandas as pd

from tqdm import tqdm

def get_args():
    parser = argparse.ArgumentParser(description="Make image embeddings for database.")
    parser.add_argument("--input_filepath", type=str, required=True, help="Path to the parquet file")
    parser.add_argument("--column_name", type=str, required=True, help="Name of the column to process")
    parser.add_argument("--output_filepath", type=str, required=True, help="Path to the output file")

    parser.add_argument("--n_samples", type=int, default=1000000, help="Number of samples to process")

    return parser.parse_args()

def main():
    args = get_args()

    tokenizer = open_clip.get_tokenizer("ViT-L-14")

    df = pd.read_parquet(args.input_filepath)
    df = df.sample(n=args.n_samples)
    samples = df[args.column_name].tolist()
    del df

    token_counts = []
    for sample in tqdm(samples):
        tokens = tokenizer(sample).flatten()
        tokens = tokens[tokens != 0]
        token_counts.append(len(tokens))
    
    print(f"Average number of tokens: {np.mean(token_counts)}")
    print(f"Max number of tokens: {np.max(token_counts)}")

    np.save(args.output_filepath, token_counts)

if __name__ == "__main__":
    main()
