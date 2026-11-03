import os
from typing import List, Dict

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="AI Chat Assistant", page_icon="💬", layout="centered")
st.title("💬 AI Chat Application")
st.caption("A simple LLM-powered chat app with conversation history and custom instructions.")

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

with st.sidebar:
    st.header("Settings")
    system_prompt = st.text_area(
        "Custom instructions",
        value="You are a helpful, clear and friendly AI assistant.",
        height=130,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.1)
    max_tokens = st.slider("Maximum response tokens", 100, 1500, 500, 50)
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.warning("API key not found. Add OPENAI_API_KEY to your .env file or deployment secrets.")
    st.code("OPENAI_API_KEY=your_api_key_here\nOPENAI_MODEL=gpt-4o-mini", language="text")
    st.stop()

client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Keep the system message separate from stored conversation history.
    api_messages = [{"role": "system", "content": system_prompt}]
    api_messages.extend(st.session_state.messages)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=api_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                answer = response.choices[0].message.content or ""
                st.markdown(answer)

                usage = response.usage
                if usage:
                    st.caption(
                        f"Token usage — input: {usage.prompt_tokens}, "
                        f"output: {usage.completion_tokens}, total: {usage.total_tokens}"
                    )

        st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as exc:
        # Do not expose secrets or full request headers in the UI.
        st.error(f"Request failed: {type(exc).__name__}. Check your API key, model name, quota and network connection.")
        st.session_state.messages.pop()
