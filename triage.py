import os
import re
from pathlib import Path
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# Load environment variables from .env
env_path = Path(__file__).resolve().parent / ".env"

def _load_env_fallback(path: Path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("\"'")
                    if k not in os.environ:
                        os.environ[k] = v

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
except ImportError:
    _load_env_fallback(env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in .env")

# Triage Prompt
TRIAGE_PROMPT = """You are a support ticket triage specialist for Shopify merchants.
Analyze the following merchant support message and categorize it into either 'billing' or 'orders'.

- billing: questions or issues regarding invoices, subscription plans, app charges, refunds for fees/charges, payment processing, and payouts.
- orders: questions or issues regarding customer orders, fulfillments, shipping labels, carrier tracking, customer address updates, and line-item refunds or cancellations.

Answer strictly on two labelled lines in this exact format:
Route: <billing or orders>
Reason: <one sentence pointing to what the merchant wrote>

Merchant Message:
{message_body}"""

class TriageState(TypedDict, total=False):
    message_body: str
    route: str
    reason: str

def triage(state: TriageState) -> dict:
    """Triage node that sends message_body to OpenRouter and extracts Route and Reason."""
    message_body = state.get("message_body", "")
    if not message_body:
        raise ValueError("Ticket message_body is empty.")

    llm = ChatOpenAI(
        model=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.0,
    )

    prompt = TRIAGE_PROMPT.format(message_body=message_body)
    response = llm.invoke(prompt)
    raw_content = response.content
    reply = raw_content if isinstance(raw_content, str) else str(raw_content)
    reply = reply.strip()

    route = None
    reason = None

    for line in reply.splitlines():
        line = line.strip()
        if line.lower().startswith("route:"):
            route = line.split(":", 1)[1].strip().lower()
        elif line.lower().startswith("reason:"):
            reason = line.split(":", 1)[1].strip()

    if not route:
        match = re.search(r"Route:\s*([a-zA-Z]+)", reply, re.IGNORECASE)
        if match:
            route = match.group(1).strip().lower()

    # Validate route strictly
    if route not in ("billing", "orders"):
        raise ValueError(
            f"Invalid route '{route}' received from model. Expected 'billing' or 'orders'. Full model reply:\n{reply}"
        )

    # Validate reason strictly
    if not reason:
        raise ValueError(
            f"Missing 'Reason:' line in model reply. Expected labelled 'Reason:' line. Full model reply:\n{reply}"
        )

    return {"route": route, "reason": reason}

# LangGraph single-node workflow
builder = StateGraph(TriageState)  # type: ignore[bad-specialization]
builder.add_node("triage", triage)
builder.add_edge(START, "triage")
builder.add_edge("triage", END)
graph = builder.compile()

if __name__ == "__main__":
    sample_ticket = {
        "message_body": "hi, I uninstalled the ReviewPop app on nov 8 because it was slowing down my product pages and I switched to a different one, but my bill this month still shows ReviewPop at $29. can you take that off or refund it please."
    }
    result = graph.invoke(sample_ticket)
    print("\nTriage Result:")
    print(f"Route : {result.get('route')}")
    print(f"Reason: {result.get('reason')}")

