import requests


LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"


def generate(messages, temperature=0.0, max_tokens=1200):
    response = requests.post(
        LLAMA_URL,
        json={
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=300,
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"]