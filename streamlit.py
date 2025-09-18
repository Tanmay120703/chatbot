import streamlit as st
from app import workflow, retrieve_allthreads, save_thread_metadata
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime

def generate_threadid():
    return str(uuid.uuid4())

def clear_chat():
    thread_id = generate_threadid()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state['thread_id'] = thread_id
    save_thread_metadata(thread_id, timestamp)  # ✅ save in SQLite
    st.session_state['messages_history'] = []

def load_conversation(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get("messages", [])

# --- Initialize session state ---
if 'messages_history' not in st.session_state:
    st.session_state['messages_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_threadid()
    save_thread_metadata(st.session_state['thread_id'])  # ✅ store initial

if 'chat_thread' not in st.session_state:
    # load all saved threads with timestamps from SQLite
    st.session_state['chat_thread'] = retrieve_allthreads()

# Ensure current thread is tracked
save_thread_metadata(st.session_state['thread_id'])

# --- Sidebar UI ---
st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('new_chat'):
    clear_chat()

st.sidebar.header('My Conversations')
for thread in st.session_state['chat_thread']:
    label = f"[{thread['created_at']}] - {thread['id'][:8]}..."  # shorter ID
    if st.sidebar.button(label):
        st.session_state['thread_id'] = thread['id']
        messages = load_conversation(thread['id'])

        temp_messages = []
        for message in messages:
            role = 'user' if isinstance(message, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': message.content})

        st.session_state['messages_history'] = temp_messages

# --- Conversation UI ---
for msg in st.session_state['messages_history']:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

user_input = st.chat_input('type here :')

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

if user_input:
    st.session_state['messages_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        response_chunks = workflow.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        )

        for message_chunk, meta_data in response_chunks:
            full_response += message_chunk.content
            placeholder.markdown(full_response)

    # Save the complete response in history
    st.session_state['messages_history'].append({
        "role": "assistant", "content": full_response
    })
