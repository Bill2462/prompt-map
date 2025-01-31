import argparse
import pandas as pd 
import json

def main():
    parser = argparse.ArgumentParser(description='Export data for manual entry.')
    parser.add_argument('--input', type=str, help='Input file', default='general_categories.json')
    parser.add_argument('--output', type=str, help='Output file', default='db_initial.parquet')
    args = parser.parse_args()

    with open(args.input) as f:
        data = [json.loads(line) for line in f]
    
    df = pd.DataFrame(data)
    df.to_parquet(args.output)

if __name__ == '__main__':
    main()
