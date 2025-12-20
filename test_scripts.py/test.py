from openrouter import OpenRouterClient

def test_openrouter_client_initialization():
    client = OpenRouterClient(system_prompt="Test prompt")

    response = client.chat(messages=[{"role": "user", "content": "Hello, how are you?"}])

    return response


if __name__ == "__main__":
    print(test_openrouter_client_initialization())


    