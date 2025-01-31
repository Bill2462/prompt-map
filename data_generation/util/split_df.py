import os
import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description='Sp[lit the dataframe into n parts.')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to the parquet file.')
    
    parser.add_argument('-n', '--n_parts', type=int, required=True,
                        help='Name of the column containing the text entries.')

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Path to the output directory.')
    
    parser.add_argument('--max_n_samples', type=int,
                        help='Maximum number of samples to process.')
    
    return parser.parse_args()

def main():
    args = get_args()

    df = pd.read_parquet(args.input)

    print(f'Loaded {len(df)} samples.', flush=True)

    if args.max_n_samples:
        if args.max_n_samples < len(df):
            df = df.sample(args.max_n_samples).reset_index(drop=True)

    os.makedirs(args.output, exist_ok=True)

    n = args.n_parts

    target_n_samples_per_part = len(df) // n
    for i in range(n):
        start = i * target_n_samples_per_part
        end = (i + 1) * target_n_samples_per_part

        # For last part, we need to include the remaining samples
        if i == n - 1:
            end = len(df)

        df_part = df.iloc[start:end]
        df_part.to_parquet(os.path.join(args.output, f'{i}.parquet'))
    
if __name__ == '__main__':
    main()
