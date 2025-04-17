from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults

from langgraph_supervisor import create_supervisor

from utils import save_graph

CHAT_SYSTEM_MESSAGE = (
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

# SEARCH_SYSTEM_MESSAGE = (
#     "Your job is to identify key assumptions in a query and then form fact-checkable "
#     "questions which challenge these assumptions. "
#     "Your questions will be used to search in DuckDuckGo Search API with semantic search "
#     "capabilities (optimize accordingly). "
#     "The user will not see your searches - so do not address them. Keep assumptions concise. "
#     "Generate questions that question the foundational assumptions behind the user query. "
#     "Fact Checks should explore the basic existence or availability of the services or features mentioned in the question, "
#     "using varied wording and sentence structures to maximize search scope. "
# )
SEARCH_SYSTEM_MESSAGE = (
    "You are a powerful search engine and helpful in searching the current events."
)
llm = ChatOllama(model="llama3.2")

chat_agent = create_react_agent(
    model=llm,
    tools=[],
    name="chat_expert",
    prompt=CHAT_SYSTEM_MESSAGE
)

ddg_search = DuckDuckGoSearchResults(
    max_results=2
)
search_agent = create_react_agent(
    model=llm,
    tools=[ddg_search],
    name="search_expert",
    prompt=SEARCH_SYSTEM_MESSAGE
)

workflow = create_supervisor(
    [chat_agent, search_agent],
    model=llm,
    prompt=(
        "You are a team supervisor managing a chat expert and a search expert. "
        "For current events, use search_agent. "
        "For conversation, use chat_agent."
    )
)
graph = workflow.compile(checkpointer=MemorySaver())
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
