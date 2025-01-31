import os
import io
import argparse
import pandas as pd
import webdataset as wds

from PIL import Image
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

class VqaModel:
    def __init__(self, model_path: str,
                 gpu_memory_utilization: int,
                 max_tokens: int = 1024,
                 best_of: int = 3):

        self.llm = LLM(
            model=model_path,
            trust_remote_code=True,
            gpu_memory_utilization=gpu_memory_utilization,
            max_model_len=2048
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        stop_tokens = ('<|im_end|>', '<|endoftext|>')
        stop_token_ids = [self.tokenizer.convert_tokens_to_ids(i) for i in stop_tokens]

        self.sample_params = SamplingParams(
            stop_token_ids=stop_token_ids,
            use_beam_search=True,
            temperature=0,
            best_of=best_of,
            max_tokens=max_tokens
        )
    
    def set_question(self, question: str = "What is the main subject of the image? Your caption should be between 10 and 15 words long."):
        messages = [{"role":
                     "user",
                     "content":
                     "(<image>./</image>)" + \
                     f"\n{question}"}]
        
        self.prompt = self.tokenizer.apply_chat_template(messages,
                                                         tokenize=False,
                                                         add_generation_prompt=True)
    
    def run_inference(self, images: list) -> list[str]:
        inputs = [{
            "prompt": self.prompt,
            "multi_modal_data": {
                "image": image
            },
        } for image in images]

        outputs = self.llm.generate(inputs,
                                    sampling_params=self.sample_params,
                                    use_tqdm = False)

        return [output.outputs[0].text for output in outputs]

def get_messages(question: str) -> list:
    return  [{
        "role":
        "user",
        "content":
        "(<image>./</image>)" + \
        f"\n{question}" 
    }]

class DataBatcher:
    def __init__(self, data_iter, batch_size):
        self.data_iter = iter(data_iter)
        self.batch_size = batch_size
        self.current_batch = []
        self.end_of_data = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.end_of_data:
            raise StopIteration
        
        self.current_batch = []
        try:
            for _ in range(self.batch_size):
                self.current_batch.append(next(self.data_iter))
        except StopIteration:
            self.end_of_data = True

        if not self.current_batch:
            raise StopIteration
        return self.current_batch

    def reset(self, data_iter=None):
        if data_iter is not None:
            self.data_iter = iter(data_iter)
        else:
            self.data_iter = iter(self.data_iter)
        self.current_batch = []
        self.end_of_data = False

def webp_decoder(key, value):
    if not key.endswith(".webp"):
        return None
    assert isinstance(value, bytes)
    return Image.open(io.BytesIO(value))

def get_question(question_type: str) -> str:
    if question_type == "location":
        return "Where is the image set? Your caption should be between 10 and 15 words long. Do not describe the main subject of the image."
    elif question_type == "subject":
        return "What is the main subject of the image? Your caption should be between 10 and 15 words long. Do not describe the location where the image is set."
    elif question_type == "subject_for_layout":
        return "What is the main subject of the image? Your caption should be between 10 and 15 words long."
    elif question_type == "lighting":
        return "What is the lighting like in this image? Your caption should be between 10 and 15 words long."
    elif question_type == "mood":
        return "What is the mood of this image? Your caption should be between 10 and 15 words long."
    elif question_type == "tone":
        return "What is the tone of this image? Your caption should be between 10 and 15 words long."
    elif question_type == "genre":
        return "What genre is this image? Your answer must be less than 5 words long"
    else:
        raise ValueError(f"Invalid question type: {question_type}")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_filepath", type=str, required=True)
    parser.add_argument("--output_filepath", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)

    parser.add_argument("--question_type", type=str, default="subject_for_layout",
                    choices=["subject_for_layout", "location", "subject", "lighting", "mood", "tone", "genre"])

    parser.add_argument("--batch_size", type=int, default=1)    
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.95)
    parser.add_argument("--best_of", type=int, default=3)
    parser.add_argument("--max_tokens", type=int, default=1024)

    return parser.parse_args()

def main():
    args = get_args()
    model = VqaModel(args.model, args.gpu_memory_utilization,
                        args.max_tokens, args.best_of)

    model.set_question(get_question(args.question_type))

    ds = (
        wds.WebDataset(args.input_filepath)
        .decode(webp_decoder)
        .to_tuple("webp", "__key__")
    )

    os.makedirs(os.path.dirname(args.output_filepath), exist_ok=True)
    filenames_all = []
    answers_all = []

    n_processed_samples = 0
    for batch in DataBatcher(ds, args.batch_size):
        images, filenames = zip(*batch)
        answers = model.run_inference(images)

        filenames_all.extend(filenames)
        answers_all.extend(answers)

        n_processed_samples += len(answers)
        print(f"Processed {n_processed_samples} samples", flush=True)
    
    df = pd.DataFrame({
        "filename": filenames_all,
        "vqa_subject": answers_all
    })

    df.to_parquet(args.output_filepath, index=False)
    
if __name__ == "__main__":
    main()
