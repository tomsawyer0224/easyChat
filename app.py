from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from typing import cast

import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    model = ChatOllama(
        #model="llama3.2:1b",
        model="qwen2.5:0.5b",
        temperature=0.7
    )
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
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()