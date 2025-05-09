# easyChat

A simple project to create a local chatbot.
<p float="left">
  <img src="demo/chatbot_1.png" width="49%" />
  <img src="demo/chatbot_2.png" width="49%" />
</p>

## Description

This project creates a chatbot program that runs locally on CPU using the LangGraph, Ollama, and Chainlit frameworks.

## Getting Started

### Dependencies

* OS: Ubuntu (22.04, 24.04).
* Installed packages: [Ollama](https://ollama.com/download/linux), [Docker](https://docs.docker.com/engine/install/ubuntu/), [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

### How to use

1. Open a terminal and clone this repository:

```
git clone https://github.com/tomsawyer0224/easyChat.git
cd easyChat
```
2. Run the following command to create a virtual environment and install all requirements.
```
source init.sh
```
3. Modify the 'config.yaml' file if needed. By default, the chatbot is powered by 'llama3.2:1b' and 'gemma:2b' in the Ollama framework. When using it, you can choose either of them.
4. You can use the command below to launch the chatbot, wait a few seconds, and then use a web browser to access the application at http://localhost:8080. Proceed to step 5 (recommended) if you wish to create a Docker image.
```
chainlit run app.py -w -h --port 8080
```

5. Build a Docker image by running the command (on a terminal inside the 'easyChat' directory):
```
python build_docker.py
```
* To start the chatbot, run command:
```
docker run --name echat --rm -p 8080:8080 chatbot
```
or in background mode:
```
docker run --name echat --rm -d -p 8080:8080 chatbot
```
* Access the application at http://localhost:8080.
* To stop the chatbot, run command:
```
docker stop echat
```
> [!Note]
> For later use, you can publish the docker image to [Docker hub](https://hub.docker.com/). Because the chatbot runs on CPU, you should build the chatbot using minimal Ollama models (specified in the 'config.yaml' file).\
> The chatbot will generate varied responses to identical questions, even with the temperature set to zero, due to its retention of the entire conversation history.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments
* [chainlit-langgraph](https://docs.chainlit.io/integrations/langchain)
* [chainlit-cookbook](https://github.com/Chainlit/cookbook/tree/main/aws-ecs-deployment)
* [langchain-runnable](https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html)
* [react-agent](https://github.com/langchain-ai/react-agent/tree/main)
