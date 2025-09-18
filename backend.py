from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import BaseMessage, add_messages
from typing import TypedDict, List, Annotated
from langgraph.checkpoint.memory import InMemorySaver, MemorySaver #stores messages in ram
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

conn = sqlite3.connect('chatbot.db' , check_same_thread = False)

checkpointer = SqliteSaver(conn=conn)

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage],add_messages]


CONFIG = {'configurable':{'thread_id':'thread-1'}}

graph = StateGraph(ChatState)

def node1(state : ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages':[response]}

graph.add_node('node1',node1)

graph.add_edge(START,'node1')
graph.add_edge('node1',END)

workflow = graph.compile(checkpointer=checkpointer)


def retrieve_allthreads():
    all_thread = set()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        all_thread.add(thread_id)
    return list(all_thread)