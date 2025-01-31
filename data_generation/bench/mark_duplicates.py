import os
import torch
import faiss
import argparse
import numpy as np
import pandas as pd
import concurrent.futures

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_filepath_embed', type=str, required=True)
    parser.add_argument('--input_filepath_df', type=str, required=True)
    parser.add_argument('--output_filepath', type=str, required=True)

    parser.add_argument('--threshold', type=float, default=0.8)
    parser.add_argument('--n_ann_return', type=int, default=5000)
    parser.add_argument('--n_part_ivf', type=int, default=100)
    parser.add_argument('--n_probe', type=int, default=32)
    parser.add_argument('--num_threads', type=int, default=16)
    return parser.parse_args()

def find_duplicates(start_idx, end_idx, I, embed, threshold):
    duplicate_samples = set()
    for sample_idx in range(start_idx, end_idx):
        for idx in I[sample_idx]:
            embed1 = embed[sample_idx]
            embed2 = embed[idx]
            cosine_sim = np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))
            if cosine_sim >= threshold and idx > sample_idx:
                duplicate_samples.add(idx)
    return duplicate_samples

def main():
    args = get_args()

    df = pd.read_parquet(args.input_filepath_df)
    embed = np.load(args.input_filepath_embed).astype(np.float32)
    embed = np.ascontiguousarray(embed)

    assert len(df) == embed.shape[0]
    print(f"Loaded: {embed.shape[0]} samples", flush=True)

    d = embed.shape[1]
    quantizer = faiss.IndexFlatIP(d)
    index = faiss.IndexIVFFlat(quantizer, d, args.n_part_ivf)
    index.verbose = True

    print("Adding vectors to index...", flush=True)
    index.train(embed)
    index.add(embed)
    index.nprobe = args.n_probe

    print("Searching...", flush=True)
    _, I = index.search(embed, args.n_ann_return)

    num_threads = args.num_threads
    chunk_size = len(I) // num_threads
    futures = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_threads) as executor:
        for i in range(num_threads):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size if i != num_threads - 1 else len(I)
            futures.append(executor.submit(find_duplicates, start_idx, end_idx, I, embed, args.threshold))

    duplicate_samples = set()
    for future in concurrent.futures.as_completed(futures):
        duplicate_samples.update(future.result())

    duplicate_samples = list(duplicate_samples)

    df['is_duplicate'] = False
    df.loc[duplicate_samples, 'is_duplicate'] = True

    os.makedirs(os.path.dirname(args.output_filepath), exist_ok=True)
    df.to_parquet(args.output_filepath)

if __name__ == '__main__':
    main()    
