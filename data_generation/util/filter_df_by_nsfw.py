import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description='Filter dataframe by nsfw')
    parser.add_argument('--data_path', type=str, help='Path to data')
    parser.add_argument('--output_filepath_nsfw', type=str, help='Path to output file')
    parser.add_argument('--output_filepath_sfw', type=str, help='Path to output file')
    return parser.parse_args()

def main():
    args = get_args()

    # Load data
    data = pd.read_parquet(args.data_path)
    print('Data shape:', data.shape)

    # Filter by nsfw
    nsfw = data[data['nsfw_flag'] == True]
    sfw = data[data['nsfw_flag'] == False]
    print('NSFW shape:', nsfw.shape)
    print('SFW shape:', sfw.shape)

    # Save to output_filepath
    nsfw.to_parquet(args.output_filepath_nsfw)
    sfw.to_parquet(args.output_filepath_sfw)

if __name__ == '__main__':
    main()
