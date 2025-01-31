import os
import faiss
import numpy as np
from .text_embedding_model import TextEmbeddingModel

class SearchEngine:
    def __init__(self, search_index_path, text_embedding_model):
        self.text_embedding_model = text_embedding_model
        self._load_all_faiss_indexex(search_index_path)

    def _load_all_faiss_indexex(self, path: str):
        self.indexes = {}
        for file in os.listdir(path):
            if file.endswith(".idx"):
                index_name = file.split(".")[0]
                self.indexes[index_name] = faiss.read_index(os.path.join(path, file))
        
        print(f"Loaded indexes: {list(self.indexes.keys())}")

    def search_by_txt(self, index_name: str, query: str, n_points: int):
        query_embedding = self.text_embedding_model.encode_text(query)
        index = self.indexes[index_name]
        return index.search(query_embedding, n_points)
