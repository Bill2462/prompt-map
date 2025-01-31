import os
import json
import argparse
import pandas as pd

from dataset_generation.predictor import LLMPredictor
from dataset_generation.processing_pool import LlmProcessingPool
from dataset_generation.processing_thread import SimpleProcessingThread, ProcessingError
from dataset_generation.loaders import SimpleDfSequentialReader, DummyReader

def load_json_config(config_file: str) -> dict:
    with open(config_file, "r") as f:
        return json.load(f)

def get_args():
    parser = argparse.ArgumentParser(description="Run the selected step of the data generation pipeline.")

    parser.add_argument("--task_config",type=str, required=True,
                        help="Path to the task configuration file")
    
    parser.add_argument("--llm_config", type=str, required=True,
                        help="Path to the worker configuration file")
    
    parser.add_argument("--input_path", type=str,
                        help="Path to the input data file or directory")
    
    parser.add_argument("--output_path", type=str, required=True,
                        help="Path to the output data file or directory")
    
    parser.add_argument("--prompt_path", type=str, default="prompts",
                        help="Path to directory with prompts.")

    parser.add_argument("--print_faliures", action="store_true",
                        help="Will print outputs for failed threads.")
    
    return parser.parse_args()

def load_prompt_from_file_if_needed(args, prompt: str):
    if prompt.startswith("file:"):
        path = os.path.join(args.prompt_path, prompt[5:]) 
        with open(path, "r") as f:
            return f.read()
    else:
        return prompt

def main():
    args = get_args()

    task_config = load_json_config(args.task_config)
    llm_config = load_json_config(args.llm_config)
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)

    if args.input_path:
        reader = SimpleDfSequentialReader(args.input_path,
                                          n_repeats = task_config["repeat_samples_n_times"] if "repeat_samples_n_times" in task_config.keys() else 1,
                                          shuffle = False,
                                          clip_size_to = None)
    else:
        reader = DummyReader(n_samples = task_config["n_samples"])

    predictor = LLMPredictor(model_path = llm_config["model_path"],
                             vllm_args = llm_config["vllm_args"])
    
    processing_pool = LlmProcessingPool(batch_size = llm_config["batch_size"])

    prompt_template = load_prompt_from_file_if_needed(args, task_config["prompt_template"])

    outputs = []
    printed_prompt_template = False
    while True:
        for _ in range(processing_pool.count_free_spots()):
            try:
                sample = reader.get_sample()
            except IndexError:
                break
            
            if "prompt_args" in task_config.keys():
                sample.update(task_config["prompt_args"])
                
            thread = SimpleProcessingThread(
                prompt_template = prompt_template,
                output_checker_parameters = task_config["output_checker_params"],
                sampling_parameters = task_config["sampling_parameters"],
                prompt_parameter_values = sample,
                max_n_retries = task_config["max_n_retries"]
            )
            processing_pool.add_processing_thread(thread)

            if not printed_prompt_template:
                print(thread.prompt, flush=True)
                printed_prompt_template = True
        
        if len(processing_pool.processing_threads) == 0:
            break
        
        n_threads = len(processing_pool.processing_threads)

        llm_inputs = processing_pool.get_llm_batch()
        llm_outputs = predictor(llm_inputs)
        processing_pool.process_llm_outputs(llm_outputs)

        if args.print_faliures:
            for e in processing_pool.errors:
                print(e.get_str(), flush=True)

        done_threads = processing_pool.get_done_processing_threads()
        n_done_threads = len(done_threads)

        samples_exceeding_retries = 0
        last_samples_saved = task_config["save_every_n_samples"]
        for thread in done_threads:
            result = thread.get_result()
            if isinstance(result, ProcessingError):
                samples_exceeding_retries += 1
                continue
    
            if not isinstance(result, list):
                result = [result]
            
            if "write_output_to_column" in task_config.keys():
                result = [{task_config["write_output_to_column"]: x} for x in result]
            else:
                if not isinstance(result[0], dict):
                    raise ValueError("Result must be a dictionary if write_output_to_column is not specified.")
            
            if task_config["pass_input_input_to_output"]:
                for r in result:
                    r.update(thread.get_input_data())
            
            outputs.extend(result)

        # Print some stats
        n_falied_threads = n_threads - n_done_threads
        out_str = f"Processed {reader.current_index}/{len(reader)} ({(reader.current_index/len(reader))*100:.2f}%) samples."
        out_str += f" Threads succeeded={n_done_threads} failed={n_falied_threads} samples that exceeded max retries={samples_exceeding_retries}"
        out_str += f" success rate={n_done_threads / n_threads:.2f}"
        print(out_str, flush=True)

        if last_samples_saved + task_config["save_every_n_samples"] <= len(outputs):
            last_samples_saved = len(outputs)
            print("Saving intermediate results.")
            df = pd.DataFrame(outputs)
            df.to_parquet(args.output_path)

    df = pd.DataFrame(outputs)
    df.to_parquet(args.output_path)

if __name__ == "__main__":
    main()
