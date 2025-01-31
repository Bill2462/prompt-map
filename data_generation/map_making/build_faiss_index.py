import os
import faiss
import argparse
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedding_filepath", type=str, required=True)
    parser.add_argument("--output_index_filepath", type=str, required=True)
    parser.add_argument("--n_part_ivf", type=int, default=500)
    parser.add_argument("--n_subquantizers", type=int, default=32)
    parser.add_argument("--n_bits_per_vector", type=int, default=8)
    parser.add_argument("--is_gpu", action="store_true")
    return parser.parse_args()

def main():
    args = get_args()

    embedding = np.load(args.embedding_filepath).astype("float32")
    embedding = np.ascontiguousarray(embedding)
    d = embedding.shape[1]

    quantizer = faiss.IndexFlatIP(d)
    index = faiss.IndexIVFPQ(quantizer,
                             d,
                             args.n_part_ivf,
                             args.n_subquantizers,
                             args.n_bits_per_vector)

    if args.is_gpu:
        res = faiss.StandardGpuResources()
        index = faiss.index_cpu_to_gpu(res, 0, index)
    
    index.train(embedding)
    index.add(embedding)

    os.makedirs(os.path.dirname(args.output_index_filepath), exist_ok=True)
    faiss.write_index(index, args.output_index_filepath)

if __name__ == "__main__":
    main()
