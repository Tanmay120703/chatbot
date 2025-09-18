from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import BaseMessage, add_messages
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI()

CONFIG = {'configurable':{'thread_id':'thread-1'}}

checkpointer = MemorySaver()

class chatstate(TypedDict):
    messages : Annotated[List[BaseMessage], add_messages]

def node1(state : chatstate):
    message = state['messages']
    reponse = llm.invoke(message)
    return {'messages' : [reponse]}

graph = StateGraph(chatstate)

graph.add_node('node1',node1)

graph.add_edge(START, 'node1')
graph.add_edge('node1', END)

chatbot = graph.compile(checkpointer=checkpointer)

for message_chunk , meta_data in chatbot.stream(
    {'messages' : [HumanMessage(content='what is india')]},
    stream_mode='messages',
    config=CONFIG):

    if message_chunk.content:
        print(message_chunk.content, end=" ",flush=True)


