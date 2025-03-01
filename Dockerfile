# Use an appropriate base image, e.g., python:3.10-slim
FROM python:3.12-slim

# Set environment variables (e.g., set Python to run in unbuffered mode)
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0:11434
# install ollama and pull model
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/* 
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama serve & sleep 10 && ollama pull qwen2.5:0.5b

# Set the working directory
WORKDIR /app

# Copy your application's requirements and install them
COPY . . 

# install dependencies
RUN pip install -U pip && pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "-m", "chainlit", "run", "app.py", "-h", "--host", "0.0.0.0","--port", "8080"]
