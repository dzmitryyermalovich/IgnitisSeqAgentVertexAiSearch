# deploy.py
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.adk.memory import VertexAiMemoryBankService
from ignity_agent.agent import root_agent  # adjust import path if needed

PROJECT        = "email-eso-agents-pilot"
LOCATION       = "europe-west1"
STAGING_BUCKET = "gs://adk_to_agent_engine_bucket"
RUNTIME_SA = "agent-engine-sa@email-eso-agents-pilot.iam.gserviceaccount.com"

vertexai.init(project=PROJECT, location=LOCATION, staging_bucket=STAGING_BUCKET)

app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=False,
)

# Deploy onto the existing engine (keeps its Memory Bank)
remote_app = agent_engines.create(
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]==1.120.0",
        "google-adk",
        "google-cloud-discoveryengine==0.13.12",
        "google-genai==1.43.0",
        "google-api-core==2.26.0",
        "pydantic==2.12.0",
        "pydantic-settings==2.11.0",
        "python-dotenv==1.1.1",
    ],
    service_account=RUNTIME_SA,
    extra_packages=["./ignity_agent"],
)

print("Deployment finished!")
print("Resource Name:", remote_app.resource_name)
print("Engine ID:", remote_app.resource_name.split("/")[-1])
