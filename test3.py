from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "llama3.2:1b",
    temperature = 0.8,
    num_predict = 256,
    base_url = 'http://localhost:11434',
    verbose = True
)
messages = [
    ("system", "You are professional chatbot. Answer the user's question simply."),
    ("human", "explain multihead latent attention"),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)