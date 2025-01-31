FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

RUN echo 'APT::Sandbox::User "root";' > /etc/apt/apt.conf.d/sandbox-disable

RUN apt update && apt install python3-pip wget zip ffmpeg libsm6 libxext6 git libcairo2-dev -y

RUN pip3 install --upgrade pip

RUN pip3 install --default-timeout=100 torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121

RUN pip3 install --default-timeout=100 webdataset pytorch-lightning wandb transformers diffusers accelerate pandas pyarrow \
opencv-python matplotlib scikit-learn nltk numba seaborn umap-learn torchmetrics open-clip-torch plotly sentence-transformers

RUN adduser --disabled-password bigdata

WORKDIR /home/bigdata
USER bigdata
