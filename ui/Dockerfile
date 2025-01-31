FROM nvidia/cuda:12.1.0-base-ubuntu22.04

RUN echo 'APT::Sandbox::User "root";' > /etc/apt/apt.conf.d/sandbox-disable

RUN apt update && apt install python3-pip wget zip ffmpeg libsm6 libxext6 git libcairo2-dev libffi-dev python3-dev build-essential libopenblas-dev swig -y

RUN pip3 install --upgrade pip

RUN pip3 install --default-timeout=100 torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu121

RUN pip3 install --default-timeout=100 webdataset transformers diffusers pandas pyarrow \
opencv-python scikit-learn nltk numba seaborn open-clip-torch flask gunicorn lmdb faiss-cpu sentence-transformers

RUN adduser --disabled-password bigdata

WORKDIR /home/bigdata
USER bigdata
