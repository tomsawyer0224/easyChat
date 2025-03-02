from typing import List, Optional, cast

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
# from langchain_core.runnables import (
#     RunnableLambda,
#     ConfigurableFieldSpec,
#     RunnablePassthrough,
# )
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain.schema.runnable.config import RunnableConfig
from langchain.schema import StrOutputParser

import chainlit as cl
from chainlit.input_widget import Select, Slider


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]

# history = get_by_session_id("1")
# history.add_message(AIMessage(content="hello"))
# print(store)  # noqa: T201

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
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    model = ChatOllama(
        model=settings["model"],
        temperature=settings["temperature"]
    )
    chain = prompt | model | StrOutputParser()
    runnable = RunnableWithMessageHistory(
        chain,
        get_by_session_id,
        input_messages_key="question",
        history_messages_key="history",
    )
    cl.user_session.set("runnable", runnable)

@cl.on_chat_start
async def on_chat_start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Ollama - Model",
                values=["llama3.2:1b", "qwen2.5:0.5b"],
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
    runnable = cast(RunnableWithMessageHistory, cl.user_session.get("runnable"))  # type: RunnableWithMessageHistory

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        # config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        config={"configurable": {"session_id": "chat_session"}}
    ):
        await msg.stream_token(chunk)

    await msg.send()