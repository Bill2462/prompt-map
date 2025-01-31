import os
import argparse
import numpy as np
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser(description="Rescale points")
    parser.add_argument("--reduced_embeddings_filepath", type=str, required=True)
    parser.add_argument("--map_layers_dir", type=str, required=True)
    parser.add_argument("--output_reduced_points", type=str, required=True)
    parser.add_argument("--output_map_layers", type=str, required=True)

    return parser.parse_args()

def main():
    args = get_args()
    points = np.load(args.reduced_embeddings_filepath)

    # List all .parquet files in the map layers directory
    map_layers = [f for f in os.listdir(args.map_layers_dir) if f.endswith(".parquet")]

    # Rescale and shift the points so that they are in the range [0, 1]
    min_value = points.min(axis=0)
    max_value = points.max(axis=0)
    points = (points - min_value) / (max_value - min_value)

    # Save the rescaled points
    np.save(args.output_reduced_points, points)

    # Now rescale the map layers using the same transformation
    for layer in map_layers:
        layer_df = pd.read_parquet(os.path.join(args.map_layers_dir, layer))
        
        label_positions = np.column_stack((list(layer_df["center_x"]), list(layer_df["center_y"])))
        label_positions = (label_positions - min_value) / (max_value - min_value)

        layer_df["center_x"] = label_positions[:, 0]
        layer_df["center_y"] = label_positions[:, 1]

        layer_df.to_parquet(os.path.join(args.output_map_layers, layer))

if __name__ == "__main__":
    main()
