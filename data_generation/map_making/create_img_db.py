import os
import lmdb
import argparse
import webdataset as wds

def get_args():
    parser = argparse.ArgumentParser(description='Create LMDB database for image dataset')
    parser.add_argument('--input', type=str, help='Path to folder with dataset')
    parser.add_argument('--output', type=str, help='Output LMDB database')
    return parser.parse_args()

def main():
    args = get_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # List tar files
    files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.endswith('.tar')]
    print(f'Found {len(files)} tar files')

    # Create LMDB database
    idx = 0
    with lmdb.open(args.output, map_size=1099511627776) as env:
        with env.begin(write=True) as txn:
            for f in files:
                print(f'Processing {f}')
                ds = wds.WebDataset(f).to_tuple("webp", "__key__")

                for sample, key in ds:
                    key = key.encode('utf-8')
                    txn.put(key, sample)
                    idx += 1
                    if idx % 100000 == 0:
                        print(f'Processed {idx} images')

    print('Done')

if __name__ == '__main__':
    main()
