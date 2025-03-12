from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain.schema import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import ConfigurableField
from langchain_core.prompts import PromptTemplate

from pydantic import BaseModel, Field
from uuid import uuid4

import chainlit as cl
from typing import List, Callable
from functools import partial

import sys
import asyncio

SYSTEM_MESSAGE = (
    "You are a helpful, respectful and honest assistant. "
    "Always answer as helpfully as possible, while being safe. "
    "Your answers should not include any harmful, unethical, "
    "racist, sexist, toxic, dangerous, or illegal content. "
    "Please ensure that your responses are socially unbiased and positive in nature."
    "\n\nIf a question does not make any sense, or is not factually coherent, "
    "explain why instead of answering something not correct. "
    "If you don't know the answer to a question, please don't share false information."
)

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

model = ChatOllama(
            model="llama3.2:1b",
            # temperature=0
        ).configurable_fields(
            temperature=ConfigurableField(
                id="temperature",
                name="LLM Temperature",
                description="The temperature of the LLM",
            )
        )   

prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_MESSAGE),
                # MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )
chain = prompt | model | StrOutputParser()

print(chain.with_config({"temperature":0.0}).invoke({"question": "tell me a joke"}))
print(chain.with_config({"temperature":0.0}).invoke({"question": "tell me a joke"}))
print(chain.with_config({"temperature":0.0}).invoke({"question": "tell me a joke"}))

print("-"*50)
chain_with_history = RunnableWithMessageHistory(
    chain,
    # Uses the get_by_session_id function defined in the example
    # above.
    get_by_session_id,
    input_messages_key="question",
    history_messages_key="history",
)

# print(chain_with_history.with_config({"temperature":0.00}).invoke(
#     {"question": "tell me a joke"}, {'configurable': {'session_id' : "user_local"}})
# )
# print(chain_with_history.with_config({"temperature":0.00}).invoke(
#     {"question": "tell me a joke"}, {'configurable': {'session_id' : "user_local"}})
# )
# print(chain_with_history.with_config({"temperature":0.00}).invoke(
#     {"question": "tell me a joke"}, {'configurable': {'session_id' : "user_local"}})
# )
# print("-"*50)
# print(store)
async def generate():
    chunks = []
    async for chunk in chain_with_history.with_config({"temperature": 0.90}).astream(
            {"question": "tell me a joke"},
            config={"configurable": {"session_id": "local"}},
        ):
            chunks.append(chunk)
    return chunks
c1 = asyncio.run(generate())
c2 = asyncio.run(generate())
print(c1)
print(c2)
print(c1==c2)
print(store)
