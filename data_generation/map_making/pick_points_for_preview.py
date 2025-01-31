import os
import math
import random
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_point_positions", type=str, required=True)
    parser.add_argument("--input_df", type=str, required=True)
    parser.add_argument("--output_df", type=str, required=True)

    parser.add_argument("--n_bins_level_1", type=int, default=350)
    parser.add_argument("--n_bins_level_2", type=int, default=40)
    parser.add_argument("--n_points_per_bin_level_1", type=int, default=1)
    parser.add_argument("--n_points_per_bin_level_2", type=int, default=1)
    parser.add_argument("--fraction_of_points_for_display", type=float, default=0.3)

    return parser.parse_args()

def split_points_into_bins(points, grid_size=4000):
    # Extract x and y coordinates
    x, y = points[:, 0], points[:, 1]
    
    # Compute the 2D histogram and bin edges
    hist, x_edges, y_edges = np.histogram2d(x, y, bins=grid_size, range=[[0, 1], [0, 1]])
    
    # Find the bin index for each point
    x_bin_idx = np.digitize(x, x_edges) - 1  # Find the x bin for each point
    y_bin_idx = np.digitize(y, y_edges) - 1  # Find the y bin for each point

    # Combine x and y bin indices into a single 2D bin index
    bin_idx = (x_bin_idx * grid_size) + y_bin_idx

    # Sort the points by bin index
    sorted_point_idxs = np.argsort(bin_idx)

    points_splitted = []
    current_block = []
    currentt_idx = bin_idx[sorted_point_idxs[0]]
    for idx in tqdm(sorted_point_idxs):
        if bin_idx[idx] == currentt_idx:
            current_block.append(idx)
        else:
            points_splitted.append(current_block)
            current_block = [idx]
            currentt_idx = bin_idx[idx]

    points_splitted.append(current_block)

    return points_splitted

def select_idxs_for_preview(binned_idxs_level_1, n_samples_from_bin):
    selected_points = []
    for bin_idxs in binned_idxs_level_1:
        if len(bin_idxs) == 0:
            continue

        # Randomly select n_samples_from_bin from bin_idxs
        # If there are less than n_samples_from_bin points, select all points
        random.shuffle(bin_idxs)

        if len(bin_idxs) > n_samples_from_bin:
            selected_points.extend(bin_idxs[:n_samples_from_bin])
        else:
            selected_points.extend(bin_idxs)
    
    return selected_points

def main():
    args = get_args()

    point_positions = np.load(args.input_point_positions)

    # Rescale points into <0, 1> range
    point_positions = point_positions - np.min(point_positions, axis=0)
    point_positions = point_positions / np.max(point_positions, axis=0)
    
    df = pd.read_parquet(args.input_df)

    # Sample points from bins
    print("Running binning algorithm...")
    binned_idxs_level_1 = split_points_into_bins(point_positions, grid_size=args.n_bins_level_1)
    binned_idxs_level_2 = split_points_into_bins(point_positions, grid_size=args.n_bins_level_2)

    # Select points for preview
    idx_level_1_shown = select_idxs_for_preview(binned_idxs_level_1, args.n_points_per_bin_level_1)
    idx_level_2_shown = select_idxs_for_preview(binned_idxs_level_2, args.n_points_per_bin_level_2)
    
    print(f"Number of points for level 1: {len(idx_level_1_shown)}")
    print(f"Number of points for level 2: {len(idx_level_2_shown)}")

    df["img_level_1_shown"] = False
    df["img_level_2_shown"] = False
    df["return_this_point"] = False

    # Mark points that are closest to the honeycomb pattern
    df.loc[idx_level_1_shown, "img_level_1_shown"] = True
    df.loc[idx_level_2_shown, "img_level_2_shown"] = True

    # If the level 2 is shown then do not show level 1
    df.loc[df["img_level_2_shown"], "img_level_1_shown"] = False

    # If the img_level_1_shown or img_level_2_shown is True, then return this point
    df.loc[df["img_level_1_shown"] | df["img_level_2_shown"], "return_this_point"] = True

    # For the rest of the points, randomly select fraction_of_points_for_display
    # Get the number of points to display
    num_points_to_display = int(args.fraction_of_points_for_display * len(df))

    # Get the indices of points that are not shown
    not_shown_indices = df.index[~df["return_this_point"]].tolist()

    # Randomly select num_points_to_display points
    random_indices = np.random.choice(not_shown_indices, num_points_to_display, replace=False)

    # Mark the randomly selected points
    df.loc[random_indices, "return_this_point"] = True
    
    # Save the dataframe
    df.to_parquet(args.output_df)
        
if __name__ == "__main__":
    main()
