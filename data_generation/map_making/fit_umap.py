import os
import umap
import joblib
import argparse
import numpy as np
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description='Fit UMAP to data')
    parser.add_argument('--data', type=str, required=True, help='Path to data')
    parser.add_argument('--output', type=str, help='Path to save UMAP model')
    parser.add_argument('--data_df', type=str, required=True)
    parser.add_argument('--data_column', type=str, required=True)
    parser.add_argument('--n_neighbors', type=int, default=80, help='Number of neighbors for UMAP')
    parser.add_argument('--min_dist', type=float, default=0.1, help='Minimum distance for UMAP')
    parser.add_argument('--n_components', type=int, default=2, help='Number of components for UMAP')
    parser.add_argument('--metric', type=str, default='cosine', help='Metric for UMAP')
    parser.add_argument("--max_n_samples", type=int, default=5000000, help="Maximum number of samples to use")
    return parser.parse_args()

def main():
    args = get_args()

    col = pd.read_parquet(args.data_df)[args.data_column]

    # Get indexes of samples that are not duplicates
    unique_sample_idx = col.drop_duplicates().index

    embeddings = np.load(args.data)
    clean_embeddings = embeddings[unique_sample_idx]
    del col

    if clean_embeddings.shape[0] > args.max_n_samples:
        # Randomly sample n samples
        print(f"Sampling {args.max_n_samples} samples from {clean_embeddings.shape[0]} samples", flush=True)
        idx = np.random.choice(clean_embeddings.shape[0], args.max_n_samples, replace=False)
        clean_embeddings = clean_embeddings[idx]

    print(f"loaded: {embeddings.shape[0]}, used to fit umap: {clean_embeddings.shape[0]}", flush=True)

    reducer = umap.UMAP(n_neighbors=args.n_neighbors,
                        min_dist=args.min_dist,
                        n_components=args.n_components,
                        metric=args.metric,
                        verbose=True)
    
    reducer.fit(clean_embeddings)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    joblib.dump(reducer, args.output, compress=3)

    print('UMAP model saved to', args.output)


if __name__ == '__main__':
    main()
