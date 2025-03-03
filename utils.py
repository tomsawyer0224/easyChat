import ollama
from typing import List
import yaml

def config_parser(config_file: str):
    with open("./config.yaml") as f:
        config = yaml.safe_load(f)
    return config
def pull_model(models: List[str] = ["llama3.2:1b", "gemma:2b"]):
    """
    pull models from a list
    """
    for model in models:
        ollama.pull(model)
def generate_Dockerfile(
        base_image: str = "python:3.12-slim",
        models: List[str] = ["llama3.2:1b", "gemma:2b"]
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
        "RUN ollama serve & sleep 10 && \\\n" + \
        pull_model_command + \
        "# set the working directory\n"
        "WORKDIR /app\n"
        "# copy project to the image\n"
        "COPY . .\n"
        "# install dependencies\n"
        "RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt\n"
        "# expose a port so that chainlit can listen on\n"
        "EXPOSE 8080\n"
        "# specify default commands\n"
        'CMD ["/bin/bash", "-c", "ollama serve & sleep 10 && chainlit run app.py -h --host 0.0.0.0 --port 8080"]'
    )
    
    with open("Dockerfile", "w") as dockerfile:
        dockerfile.write(content)
