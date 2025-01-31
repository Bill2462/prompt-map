import os
import cv2
import json
import argparse
import numpy as np
import pandas as pd
from closest_point_finding import find_n_closest_points

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_map", type=str, required=True)
    parser.add_argument("--input_point_positions", type=str, required=True)
    parser.add_argument("--input_df", type=str, required=True)
    parser.add_argument("--column_name", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)

    parser.add_argument("--n_samples_from_nn", type=int, default=30)

    parser.add_argument("--n_jobs", type=int, default=16)

    return parser.parse_args()

def find_red_blobs(image):
    B, G, R = cv2.split(image)
    
    # Create a binary mask where R == 255 and G != 255 and B != 255
    mask = (R == 255) & (G != 255) & (B != 255)
    mask = mask.astype(np.uint8) * 255  # Convert to uint8 binary mask

    # 2. Find contours (blobs)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Initialize lists to store the results
    normalized_centroids = []
    pixel_centroids = []

    # Get the size of the image
    height, width = image.shape[:2]

    # 3. Calculate the center point of each blob
    for contour in contours:
        M = cv2.moments(contour)
        if M['m00'] != 0:  # To avoid division by zero
            # Centroid in pixel coordinates
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            
            # 4. Normalize the center point (bottom-left is (0,0), top-right is (1,1))
            norm_cx = cx / width
            norm_cy = cy / height
            
            # Append results
            pixel_centroids.append((cx, cy))
            normalized_centroids.append((norm_cx, norm_cy))

    return np.array(normalized_centroids), np.array(pixel_centroids)

def main():
    args = get_args()

    map_img = cv2.imread(args.input_map)
    point_positions = np.load(args.input_point_positions)
    point_positions = point_positions[:, [1, 0]]

    # Rescale points into <0, 1> range
    point_positions = point_positions - np.min(point_positions, axis=0)
    point_positions = point_positions / np.max(point_positions, axis=0)
    
    all_annotations = pd.read_parquet(args.input_df)[args.column_name].to_list()

    # Draw red points on map_no_labels
    red_points_normalized, red_points = find_red_blobs(map_img)
    
    # Now fore each normalized red point find n_samples_from_nn closest points
    nearest_neighbors = find_n_closest_points(red_points_normalized,
                                              point_positions,
                                              args.n_samples_from_nn,
                                              args.n_jobs)
    
    outputs = []

    for nn_idxs, red_point_normalized, red_point_pixel_values in zip(nearest_neighbors, red_points_normalized, red_points):
        samples = [ all_annotations[j] for j in nn_idxs ]
        samples_str = json.dumps(samples, indent=4)
        outputs.append({
            "x": red_point_normalized[0],
            "y": red_point_normalized[1],
            "x_pixels": red_point_pixel_values[0],
            "y_pixels": red_point_pixel_values[1],
            "samples": samples_str
        })

    pd.DataFrame(outputs).to_parquet(args.output)
        
if __name__ == "__main__":
    main()
