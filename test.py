from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain_ollama import ChatOllama
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults

from utils import save_graph

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


llm = ChatOllama(model="llama3.2:1b")

ddg_search = DuckDuckGoSearchResults(
    max_results=2
)
tools = [ddg_search]
llm_with_tools = llm.bind_tools(tools)

# print(ddg_search.invoke("Who is prime minister of Canada?"))

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile(checkpointer=MemorySaver())


# save_graph(graph, "chatbot.png")
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


