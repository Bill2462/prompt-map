from .predictor import LlmInput, LlmOutput
from .processing_thread import ProcessingThreadBase
from .processing_error import ProcessingError

class ProcessingPoolFullError(Exception):
    pass

class LlmProcessingPool:
    def __init__(self, batch_size = 256):
        self.batch_size = batch_size
        self.processing_threads: list[ProcessingThreadBase] = []
        self.errors: list[ProcessingError] = []
    
    def count_free_spots(self) -> int:
        return self.batch_size - len(self.processing_threads)

    def add_processing_thread(self, data: ProcessingThreadBase):
        if len(self.processing_threads) >= self.batch_size:
            raise ProcessingPoolFullError()

        self.processing_threads.append(data)

    def get_llm_batch(self) -> list[LlmInput]:
        return [x.get_model_input() for x in self.processing_threads]

    def process_llm_outputs(self, outputs: list[LlmOutput]):
        self.errors = []
        for thread, output in zip(self.processing_threads, outputs):
            try:
                thread.process_llm_output(output)
            except ProcessingError as e:
                self.errors.append(e)

    def get_done_processing_threads(self) -> list[ProcessingThreadBase]:
        outs = [x for x in self.processing_threads if x.is_done()]
        self.processing_threads = [x for x in self.processing_threads if not x.is_done()]
        return outs
    
