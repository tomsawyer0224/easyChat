from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
import chainlit as cl
from chainlit.input_widget import Select, Slider

from core import builder
from utils import parse_config, pull_model

graph = builder.compile(checkpointer=MemorySaver())


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
    config = {
        "configurable":{
            "thread_id": cl.context.session.id,
            "model": settings["model"],
            "temperature": settings["temperature"]
        }
    }
    cl.user_session.set("config", config)

@cl.on_settings_update
async def update(settings):
    config = cl.user_session.get("config")
    config["configurable"]["model"] = settings["model"]
    config["configurable"]["temperature"] = settings["temperature"]
    cl.user_session.set("config", config)

@cl.on_message
async def on_message(msg: cl.Message):
    config = cl.user_session.get("config")
    final_answer = cl.Message(content="")
    
    for msg, _ in graph.stream(
        {"messages": [{"role": "user", "content": msg.content}]}, 
        config=config,
        stream_mode="messages"
    ):
        if msg.content:
            await final_answer.stream_token(msg.content)

    await final_answer.send()