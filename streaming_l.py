import streamlit as st 
from backend import workflow, retrieve_allthreads
from langchain_core.messages import HumanMessage
import uuid



def generate_threadid():
    thread_id = uuid.uuid4()
    return thread_id

def clear_chat():
    thread_id = generate_threadid()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['messages_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_thread']:
        st.session_state['chat_thread'].append(thread_id)

def load_conversation(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get("messages", [])

if 'messages_history' not in st.session_state:
    st.session_state['messages_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_threadid()

if 'chat_thread' not in st.session_state:
    st.session_state['chat_thread'] = retrieve_allthreads()

add_thread(st.session_state['thread_id'])

st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('new_chat'):
    clear_chat()

st.sidebar.header('My Conversations')
for thread_id in st.session_state['chat_thread']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp_messages.append({'role':role , 'content':message.content})

        st.session_state['messages_history'] = temp_messages


for messages in  st.session_state['messages_history']:
    with st.chat_message(messages['role']):
        st.markdown(messages['content'])

user_input = st.chat_input('type here :')

CONFIG = {'configurable': {'thread_id' : st.session_state['thread_id']}}

if user_input:
    st.session_state['messages_history'].append({'role' : 'user' , 'content' : user_input})

    with st.chat_message('user'):
        st.markdown(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream  (message_chunk.content for message_chunk , meta_data in workflow.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        ))

    st.session_state['messages_history'].append({'role':'assistant', 'content':ai_message})