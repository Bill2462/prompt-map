import os
import argparse
import pandas as pd
from glob import glob

def get_args():
    parser = argparse.ArgumentParser(description='Postprocess the columns containing text entries.')
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='Path to the directory with parquet files..')

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Path to the output parquet file.')
    
    parser.add_argument('--max_n_samples', type=int,
                        help='Maximum number of samples to process.')
    
    parser.add_argument('--add_index_as_column', action='store_true',
                        help='Add index as a column to the output dataframe.')
    
    return parser.parse_args()

def main():
    args = get_args()

    files = glob(os.path.join(args.input, '*.parquet'))
    files.sort(key=lambda x: int(x.split('/')[-1].split('.')[0]))
    dfs = [pd.read_parquet(file) for file in files]
    df = pd.concat(dfs, ignore_index=True)

    if args.add_index_as_column:
        df['index'] = list(range(len(df)))

    if args.max_n_samples:
        if args.max_n_samples < len(df):
            df = df.sample(args.max_n_samples).reset_index(drop=True)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_parquet(args.output)
    
if __name__ == '__main__':
    main()
