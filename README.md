# easyChat

A simple project to create a local chatbot.

## Description

This project creates a chatbot program that runs locally on CPU using the Langchain, Ollama, and Chainlit frameworks.

## Getting Started

### Dependencies

* OS: Ubuntu (22.04, 24.04).
* Installed packages: [Ollama](https://ollama.com/download/linux), [Docker](https://docs.docker.com/engine/install/ubuntu/), [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

### How to use

1. Open a Terminal and clone this repository:

```
git clone https://github.com/tomsawyer0224/easyChat.git
cd easyChat
```
2. Run the following command to create a virtual environment and install all requirements,
```
source init.sh
```
3. Modify the 'config.yaml' file if needed. By default, the chatbot is powered by 'llama3.2:1b' or 'gemma:2b'. When using, you can chose either of them.
4. You can run the chatbot here using the below command, wait for a few seconds and open the url http://localhost:8080 on a web browser to use the application.
```
chainlit run app.py -w --port 8080
```
If you want to build a docker image, continue to step 5 (preferred).\
5. Run the command to build a docker image
```
python build_docker.py
```
* To start the chatbot, run command
```
docker run --name echat --rm -p 8080:8080 chatbot
```
or in background mode
```
docker run --name echat --rm -d -p 8080:8080 chatbot
```
* Open the url http://localhost:8080 on a web browser to use the chatbot.
* To stop the chatbot, run command:
```
docker stop echat
```
> [!Note]
> You can push the docker image to [Docker hub](https://hub.docker.com/) for future use.
> Because of working on CPU, you should choose small Ollama models to build the chatbot (specify in the 'config.yaml' file).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
* [chainlit-langchain](https://docs.chainlit.io/integrations/langchain)
* [chainlit-cookbook](https://github.com/Chainlit/cookbook/tree/main/aws-ecs-deployment)
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
