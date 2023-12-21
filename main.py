import gpt_assistant


def main():
    print(f"Assistant ID: {gpt_assistant.assistant_id}")

    while True:
        user_input = input("Enter your query (or type 'exit' to end): ")
        if user_input.lower() == 'exit':
            print("Exiting the Assistant.")
            break

        # Just call use_assistant with user_input
        gpt_assistant.use_assistant(user_input)

if __name__ == "__main__":
    main()
