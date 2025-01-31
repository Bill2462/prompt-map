import faiss
import pandas as pd
from .text_embedding_model import TextEmbeddingModelSt

class DiffusionDb:
    def __init__(self,
                 text_embedding_model: TextEmbeddingModelSt,
                 diffusion_db_search_index_path,
                 diffusion_db_data_path):
        self.index = faiss.read_index(diffusion_db_search_index_path)
        self.df = pd.read_parquet(diffusion_db_data_path)
        self.text_embedding_model = text_embedding_model

    def search_by_txt(self, query, n_points):
        query_embedding = self.text_embedding_model.encode_text(query)
        distances, indices = self.index.search(query_embedding, n_points)
        return self.df.iloc[list(indices[0])].to_dict(orient="records")
