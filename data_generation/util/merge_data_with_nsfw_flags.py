import os
import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description='Merge parameters with nsfw flags')
    parser.add_argument('--data_path', type=str, help='Path to parameters shards')
    parser.add_argument('--nsfw_flags_path', type=str, help='Path to nsfw flags shards')
    parser.add_argument('--output_filepath', type=str, help='Path to output file')
    return parser.parse_args()

def main():
    args = get_args()

    # Load all .parquet files from data_path and nsfw_flags_path
    if os.path.isdir(args.data_path) is False:
        data_files = [args.data_path]
    else:
        data_files = [os.path.join(args.data_path, f) for f in os.listdir(args.data_path) if f.endswith('.parquet')]
    if os.path.isdir(args.nsfw_flags_path) is False:
        nsfw_flags_files = [args.nsfw_flags_path]
    else:
        nsfw_flags_files = [os.path.join(args.nsfw_flags_path, f) for f in os.listdir(args.nsfw_flags_path) if f.endswith('.parquet')]

    print(len(data_files), 'data files found')
    print(len(nsfw_flags_files), 'nsfw flags files found')

    # Merge all data and nsfw_flags files
    data = pd.concat([pd.read_parquet(f) for f in data_files])
    nsfw_flags = pd.concat([pd.read_parquet(f) for f in nsfw_flags_files])

    # Rename filename to index
    nsfw_flags.rename(columns={'filename': 'index'}, inplace=True)
    nsfw_flags['index'] = nsfw_flags['index'].astype('int64')

    # Sort by index column to ensure that the order is the same
    if 'index' not in data.columns:
        data.rename(columns={'fname': 'index'}, inplace=True)

    data = data.sort_values(by='index')
    nsfw_flags = nsfw_flags.sort_values(by='index')

    # Print dtypes and shapes
    print('Data dtypes:', data.dtypes)
    print('NSFW flags dtypes:', nsfw_flags.dtypes)

    print('Data shape:', data.shape)
    print('NSFW flags shape:', nsfw_flags.shape)

    # Merge data with nsfw_flags
    merged = pd.merge(data, nsfw_flags, on='index')

    # Print merged dtypes and shape
    print('Merged dtypes:', merged.dtypes)
    print('Merged shape:', merged.shape)

    # Save merged to output_filepath
    merged.to_parquet(args.output_filepath)

if __name__ == '__main__':
    main()
