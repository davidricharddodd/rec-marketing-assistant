import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables from .env
load_dotenv()

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    agent_id = os.environ.get("ANTHROPIC_AGENT_ID")
    environment_id = os.environ.get("ANTHROPIC_ENVIRONMENT_ID")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file.")
        sys.exit(1)
    if not agent_id:
        print("Error: ANTHROPIC_AGENT_ID not found in .env file.")
        sys.exit(1)
    if not environment_id:
        print("Error: ANTHROPIC_ENVIRONMENT_ID not found in .env file.")
        sys.exit(1)

    print("--------------------------------------------------")
    print("REC Marketing Assistant - CLI Test Chat")
    print("--------------------------------------------------")
    print(f"Agent ID:       {agent_id}")
    print(f"Environment ID: {environment_id}")
    print("Initializing session...")

    # Initialize client
    client = Anthropic(api_key=api_key)

    try:
        session = client.beta.sessions.create(
            agent=agent_id,
            environment_id=environment_id,
            title="CLI interactive session",
        )
        print(f"Session established: {session.id}")
    except Exception as e:
        print(f"Error creating session: {e}")
        sys.exit(1)

    print("\nChat session is active. Type your messages below.")
    print("Type 'exit' or 'quit' to end the session.")
    print("==================================================")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting session. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Exiting session. Goodbye!")
            break

        print("Assistant: ", end="", flush=True)

        try:
            # Open the stream first
            with client.beta.sessions.events.stream(session.id) as stream:
                # Send the user message to the session
                client.beta.sessions.events.send(
                    session_id=session.id,
                    events=[{
                        "type": "user.message",
                        "content": [{"type": "text", "text": user_input}],
                    }],
                )

                # Process streamed events
                for event in stream:
                    # Check event type
                    if event.type == "agent.message":
                        # Print each text block in the message content
                        for block in event.content:
                            if hasattr(block, "text"):
                                print(block.text, end="", flush=True)
                            elif isinstance(block, dict) and "text" in block:
                                print(block["text"], end="", flush=True)
                    elif event.type == "agent.tool_use":
                        # Print when a tool is being called
                        tool_name = getattr(event, "name", "unknown")
                        print(f"\n[Tool Use: {tool_name}]", flush=True)
                    elif event.type == "session.status_idle":
                        # The agent has finished responding and is waiting for user input
                        break
                    elif event.type == "error":
                        print(f"\n[API Error: {event}]", flush=True)
                        break
        except Exception as e:
            print(f"\n[Stream Error: {e}]", flush=True)

if __name__ == "__main__":
    main()
