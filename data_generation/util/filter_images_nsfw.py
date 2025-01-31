import os
import argparse
import pandas as pd
import webdataset as wds

def get_args():
    parser = argparse.ArgumentParser(description='Filter images by nsfw')
    parser.add_argument('--input_img_path', type=str, help='Path to data', required=True)
    parser.add_argument('--output_img_path', type=str, help='Path to output file', required=True)
    parser.add_argument('--output_img_nsfw_path', type=str, help='Path to output file', required=True)
    parser.add_argument('--final_df_path', type=str, help='Path to nsfw flags', required=True)
    return parser.parse_args()

def main():
    args = get_args()
    
    os.makedirs(os.path.dirname(args.output_img_path), exist_ok=True)
    os.makedirs(os.path.dirname(args.output_img_nsfw_path), exist_ok=True)

    df_safe = pd.read_parquet(args.final_df_path)
    safe_files = set(df_safe['index'].values)
    del df_safe

    reader = wds.WebDataset(args.input_img_path)
    writer = wds.TarWriter(args.output_img_path)
    writer_nsfw = wds.TarWriter(args.output_img_nsfw_path)

    count_safe = 0
    count_removed = 0
    for sample in reader:
        idx = int(sample['__key__'])
        
        if idx in safe_files:
            writer.write(sample)
            count_safe += 1
        else:
            count_removed += 1
            writer_nsfw.write(sample)
    
    print(f"Safe: {count_safe}, Removed: {count_removed}")
    
    writer.close()
    writer_nsfw.close()
    reader.close()

if __name__ == '__main__':
    main()
