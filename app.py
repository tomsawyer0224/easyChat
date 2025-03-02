from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from typing import cast

import chainlit as cl
from chainlit.input_widget import Select, Slider

def init_model(settings):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful, respectful and honest assistant. "\
                "Always answer as helpfully as possible, while being safe. "\
                "Your answers should not include any harmful, unethical, "\
                "racist, sexist, toxic, dangerous, or illegal content. "\
                "Please ensure that your responses are socially unbiased and positive in nature."\
                "\n\nIf a question does not make any sense, or is not factually coherent, "\
                "explain why instead of answering something not correct. "\
                "If you don't know the answer to a question, please don't share false information.",
            ),
            ("human", "{question}"),
        ]
    )

    model = ChatOllama(
        model=settings["model"],
        temperature=settings["temperature"]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_chat_start
async def on_chat_start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Ollama - Model",
                values=["qwen2.5:0.5b", "llama3.2:1b"],
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

    init_model(settings)

@cl.on_settings_update
async def on_settings_update(settings):
    init_model(settings)

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        # config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()