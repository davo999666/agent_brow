import os

from langchain_openai import ChatOpenAI


def get_local_llm():
    return ChatOpenAI(
        base_url="http://127.0.0.1:1234/v1",
        api_key="lm-studio",
        model="qwen3.5-4b@q8_0",
        temperature=0.3,
        streaming=True,
        stream_usage=True,
    )

def get_local_vision_llm():
    return ChatOpenAI(
        base_url="http://127.0.0.1:1234/v1",
        api_key="lm-studio",
        model="qwen2.5-vl-3b-instruct",
        temperature=0.1,
        streaming=True,
        stream_usage=True,
    )


def get_openai_llm():
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-5",
        temperature=0.1,
        streaming=True,
        stream_usage=True,
    )