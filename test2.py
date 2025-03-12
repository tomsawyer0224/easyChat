from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.runnables import ConfigurableField

import asyncio

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
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
parser = StrOutputParser()
chain = prompt | model | parser

async def generate():
    chunks = []
    async for chunk in chain.astream({"topic": "parrot"}):
        # print(chunk, end="|", flush=True)
        chunks.append(chunk)
    print(chunks)
asyncio.run(generate())