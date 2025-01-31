import argparse
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description='Shuffle a dataframe')
    parser.add_argument('--input_df', type=str, help='Input dataframe', required=True)
    parser.add_argument('--output_df', type=str, help='Output dataframe', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    
    df = pd.read_parquet(args.input_df)
    df = df.sample(frac=1).reset_index(drop=True)

    # Delete columns
    df = df.drop(columns=['expanded_idea_i3',
                          'expanded_idea_i2',
                          'expanded_idea_i1',
                          'general_category',
                          'n_samples_to_make',
                          'nsfw_flag'])
    df.to_parquet(args.output_df)

if __name__ == '__main__':
    main()

