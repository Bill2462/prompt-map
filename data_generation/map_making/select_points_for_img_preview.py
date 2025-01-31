import pandas as pd
import numpy as np

from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class LevelImagePreviewSettings:
    n_displayed_images: int
    grid_size: float

def select_points_for_image_preview(df: pd.DataFrame,
                                    point_positions: np.ndarray,
                                    level_1_settings: LevelImagePreviewSettings,
                                    level_2_settings: LevelImagePreviewSettings):
    df["img_level_1_shown"] = False
    df["img_level_2_shown"] = False

    def assign_points(level_settings, level_column):
        # Define grid boundaries
        min_x, min_y = point_positions.min(axis=0)
        max_x, max_y = point_positions.max(axis=0)
        
        # Create a grid using the specified grid size
        x_bins = np.arange(min_x, max_x + level_settings.grid_size, level_settings.grid_size)
        y_bins = np.arange(min_y, max_y + level_settings.grid_size, level_settings.grid_size)
        
        # Digitize the positions to find which grid square each point falls into
        x_indices = np.digitize(point_positions[:, 0], x_bins) - 1
        y_indices = np.digitize(point_positions[:, 1], y_bins) - 1
        
        # Combine the x and y indices to create a unique identifier for each grid square
        grid_indices = x_indices * len(y_bins) + y_indices
        
        # Iterate over unique grid squares and select points
        for grid_id in tqdm(np.unique(grid_indices)):
            grid_mask = grid_indices == grid_id
            points_in_grid = np.where(grid_mask)[0]
            
            # Randomly select up to n_displayed_images points in this grid square
            if len(points_in_grid) > 0:
                selected_indices = np.random.choice(points_in_grid,
                                                    size=min(level_settings.n_displayed_images, len(points_in_grid)),
                                                    replace=False)
                df.loc[selected_indices, level_column] = True

    # Apply selection for each level
    assign_points(level_1_settings, "img_level_1_shown")
    assign_points(level_2_settings, "img_level_2_shown")


INPUT_FILEPATH_DF = "/datadir/ui_data/db.parquet"
INPUT_FILEPATH_POINT_POSITIONS = "/datadir/ui_data/point_positions.npy"
OUTPUT_FILEPATH_DF = "/datadir/ui_data/db.parquet"

FRAC_POINTS_TO_SHOW = 0.2

df = pd.read_parquet(INPUT_FILEPATH_DF)
point_positions = np.load(INPUT_FILEPATH_POINT_POSITIONS)

df["return_this_point"] = np.random.choice([True, False],
                                                size = len(df),
                                                p = [FRAC_POINTS_TO_SHOW,
                                                1 - FRAC_POINTS_TO_SHOW])

# Create level settings
level_1_settings = LevelImagePreviewSettings(
    n_displayed_images=1,
    grid_size=0.0005
)
level_2_settings = LevelImagePreviewSettings(
    n_displayed_images=1,
    grid_size=0.006
)

# Select points for image preview
select_points_for_image_preview(df,
                                point_positions,
                                level_1_settings,
                                level_2_settings)

df.to_parquet(OUTPUT_FILEPATH_DF)
