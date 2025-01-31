## PromptMap UI

This is a code for PromptMap user interface and preparing the database for use in it.


## Requirements

We require a docker to be installed on the system, around 600GB of storage and 32GB of RAM.
A GPU is also needed if the text-to-image model is to be used.

## Preparation of the environment

First, please build the docker container.

```
docker buildx build -t ui .
```

Please create a path where the application data will be stored, and a separate path for models.

Application data directory should have the following structure:

```
datadir
├── db_final.parquet
├── diffusion_db
│   ├── db.index
│   └── db.parquet
├── img
│   ├── diffusiondb
│   │   ├── data.mdb
│   │   └── lock.mdb
│   └── promptmap
│       ├── data.mdb
│       └── lock.mdb
├── map
│   ├── labels.parquet
│   └── point_positions.npy
└── search_indexes
    ├── genre.idx
    ├── lighting.idx
    ├── location.idx
    ├── mood.idx
    ├── prompt.idx
    ├── subject.idx
    └── tone.idx
```

To prepare it, first download the db_final.parquet and diffusiondb.parquet from the dataset repository linked on our github:
`https://github.com/Bill2462/prompt-map`, then rename diffusiondb.parquet and move it to `diffusion_db`.

Download diffusiondb image db shards from the same repository and merge shards using the following command: `cat ls.?? > data`. Separately download `lock.mdb`. Finally download map and search indexes.

To prepare model directory please clone the following models with `git clone` there:

 - `all-mpnet-base-v2`: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
 - `sdxl-turbo`: https://huggingface.co/stabilityai/sdxl-turbo

## Running PromptMap

Start interactive shell in the container:

```
docker run \
-it \
--mount src=/path/to/codebase,target=/home/bigdata,type=bind \
--mount src=/path/to/models,target=/models,type=bind \
--mount src=/path/to/ui/data,target=/datadir,type=bind \
-p 8888:8888 \
ui:latest bash
```

Replace `/path/to/codebase`, `/path/to/models`, and `/path/to/ui/data` with actual absolute paths to those locations on the given system.

Run `python3 main.py`, which will start the interface.

Use the following links to access the different versions of the UI:

 - `http://127.0.0.1:8000//conditions/goldenDragon`: PromptMap
 - `127.0.0.1:8000//conditions/brightEinstein`: DiffusionDB search
 - `127.0.0.1:8000//conditions/blueCuttlefish`: Simple baseline
 
You can browse PromptMap without the stable diffusion model by setting the `"use_dummy_sd_model"` to `true` in `cfg/config.json`. No GPU is required in that case.
