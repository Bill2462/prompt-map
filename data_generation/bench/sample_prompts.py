import os
import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_filepath', type=str, required=True)
    parser.add_argument('--output_filepath', type=str, required=True)
    parser.add_argument('--max_samples', type=int, default=50000)

    return parser.parse_args()

def main():
    args = get_args()

    if args.input_filepath.endswith('.csv'):
        df = pd.read_csv(args.input_filepath, sep='\t')
    elif args.input_filepath.endswith('.parquet'):
        df = pd.read_parquet(args.input_filepath)
    else:
        raise ValueError("Input file must be a CSV or parquet file")

    df = df.sample(n=args.max_samples)

    os.makedirs(os.path.dirname(args.output_filepath), exist_ok=True)
    df.to_parquet(args.output_filepath)

if __name__ == "__main__":
    main()
    