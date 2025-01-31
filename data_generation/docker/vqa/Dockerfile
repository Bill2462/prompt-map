FROM nvidia/cuda:12.1.0-base-ubuntu22.04

RUN echo 'APT::Sandbox::User "root";' > /etc/apt/apt.conf.d/sandbox-disable

RUN apt update && apt install python3-pip git -y

RUN pip3 install --upgrade pip

RUN pip3 install --default-timeout=100 pandas pyarrow openai vllm vllm_flash_attn webdataset timm==0.9.10

RUN adduser --disabled-password bigdata

WORKDIR /home/bigdata
USER bigdata
