from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain.schema import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import BaseChatMessageHistory

from pydantic import BaseModel, Field
from uuid import uuid4

import chainlit as cl
from typing import List, Tuple

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


class ModelStore:
    def __init__(self):
        self.models = {}
    def update(self, model: str):
        if model not in self.models.keys():
            self.models[model] = ChatOllama(model = model)
    @property
    def all_models(self):
        return self.models

def get_model_from_store(model: str, model_store: ModelStore):
    model_store.update(model)
    return model_store.all_models[model]


class UserSession:
    def __init__(self, model: str, temperature: float, model_store: ModelStore):
        self.model_name = model
        self.model_store = model_store
        self.session_id = uuid4().hex
        self.model = get_model_from_store(model, self.model_store)
        self.temperature = temperature
    def update(self, model: str):
        model != self.model_name:
        self.model_name = model
        self.model = get_model_from_store(model, self.model_store)
    @property
    def info(self):
        return dict(
            session_id = self.session_id,
            model = self.model,
            temperature = self.temperature
        )


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

class ConversationStore:
    def __init__(self):
        self.conversations = {}
    def add_conversation(self, conversation_id: Tuple[str, str]):
        if conversation_id not in self.conversations.keys():
            self.conversations[conversation_id] = InMemoryHistory()
    @property
    def all_conversations(self):
        return self.conversations

def get_conversation_from_store(conversation_id: Tuple[str, str], conversation_store: ConversationStore):
    conversation_store.add_conversation(conversation_id)
    return conversation_store.all_conversations[conversation_id]

class UserChatModel:
    def __init__(self, user_session: UserSession, conversation_store: ConversationStore):
        self.session_id = user_session.info["session_id"]
        self.model = user_session.info["model"]
        self.temperature = user_session.info["temperature"]
        self.conversation_store = conversation_store
        self.output_parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_MESSAGE),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}"),
            ]
        )
        
    def get_session_history(self, session_id: str, temperature: float) -> BaseChatMessageHistory:
        return get_conversation_from_store(
            conversation_id = (session_id, temperature),
            conversation_store = self.conversation_store
        )



    def update(self):
        pass


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
