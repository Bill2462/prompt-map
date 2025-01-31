import os
import joblib
import argparse
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_embed_filepath', type=str, required=True)
    parser.add_argument('--output_embed_filepath', type=str, required=True)
    parser.add_argument('--umap_model_filepath', type=str, required=True)
    return parser.parse_args()


def main():
    args = get_args()
    os.makedirs(os.path.dirname(args.output_embed_filepath), exist_ok=True)

    embed = np.load(args.input_embed_filepath).astype(np.float32)
    embed = np.ascontiguousarray(embed)

    umap_model = joblib.load(args.umap_model_filepath)
    umap_embed = umap_model.transform(embed)

    np.save(args.output_embed_filepath, umap_embed)
    print(f"Saved UMAP embeddings to {args.output_embed_filepath}")

if __name__ == '__main__':
    main()
