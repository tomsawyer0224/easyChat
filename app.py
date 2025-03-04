from typing import cast

from langchain_core.runnables.history import RunnableWithMessageHistory

import chainlit as cl
from chainlit.input_widget import Select, Slider

from model import ChatModel
from utils import parse_config, pull_model

chatbot = ChatModel()

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

    chatbot.update(settings)

@cl.on_settings_update
async def on_settings_update(settings):
    chatbot.update(settings)

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(RunnableWithMessageHistory, cl.user_session.get("runnable"))  # type: RunnableWithMessageHistory

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config={"configurable": {"session_id": "user_local"}}
    ):
        await msg.stream_token(chunk)

    await msg.send()