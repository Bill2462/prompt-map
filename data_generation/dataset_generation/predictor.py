from dataclasses import dataclass
from vllm import LLM, SamplingParams

@dataclass
class LlmInput:
    prompt: str
    sampling_parameters: SamplingParams
    input_id: int = None

@dataclass
class LlmOutput:
    output: str
    input_id: int = None
    input_prompt: str = None

class LLMPredictor:
    def __init__(self, 
                 model_path: str,
                 vllm_args: dict = {}):
    
        self.llm = LLM(model=model_path, **vllm_args)
    
    def __call__(self, batch: list[LlmInput]) -> list[LlmOutput]:
        inputs = [inp.prompt for inp in batch]
        input_ids = [inp.input_id for inp in batch]
        sampling_parameters = batch[0].sampling_parameters
        
        lmm_outs = self.llm.generate(prompts = inputs,
                                     sampling_params = sampling_parameters,
                                     use_tqdm = False)

        outputs = []
        for input_id, input_prompt, llm_out in zip(input_ids, inputs, lmm_outs):
            for x in llm_out.outputs:
                generated_text = x.text
                outputs.append(LlmOutput(input_id = input_id,
                                         input_prompt = input_prompt,
                                         output = str(generated_text)))

        return outputs
