from typing import cast

from langchain_core.runnables.history import RunnableWithMessageHistory

import chainlit as cl
from chainlit.input_widget import Select, Slider

from core import ModelStore, ConversationStore, Session
from utils import parse_config, pull_model

model_store = ModelStore()
conversation_store = ConversationStore()

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

    session = Session.create(
        settings = settings,
        model_store = model_store,
        conversation_store = conversation_store
    )
    cl.user_session.set("session", session)


@cl.on_settings_update
async def on_settings_update(settings):
    session = cast(Session, cl.user_session.get("session"))
    session.update(settings=settings, model_store=model_store)
    cl.user_session.set("session", session)


@cl.on_message
async def on_message(message: cl.Message):
    session_info = cl.user_session.get("session").info
    runnable = session_info["runnable"]
    session_id = session_info["session_id"]
    temperature = session_info["temperature"]
    runnable = cast(
        RunnableWithMessageHistory, runnable
    )  # type: RunnableWithMessageHistory
    
    msg = cl.Message(content="")

    async for chunk in runnable.with_config({"temperature": temperature}).astream(
        {"question": message.content},
        config={"configurable": {"session_id": session_id}},
    ):
        await msg.stream_token(chunk)

    await msg.send()
