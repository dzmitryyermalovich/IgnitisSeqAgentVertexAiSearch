import argparse
import os
import sys

from google import adk
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.adk.memory import VertexAiMemoryBankService

RESOURCE = "projects/804980146765/locations/europe-west1/reasoningEngines/1236889008596844544"
PROJECT  = "email-eso-agents-pilot"
LOCATION = "europe-west1"
appName = "1236889008596844544"
# Init Vertex AI with correct project + location
vertexai.init(project=PROJECT, location=LOCATION)


def create_session(resource_name: str, user_id: str) -> str:
    """Create a new session with the deployed agent."""
    app = agent_engines.get(resource_name)
    print(app)
    sess = app.create_session(user_id=user_id)
    print(sess)
    sid = sess["id"] if isinstance(sess, dict) else getattr(sess, "id", None)
    print("Created session:", sid)
    return sid


def send_message(resource_name: str, user_id: str, session_id: str, message: str) -> None:
    """Send a message to the deployed agent and print all responses."""
    remote_app = agent_engines.get(resource_name)

    print(f"\nSending message to session {session_id}:")
    print(f"Message: {message}")
    print("\nResponse:")
    for event in remote_app.stream_query(
        user_id=user_id,
        session_id=session_id,
        message=message,
    ):
        # event is usually a dict with 'content' → 'parts'
        if isinstance(event, dict):
            content = event.get("content", {})
            parts = content.get("parts", [])
            for p in parts:
                if "text" in p:
                    print(p["text"])
        else:
            print(event)  # fallback for unexpected formats

if __name__ == "__main__":
    # user = "Dzmitry Yermalovich"
    # user = "Igor Vasilev"
    # sid = create_session(RESOURCE, user)
    parser = argparse.ArgumentParser(description="Send a message to a deployed Vertex AI agent.")
    parser.add_argument("--message", required=True, help="Message to send to the agent")
    parser.add_argument("--session_id", required=True, help="Session ID to use")
    parser.add_argument("--user_id", default="Dzmitry Yermalovich", help="User ID (default: Dzmitry Yermalovich)")

    args = parser.parse_args()

    send_message(
        resource_name=RESOURCE,
        user_id=args.user_id,
        session_id=args.session_id,
        message=args.message,
    )
