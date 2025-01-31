# PromptMap Data Generation Pipeline

This repository contains the source code needed to run the pipeline shown in the PromptMap paper. Please note that due to stochastic nature of the
process, rerun of the pipeline may produce different results. To download the dataset that was used in the study, please visit our hugginface
repository: [https://huggingface.co/datasets/Bill2462/PromptMap](https://huggingface.co/datasets/Bill2462/PromptMap).

## Repository Structure

 - `bench` - Scripts that were used to benchmark the number of topics in the dataset.
 - `configs` - Settings for each pipeline stage.
 - `dataset_generation` - Codebase for dataset generation.
 - `map_making` - Scripts for making the map.
 - `prompts` - All of the prompts used for the LLM.
 - `seed_categories` - The list of seed categories used for the generation.
 - `util` - Various scripts used in the generation process.
 - `generate_data.py` - Main generation script.

## Environment

We use docker containers to package the environment necessary to build different stages of the pipeline.

There are three containers needed to run the process:

 - `docker/llm_inference`- Environment with VLLM, used to conduct the LLM inference.
 - `docker/general` - General environment for embedding computation, deduplication and other operations.
 - `docker/vqa` - Environment for conducting VQA.
 
Please build all three containers and note that for general container, extra manual steps need to be taken to build faiss with GPU support.
Please, first build the image and then follow instructions from: 
[https://stackoverflow.com/questions/56551276/how-to-edit-docker-image](https://stackoverflow.com/questions/56551276/how-to-edit-docker-image)
on how to commit changes made inside an interactive shell. Please run commands from `docker/general/build_faiss.txt` and then save the new image.

## Procedure for Data Generation

This section describes the procedure that when followed should result in the data that can be used in the PromptMap interface.

We do not include exact command and scripts for running the pipeline as they will be dependent on the underlying HPC architecture.

### Idea Generation

The generation is conducted using the generation script that contains file with input data, generation config file,
llm config file and output file.

#### Stage 1

For stage 1 of the pipeline please run the expansion for fictional and real categories:

```
python3 generate_data.py \
--task_config configs/idea_expansion_i1_real.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/db_initial.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_real.parquet

python3 generate_data.py \
--task_config configs/idea_expansion_i1_fiction.json \
--llm_config configs/llm/llm_config_mistral_7B.json \
--input_path /netscratch/adamkiewicz/prompt_gen/db_initial.parquet \
--output_path /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_fiction.parquet
```

then the deduplication can be ran with the following commands:

```
python3 util/make_text_embedding.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_real.parquet \
--column_name expanded_idea_i1 \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/embed_real.npy \
--model_path /netscratch/adamkiewicz/models/clip_model

python3 util/remove_duplicates.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/outputs/raw_real.parquet \
--input_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/embed_real.npy \
--output_filepath_filtered /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/final_real.parquet \
--output_filepath_duplicates /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i1/duplicates_real.pkl
```

This example shows deduplication for the real samples. Change filenames to run deduplication for fictional samples.

#### Stage 2

The process is repeated for the second stage. To run the second expansion stage, please change the `input_filepath` to corresponding deduplicated outputs written to path specified by `--output_filepath_filtered`.
Please also change the task config file to `idea_expansion_i1_real.json` and `idea_expansion_i1_fiction.json` for real categories and fictional categories respectably. Please also change the `--column_name` to `expanded_idea_i2`.

To then run the deduplication of stage 2 output, please first merge both fictional and real outputs. Please rename both output dataframes to `0.parquet` and `1.parquet` and use the `merge_dfs.py` script.

Here is the example usage of that script.

```
python3 util/merge_dfs.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/outputs \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/raw.parquet
```

For deduplication please use the same process as shown before with the exception of changed `--n_part_ivf` setting. Please add `--n_part_ivf 5000`. This step was added to ensure faster processing.

#### Stage 3

Before running the last stage of the idea generation (and subsequent stages), we recommend splitting the input df into shards to allow for parallel processing on multiple GPUs.

Use `split_dfs.py` script. Example usage: 

```
python3 util/split_df.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i2/final.parquet \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/inputs \
-n 16
```

Then outputs from generation have to be merged into a single file using the `merge_dfs.py` script. Example usage:

```
python3 util/merge_dfs.py \
-i /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/outputs \
-o /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/expansion_i3/raw.parquet
```

Configuration file for the generation script is: `idea_expansion_i3.json` and the column name for deduplication is `expanded_idea_i3` Follow the same deduplication process and settings as in Stage 2.

### Prompt Generation

The prompt generation follows the generation procedure from previous stages but without the deduplication.
It is highly recommended to split the input into shards and using multiple GPUs to avoid processing times measured in weeks.

The following files are used in order: `add_location.json`, `add_subject.json`,`make_captions.json`, and `add_parameters.json`. Each stage uses the output from the previous stage.
For the last merge operation please also add `--add_index_as_column`
flag so the index column is added. If you did not shard the input files, please add column named `index` containing numbers from 0 to the number of rows.

### Image Generation and Filtering

To make images, first split the dataframe with prompts into multiple shards (highly recommended step).
Then download the `stable-diffusion-xl-turbo` model from hugginface: [https://huggingface.co/stabilityai/sdxl-turbo](https://huggingface.co/stabilityai/sdxl-turbo).
Other models can be used but support for them need to be added to the generation script.

Then run the generation script for each prompt shard (example command):

```
python3 util/make_images.py \
--prompt_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/inputs/$JOB_IDX.parquet \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs/$JOB_IDX.tar \
--use_turbo \
--use_index_column_as_filename \
--sd_path /netscratch/adamkiewicz/models/sdxl-turbo \
--prompt_column "caption"
```

Next step is to run the NSFW filtering. To do that, please first download the safety checker from hugginface:
[https://huggingface.co/CompVis/stable-diffusion-safety-checker](https://huggingface.co/CompVis/stable-diffusion-safety-checker).

Then the safety checker should be applied to each `.tar` file with images using the following command:

```
python3 util/check_nsfw.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs/$JOB_IDX.tar \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/nsfw_flags/$JOB_IDX.parquet \
--model_path /netscratch/adamkiewicz/models/stable-diffusion-safety-checker
```

Then please merge all of the output shards and then use the `util/filter_images_by_nsfw.py` script to remove images that are not save, `util/merge_data_with_nsfw_flags.py` to merge the NSFW flags with the
prompt dataframe and finally `util/filter_df_by_nsfw.py` to filter the prompts by the dataframe.

## Procedure for Preparing the Map

All scripts for the map making are in the `map_making` directory. First you can reduce the dataset size by removing unnecessary columns. Please use `export_df.py` script.


Then please run the VQA on the image database to generate the image main subject annotations:

```
python3 map_making/run_vqa.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/make_images/outputs/$SLURM_ARRAY_TASK_ID.tar \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/vqa_output/subjects/$SLURM_ARRAY_TASK_ID.parquet \
--model /netscratch/adamkiewicz/models/MiniCPM-V-2_6 \
--batch_size 256
```

You first will need to download the MiniCPM-V-2_6 model [https://huggingface.co/openbmb/MiniCPM-V-2_6](https://huggingface.co/openbmb/MiniCPM-V-2_6).

Then, please merge the annotations, and then make text embeddings of them:

```
python3 map_making/make_text_embeddings_st.py \
--input_filepath /netscratch/adamkiewicz/prompt_gen/run/intermidiate_stages/vqa_output/subjects_map.parquet \
--column_name "vqa_subject" \
--output_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/subjects_map.npy \
--model_path /netscratch/adamkiewicz/models/all-mpnet-base-v2 --batch_size 4000
```

Text encoder model can be downloaded from [https://huggingface.co/sentence-transformers/all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2).

Next step is fitting UMAP model and applying it to the embeddings to get the point positions. For the full 12.4M samples, around 200GB of RAM will be required to perform this process and on 32 cores it will take around 4h.

```
python3 map_making/fit_umap.py \
--data /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/subjects_map.npy \
--output /netscratch/adamkiewicz/prompt_gen/run/umap.pkl \
--data_df /netscratch/adamkiewicz/prompt_gen/run/vqa_output.parquet --data_column vqa_subject --n_neighbors 50

python3 map_making/apply_umap.py \
--input_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/embeddings_st/subjects_map.npy \
--umap_model_filepath /netscratch/adamkiewicz/prompt_gen/run/umap.pkl \
--output_embed_filepath /netscratch/adamkiewicz/prompt_gen/run/map/point_positions_raw.npy
```

Now rescale all of the point positions to fit the <0, 1> square using the `map_making/rescale_points.py`. Then to build the build the map, please use the `make_histogram_map.py` to create a 2D map histogram serving as the map background.
Then please mark in red the positions where the labels should go on the histogram picture. Then please split label points between zoom levels using the `map_making/split_labels_into_levels.py` and then
run nearest neighbour search `map_making/get_nn_to_manual_selection.py`(with `subject` column as input column) to generate input to LLM. Finally, run the LLM to summarize the points using the `generate_data.py` script with `make_labels.json` config.

To generate map background please process the histogram image manually in an image editor. We used color manipulation in GIMP to obtain the final image.

To build search indexes, please use the `map_making/make_text_embeddings_st.py` to create embedding of each column within the dataset (`subject`, `location`, `lighting`, `mood`, `tone`, `genre`).
Then please run `map_making/build_faiss_index.py` for each created embedding table to build index table.

Then finally, export all images as lmdb by running the `map_making/create_img_db.py` script and preselect images for preview with `map_making/select_points_for_img_preview.py` script.

## Counting Unique Ideas

All scripts for reproducing the subject count plot from the paper are located in `bench` directory. First, use `bench/sample_prompts.py` to pick random prompt samples. To produce naive prompts, please use ``generate_data.py`` script with config and prompt
from `bench/naive_prompt`. Then, generate images from prompt samples using `util/make_images.py` script and run VQA using the `bench/run_vqa.py` script. Finally, make text embeddings, using the `util/make_text_embedding.py` script
using the same settings as in the deduplication step in the pipeline and run `bench/mark_duplicates.py` to find duplicate topics. Finally, plot, the result using the `bench/plot_bench_result.py` script.
Average token counts can be obtained using the `bench/count_tokens.py` script.
