import json
from dataclasses import dataclass

@dataclass
class Paths:
    sd_path: str
    clip_model_path: str
    sentence_transformer_model_path: str
    
    main_db_path: str
    diffusion_db_path: str

    diffusion_db_search_index_path: str

    search_indexes_path: str
    point_positions_path: str
    map_path: str

    main_img_db_path: str
    diffusiondb_img_db_path: str

    logdir: str
    final_logdir: str

    @staticmethod
    def from_json(json_path: str):
        with open(json_path, 'r') as f:
            data = json.load(f)

        return Paths(**data)

@dataclass
class AppConfig:
    use_dummy_sd_model: bool
    condition: str
    
    @staticmethod
    def from_json(json_path: str):
        with open(json_path, 'r') as f:
            data = json.load(f)

        return AppConfig(**data)
