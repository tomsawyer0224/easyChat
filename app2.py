from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

import chainlit as cl
from chainlit.input_widget import Select, Slider

from utils import parse_config, pull_model

SYSTEM_MESSAGE = (
    "You are a helpful, respectful and honest assistant. "
    "Always answer as helpfully as possible, while being safe. "
    "Your answers should not include any harmful, unethical, "
    "racist, sexist, toxic, dangerous, or illegal content. "
    "Please ensure that your responses are socially unbiased and positive in nature."
    "\n\nIf a question does not make any sense, or is not factually coherent, "
    "explain why instead of answering something not correct. "
    "If you don't know the answer to a question, please don't share false information."
    "You don't need to use tool for every query, only use when searching current events."
)
model = ChatOllama(model="llama3.2:1b")
config = parse_config("./config.yaml")
models = config["models"]
pull_model(models)

@cl.on_chat_start
async def on_chat_start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Ollama - Model",
                values=models,
                initial_index=0,
            ),
            Slider(
                id="temperature",
                label="Temperature",
                initial=0.7,
                min=0,
                max=1,
                step=0.1,
            ),
        ]
    ).send()

graph = create_react_agent(
    model=model,
    tools=[],
    name="chat_expert",
    prompt=SYSTEM_MESSAGE,
    checkpointer=MemorySaver()
)

@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    print(f"config: {config}")
    final_answer = cl.Message(content="")
    
    for msg, metadata in graph.stream({"messages": [HumanMessage(content=msg.content)]}, stream_mode="messages", config=config):
        if msg.content:
            print(f"***msg***: {msg}")
            print(f"***metadata***: {metadata}")
            print("-"*30)
            await final_answer.stream_token(msg.content)

    await final_answer.send()