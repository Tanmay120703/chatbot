import streamlit as st 
from backend import workflow
from langchain_core.messages import HumanMessage

st.title("💬 AI Chatbot")
st.write("Type a message below to start chatting.")


if 'messages_history' not in st.session_state:
    st.session_state['messages_history'] = []

# Display past conversation
for message in st.session_state['messages_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Input box
user_input = st.chat_input('type here :')

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if user_input:
    # Save user message
    st.session_state['messages_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.markdown(user_input)

    # Get AI response
    response = workflow.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response['messages'][-1].content

    # Save AI response
    st.session_state['messages_history'].append({'role': 'assistant', 'content': ai_message})

    with st.chat_message('assistant'):
        st.markdown(ai_message)
