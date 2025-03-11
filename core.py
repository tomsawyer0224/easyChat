from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain.schema import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import ConfigurableField

from pydantic import BaseModel, Field
from uuid import uuid4

import chainlit as cl
from typing import List, Tuple, Callable
from functools import partial

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


class ModelStore:
    """stores Ollama model"""
    def __init__(self):
        self.models = {}

    def deliver_to_user(self, model: str):
        """returns specific model"""
        if model not in self.models.keys():
            self.models[model] = ChatOllama(model=model).configurable_fields(
                temperature=ConfigurableField(
                    id="temperature",
                    name="LLM Temperature",
                    description="The temperature of the LLM",
                )
            )
        return self.models[model]

    @property
    def all_models(self):
        return self.models


class ConversationStore:
    """stores conversations"""
    def __init__(self):
        self.conversations = {}

    def deliver_to_user(self, session_id):
        """returns specific conversation"""
        if session_id not in self.conversations.keys():
            self.conversations[session_id] = InMemoryHistory()
        return self.conversations[session_id]

    @property
    def all_conversations(self):
        return self.conversations


class Session:
    """chat session for each user"""
    def __init__(self, model: ChatOllama, temperature: float, get_session_history: Callable):
        """This method is not used to create an instance direcly"""
        self.session_id = uuid4().hex
        self.model = model
        self.temperature = temperature
        self.get_session_history = get_session_history
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_MESSAGE),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )
        chain = self.prompt | self.model | self.output_parser
        self.runnable = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

    @classmethod
    def create(
        cls,
        settings: cl.ChatSettings,
        model_store: ModelStore,
        conversation_store: ConversationStore,
    ):
        """method to create a Session instance"""
        def get_conversation_from_store(conversation_store, session_id):
            return conversation_store.deliver_to_user(session_id)
        get_session_history = partial(get_conversation_from_store, conversation_store)
        return cls(
            model=model_store.deliver_to_user(settings["model"]),
            temperature=settings["temperature"],
            get_session_history=get_session_history
        )

    def update(self, settings: cl.ChatSettings, model_store: ModelStore):
        """updates a session when changing settings"""
        self.model = model_store.deliver_to_user(settings["model"])
        self.temperature = settings["temperature"]
        
        chain = self.prompt | self.model | self.output_parser
        self.runnable = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

    @property
    def info(self):
        return dict(
            session_id=self.session_id, runnable=self.runnable, temperature=self.temperature
        )


