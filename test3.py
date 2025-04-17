from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults

from utils import save_graph

SYSTEM_MESSAGE = (
    "You are a helpful, respectful and honest assistant. "
    "Always answer as helpfully as possible, while being safe. "
    "Your answers should not include any harmful, unethical, "
    "racist, sexist, toxic, dangerous, or illegal content. "
    "Please ensure that your responses are socially unbiased and positive in nature."
    "\n\nIf a question does not make any sense, or is not factually coherent, "
    "explain why instead of answering something not correct. "
    "If you don't know the answer to a question, please don't share false information."
    "You don't need to use tool for every query, only use when searching current events."
)

llm = ChatOllama(model="llama3.2")
ddg_search = DuckDuckGoSearchResults(
    max_results=2
)
tools = [ddg_search]
graph = create_react_agent(
    model = llm,
    tools = [ddg_search],
    prompt = SYSTEM_MESSAGE,
    checkpointer = MemorySaver()
)
save_graph(graph, "chatbot.png")
config = {"configurable": {"thread_id": "1"}}
while True:
    user_input = input("What's up: ")
    if user_input == "q": break

    # The config is the **second positional argument** to stream() or invoke()!
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )
    for event in events:
        event["messages"][-1].pretty_print()
