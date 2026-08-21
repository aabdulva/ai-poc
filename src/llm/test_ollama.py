from ollama import chat


def main():

    response = chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": "Explain what a software test failure is in one sentence."
            }
        ],
    )

    print()
    print("======================================")
    print("Ollama Test")
    print("======================================")
    print()

    print(response.message.content)


if __name__ == "__main__":
    main()