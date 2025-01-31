from .predictor import LlmInput, SamplingParams, LlmOutput
from .utils import fill_template_params, check_if_type_is_correct
from .processing_error import ProcessingError

import json
from typing import Any

class ProcessingThreadBase:
    def get_model_input(self) -> LlmInput:
        raise NotImplementedError()
    
    def process_llm_output(self, output: LlmOutput):
        raise NotImplementedError()
    
    def get_result(self) -> Any:
        raise NotImplementedError()
    
    def get_input_data(self) -> dict:
        return self.prompt_parameter_values
    
    def is_done(self) -> bool:
        raise NotImplementedError()
    
def postprocess_str(x: str) -> str:
    x = x.replace('_', ' ').lower()
    x = ''.join([c for c in x if ord(c) < 128])
    x = x.replace("\n", " ").strip()
    return x

class SimpleProcessingThread(ProcessingThreadBase):
    def __init__(self,
                 prompt_template: str,
                 output_checker_parameters: dict = {"output_type": "str"},
                 sampling_parameters: dict = {},
                 prompt_parameter_values: dict = None,
                 max_n_retries: int = 5):

        self.output_checker_parameters = output_checker_parameters

        self.sampling_parameters = SamplingParams(**sampling_parameters)
    
        if prompt_parameter_values:
            self.prompt = fill_template_params(prompt_template, prompt_parameter_values)
        else:
            self.prompt = prompt_template

        self.max_n_retries = max_n_retries
        self.current_try_number = 0
        
        self.prompt_parameter_values = prompt_parameter_values
        if not prompt_parameter_values:
            self.prompt_parameter_values = {}
        
        self.result = None
    
    def get_model_input(self) -> LlmInput:
        return LlmInput(prompt=self.prompt, sampling_parameters=self.sampling_parameters)
    
    def get_input_data(self) -> dict:
        return self.prompt_parameter_values

    def process_llm_output(self, out: LlmOutput):
        out_str = out.output
        self.current_try_number += 1
        if self.current_try_number >= self.max_n_retries:
            self.result = ProcessingError("Max number of retries reached", out_str)
            raise ProcessingError("Max number of retries reached", out_str)
        
        out_str = postprocess_str(out_str)

        if not self.output_checker_parameters["output_type"] == "str":
            try:
                result = json.loads(out_str)
            except Exception:
                raise ProcessingError("JSON parsing error", out)
        else:
            result = out_str
        
        # Postprocess strings
        if isinstance(result, list):
            for i, x in enumerate(result):
                if isinstance(x, str):
                    result[i] = postprocess_str(x)
        if isinstance(result, dict):
            for k, v in result.items():
                if isinstance(v, str):
                    result[k] = postprocess_str(v)
                elif isinstance(v, list) and all(isinstance(o, str) for o in v):
                    result[k] = [postprocess_str(x) for x in v]
                else:
                    raise ProcessingError("Invalid output format", out)

        try:
            check_if_type_is_correct(result, self.output_checker_parameters)
        except PermissionError as e:
            e.model_input = out.input_prompt
            raise e
        
        if isinstance(result, list):
            if "clip_at" in self.output_checker_parameters and len(result) > self.output_checker_parameters["clip_at"]:
                clip_at = self.output_checker_parameters["clip_at"]
                result = result[:clip_at]
        
        if isinstance(result, dict):
            if "clip_at" in self.output_checker_parameters:
                clip_at = self.output_checker_parameters["clip_at"]
                for k, v in result.items():
                    if isinstance(v, list):
                        if len(v) > clip_at:
                            result[k] = v[:clip_at]
        
        # Delete keys that are not in the output_checker_parameters
        if isinstance(result, dict):
            required_keys = [k[0] for k in self.output_checker_parameters["parameters"]]
            result = {k: v for k, v in result.items() if k in required_keys}

        # Convert list in dict parameters to json string
        if isinstance(result, dict):
            for k, v in result.items():
                if isinstance(v, list):
                    result[k] = json.dumps(v)

        self.result = result
    
    def get_result(self) -> Any:
        return self.result
    
    def is_done(self) -> bool:
        return self.result is not None
