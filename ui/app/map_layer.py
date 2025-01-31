import os
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass
from scipy.spatial.distance import pdist, squareform

from .configs import Paths
from tqdm import tqdm

@dataclass
class MapLabel:
    x: float
    y: float
    
    label: str

    def to_dict(self):
        return {"x": float(self.x),
                "y": float(self.y),
                "data": {"label": str(self.label)}}
    
    @staticmethod
    def from_db_rows(rows: list[dict], positions: np.ndarray):
        labels = []
        for row in rows:
            labels.append(MapLabel(x = row["x"],
                                   y = row["y"],
                                   label = row["label"]))
        return labels

@dataclass
class MapPoint:
    x: float
    y: float

    id: str
    
    prompt: str
    location: str
    subject: str

    lighting: str
    mood: str
    tone: str
    genre: str

    img_level_1_shown: bool
    img_level_2_shown: bool

    def to_dict(self):
        return {"x": float(self.x),
                "y": float(self.y),
                "id": int(self.id),
                "img_level_1_shown": self.img_level_1_shown,
                "img_level_2_shown": self.img_level_2_shown,
                "data": {"prompt": str(self.prompt),
                         "location": str(self.location),
                         "subject": str(self.subject),
                         "lighting": str(self.lighting),
                         "mood": str(self.mood),
                         "tone": str(self.tone),
                         "genre": str(self.genre)}}
    
    @staticmethod
    def from_db_rows(rows: list[dict], positions: np.ndarray):
        points = []
        for row, position in zip(rows, positions):
            points.append(MapPoint(x = position[0],
                                   y = position[1],
                                   id = row["index"],
                                   img_level_1_shown = row["img_level_1_shown"],
                                   img_level_2_shown = row["img_level_2_shown"],
                                   prompt = row["caption"],
                                   location = row["location"],
                                   subject = row["subject"],
                                   lighting = row["lighting"],
                                   mood = row["mood"],
                                   tone = row["tone"],
                                   genre = row["genre"]))
        return points

class MapLayer:
    def __init__(self,
                 db,
                 point_position_filepath: str = None,
                 level: int = None):
        if isinstance(db, str):
            self.df = pd.read_parquet(db)
        else:
            self.df = db

        # If level is specified then filter the dataframe by the level
        if level:
            self.df = self.df[self.df["level"] == level]

        if point_position_filepath:
            self.point_positions = np.load(point_position_filepath)
        else:
            self.point_positions = np.column_stack((list(self.df["x"]),
                                                    list(self.df["y"])))

        # Fucking piece of shit opencv has swapped axis, AAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        if level is None:
            self.point_positions = self.point_positions[:, [1, 0]]
            self.point_positions = self.point_positions - np.min(self.point_positions, axis=0)
            self.point_positions = self.point_positions / np.max(self.point_positions, axis=0)
        
        if "return_this_point" not in self.df.columns:
            self.df["return_this_point"] = True

    def get_points_fitting_into_coordinate_range(self,
                                                x_range: tuple[float, float],
                                                y_range: tuple[float, float],
                                                additional_flag_filters: list[str] = None):
        x_min, x_max = x_range
        y_min, y_max = y_range
        positions = self.point_positions

        # Create a boolean mask for the flags if any additional flag filters are provided
        if additional_flag_filters:
            combined_flag_filter = self.df[additional_flag_filters].any(axis=1)
        else:
            combined_flag_filter = True  # No additional flags, so the filter is just True

        # Add the "return_this_point" filter
        combined_filter = combined_flag_filter & self.df["return_this_point"]

        # Apply the combined filter first
        filtered_df = self.df[combined_filter]
        filtered_positions = positions[combined_filter.values]

        # Now filter by x and y ranges
        x_idxs = np.where((filtered_positions[:, 0] >= x_min) & (filtered_positions[:, 0] <= x_max))[0]
        y_idxs = np.where((filtered_positions[:, 1] >= y_min) & (filtered_positions[:, 1] <= y_max))[0]

        idxs = np.intersect1d(x_idxs, y_idxs)

        return filtered_df.iloc[idxs].to_dict(orient="records"), filtered_positions[idxs]
    
    def get_all_points(self):
        return self.df.to_dict(orient="records"), self.point_positions
    
    def get_points_by_idx(self, idxs: list[int]):
        return self.df.iloc[idxs].to_dict(orient="records"), self.point_positions[idxs]

def load_all_map_layers(paths: Paths) -> dict[str, MapLayer]:
    map_layers = {
        "level_3": MapLayer(db = paths.map_path, level=1),
        "level_2": MapLayer(db = paths.map_path, level=2),
    }

    map_layers["points"] = MapLayer(db = pd.read_parquet(paths.main_db_path),
                                    point_position_filepath = paths.point_positions_path)
    
    return map_layers
