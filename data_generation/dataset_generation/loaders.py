import pandas as pd

class SimpleDfSequentialReader:
    def __init__(self,
                 filepath: str,
                 n_repeats: int = 1,
                 shuffle: bool = False,
                 clip_size_to: bool = None):

        self.df = pd.read_parquet(filepath)

        if shuffle:
            self.df = self.df.sample(frac=1).reset_index(drop=True)

        if clip_size_to:
            self.df = self.df.head(clip_size_to)
        
        self.length = len(self.df) * n_repeats
        self.internal_idx = 0
        self.current_index = 0
        self.n_repeats = n_repeats
        self.sample_repeat_counter = 0
    
    def __len__(self):
        return self.length

    def get_sample(self) -> dict:
        if self.internal_idx >= self.length:
            raise IndexError("No more samples to read.")
        
        sample = self.df.iloc[self.internal_idx].to_dict()\

        self.sample_repeat_counter += 1
        self.current_index += 1
        if self.sample_repeat_counter == self.n_repeats:
            self.sample_repeat_counter = 0
            self.internal_idx += 1
        
        return sample

class DummyReader:
    def __init__(self, n_samples: int):
        self.n_samples = n_samples
        self.current_index = 0
    
    def __len__(self):
        return self.n_samples

    def get_sample(self) -> dict:
        if self.current_index >= self.n_samples:
            raise IndexError("No more samples to read.")

        self.current_index += 1

        return {}
