import argparse
import numpy as np
import pandas as pd

from scipy.spatial import distance_matrix

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_df", type=str, required=True)
    parser.add_argument("--output_df", type=str, required=True)
    parser.add_argument("--fraction_level_1", type=float, default=0.03)
    
    return parser.parse_args()

def select_closest_points_until_set_count(positions: np.array, n_points: int) -> list[int]:
    # Check if n_points is valid
    assert n_points <= len(positions), "n_points must be less than or equal to the number of input points"
    
    # Initialize a list to store the indices of removed points
    selected_idxs = []
    
    # Initialize remaining points indices
    remaining_idxs = list(range(len(positions)))
    
    # Compute the distance matrix once
    dists = distance_matrix(positions, positions)
    
    # Set diagonal to infinity to avoid self-pairing
    np.fill_diagonal(dists, np.inf)
    
    # Continue removing points until the desired number of points is reached
    while len(remaining_idxs) > n_points:
        # Find the index of the minimum distance (closest pair)
        i, j = np.unravel_index(np.argmin(dists), dists.shape)
        
        # Add the second point (j) to the list of removed indices
        selected_idxs.append(j)
        
        # Remove point j from the remaining_idxs list
        remaining_idxs.remove(j)

        # Set distances for the removed point j to infinity so it's no longer considered
        dists[j, :] = np.inf
        dists[:, j] = np.inf
    
    return selected_idxs

def main():
    args = get_args()
    
    df = pd.read_parquet(args.input_df)
    positions = np.stack([df["x"].values, df["y"].values], axis=1)

    # Compute the number of points to keep in level 1
    n_points_level_1 = int(len(positions) * args.fraction_level_1)

    # Remove the closest points until the desired number of points is reached
    removed_idxs = select_closest_points_until_set_count(positions, n_points_level_1)
    
    df["level"] = 1
    df.loc[removed_idxs, "level"] = 2

    print(df["level"].value_counts())

    df.to_parquet(args.output_df)

if __name__ == "__main__":
    main()
