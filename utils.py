import ollama
from typing import List
import yaml
from PIL import Image
from io import BytesIO
from langgraph.graph.state import CompiledStateGraph

def save_graph(graph: CompiledStateGraph, file_path: str):
    """visualize a graph by a .png image file"""
    img_in_byte = graph.get_graph().draw_mermaid_png()
    with Image.open(BytesIO(img_in_byte)) as img:
        img.save(file_path)

def parse_config(config_file: str):
    with open("./config.yaml") as f:
        config = yaml.safe_load(f)
    return config


def pull_model(models: List[str] = ["llama3.2", "llama3.2:1b"]):
    """
    pull models from a list
    """
    existing_model = [m.model for m in ollama.list().models]
    for model in set(models) - set(existing_model):
        ollama.pull(model)


def generate_Dockerfile(
    base_image: str = "python:3.12-slim",
    models: List[str] = ["llama3.2", "llama3.2:1b"],
):
    """
    generate Dockerfile
    """
    pull_model_command = ""
    n_model = len(models)
    for i in range(n_model):
        end = "\n" if i == n_model - 1 else "&& \\\n"
        pull_model_command += f"\tollama pull {models[i]} {end}"
        content = (
        "# base image\n"
        f"FROM {base_image}\n"
        "# set environment variables\n"
        "ENV PYTHONUNBUFFERED=1\n"
        "# install ollama and pull models\n"
        "RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*\n"
        "RUN curl -fsSL https://ollama.com/install.sh | sh\n"
        "RUN ollama serve & sleep 10 && \\\n"
        + pull_model_command
        + "# set the working directory\n"
        "WORKDIR /app\n"
        "# copy project to the image\n"
        "COPY . .\n"
        "# install dependencies\n"
        "RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt\n"
        # expose a port so that chainlit can listen on
        EXPOSE 8080
        # specify default commands
        CMD ["/bin/bash", "-c", "ollama serve & sleep 10 && chainlit run app.py -h --host 0.0.0.0 --port 8080"]
    )
    with open("Dockerfile", "w") as dockerfile:
        dockerfile.write(content)
