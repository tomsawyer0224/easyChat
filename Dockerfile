FROM python:3.12-slim

RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://ollama.com/install.sh | sh

EXPOSE 11434
#RUN ollama pull llama3.2:1b
RUN ollama serve & ollama pull qwen2.5:0.5b

WORKDIR /usr/src/app
COPY . .
RUN pip install -U pip
RUN pip install -r requirements.txt
CMD ["chainlit", "run", "app.py", "-w"]
