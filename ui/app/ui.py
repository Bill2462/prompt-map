from .map_layer import load_all_map_layers, MapLabel, MapPoint
from .search_engine import SearchEngine
from .text_embedding_model import TextEmbeddingModelSt

from sklearn.cluster import DBSCAN

class Ui:
    def __init__(self, paths_config: str, config, text_embedding_model: TextEmbeddingModelSt):
        self.paths = paths_config
        self.config = config
        self.text_embedding_model = text_embedding_model

        self._load_map_layers()
        self._load_search_engine()

        print("Ui initialized")

    def _load_map_layers(self):
        self.map_layers = load_all_map_layers(self.paths)
        print(f"Loaded map layers: {list(self.map_layers.keys())}")
        print("Map layers loaded")
    
    def _load_search_engine(self):
        self.search_engine = SearchEngine(self.paths.search_indexes_path,
                                          self.text_embedding_model)
        print("Search engine loaded")

    def get_general_labels(self):
        df, pos = self.map_layers[f"level_3"].get_all_points()
        
        outputs = []
        for record, position in zip(df, pos):
            outputs.append(MapLabel(x = float(position[0]),
                                    y = float(position[1]),
                                    label = record["label"]))

        return outputs

    def get_detailed_labels(self,
                            origin_x_range: tuple[float, float],
                            origin_y_range: tuple[float, float],
                            level: str):
        if level == "1":
            return [] # Not implemented
        map_layer_name = f"level_{level}"

        layer = self.map_layers[map_layer_name]
        records, positions = layer.get_points_fitting_into_coordinate_range(origin_x_range,
                                                                            origin_y_range)
        return MapLabel.from_db_rows(records, positions)

    def get_map_points(self,
                       origin_x_range: tuple[float, float],
                       origin_y_range: tuple[float, float],):
        layer = self.map_layers["points"]
        records, positions = layer.get_points_fitting_into_coordinate_range(origin_x_range,
                                                                            origin_y_range)
    
        return MapPoint.from_db_rows(records, positions)
    
    def get_preview_images(self,
                        origin_x_range: tuple[float, float],
                        origin_y_range: tuple[float, float],
                        mapLevel: str):  # Changed mapLevel to int
        layer = self.map_layers["points"]

        if mapLevel == "2":
            additional_flag_filters = ["img_level_2_shown"]
        elif mapLevel == "1":
            additional_flag_filters = ["img_level_1_shown", "img_level_2_shown"]
        else:
            raise ValueError("Invalid mapLevel")

        records, positions = layer.get_points_fitting_into_coordinate_range(origin_x_range,
                                                                            origin_y_range,
                                                                            additional_flag_filters=additional_flag_filters)

        return MapPoint.from_db_rows(records, positions)

    def search_by_txt(self, index_name: str, query: str, n_points: int):
        distances, indices = self.search_engine.search_by_txt(index_name, query, n_points)
        records, positions = self.map_layers["points"].get_points_by_idx(list(indices[0]))
        return MapPoint.from_db_rows(records, positions)
