import os
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    return parser.parse_args()

def make_curve(vals):
    vals = ~vals
    return np.cumsum(vals)

def main():
    args = get_args()

    filepaths = glob.glob(os.path.join(args.input_dir, "*.parquet"))
    filepaths.sort()

    subject_curves = {}
    location_curves = {}
    for filepath in filepaths:
        fname = os.path.basename(filepath)
        fname = os.path.splitext(fname)[0]
        
        df = pd.read_parquet(filepath)
        location_curve = make_curve(df["is_duplicate_location"])
        subject_curve = make_curve(df["is_duplicate_subject"])

        location_curves[fname] = location_curve
        subject_curves[fname] = subject_curve
    
    os.makedirs(args.output_dir, exist_ok=True)

    # Plot subject curves
    plt.figure()
    for fname, curve in subject_curves.items():
        plt.plot(curve, label=fname)
    
    plt.title("Number of unique subjects in dataset")
    plt.xlabel("Number of samples")
    plt.ylabel("Number of unique samples")
    plt.legend()
    plt.savefig(os.path.join(args.output_dir, "subject_curves.png"))
    plt.close()

    # Plot location curves
    plt.figure()
    for fname, curve in location_curves.items():
        plt.plot(curve, label=fname)
    
    plt.title("Number of unique locations in dataset")
    plt.xlabel("Number of samples")
    plt.ylabel("Number of unique samples")
    plt.legend()
    plt.savefig(os.path.join(args.output_dir, "location_curves.png"))

if __name__ == '__main__':
    main()
