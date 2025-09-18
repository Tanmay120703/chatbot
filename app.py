from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import BaseMessage, add_messages
from typing import TypedDict, List, Annotated
from langgraph.checkpoint.memory import InMemorySaver, MemorySaver # stores messages in ram
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from datetime import datetime

# ----------------- DATABASE SETUP -----------------
conn = sqlite3.connect('chatbot.db', check_same_thread=False)
cursor = conn.cursor()

# Add new table for thread metadata (id + created_at)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS thread_meta (
        id TEXT PRIMARY KEY,
        created_at TEXT
    )
""")
conn.commit()

checkpointer = SqliteSaver(conn=conn)

load_dotenv()

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

graph = StateGraph(ChatState)

def node1(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}

graph.add_node('node1', node1)

graph.add_edge(START, 'node1')
graph.add_edge('node1', END)

workflow = graph.compile(checkpointer=checkpointer)

# ----------------- THREAD MANAGEMENT -----------------
def save_thread_metadata(thread_id: str, timestamp: str = None):
    """Save thread ID + timestamp into SQLite if not already present"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT OR IGNORE INTO thread_meta (id, created_at) VALUES (?, ?)", (thread_id, timestamp))
    conn.commit()

def retrieve_allthreads():
    """Fetch all threads with their timestamps"""
    cursor.execute("SELECT id, created_at FROM thread_meta ORDER BY created_at DESC")
    rows = cursor.fetchall()
    return [{"id": row[0], "created_at": row[1]} for row in rows]
