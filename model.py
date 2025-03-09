from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain.schema import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory

from pydantic import BaseModel, Field

import chainlit as cl
from typing import List

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


class ChatModel:
    def __init__(self):
        self.model = None
        self.store = {}
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_MESSAGE),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryHistory()
        return self.store[session_id]

    def update(self, settings: cl.ChatSettings):
        """
        update model from chainlit ChatSettings (with keys are 'model', 'temperature')
        """
        self.model = ChatOllama(
            model=settings["model"], temperature=settings["temperature"]
        )
        chain = self.prompt | self.model | self.output_parser
        runnable = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        cl.user_session.set("runnable", runnable)

# modify something
