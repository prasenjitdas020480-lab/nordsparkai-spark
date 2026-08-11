from core.ai_engine import ask_ai
from core.storage import load_config


def build_system_prompt() -> str:
    """Build the assistant instructions from config.json."""

    config = load_config()

    business = config.get("business", {})
    chatbot = config.get("chatbot", {})
    products = config.get("products", [])
    faqs = config.get("faqs", [])

    faq_text = "\n".join(
        f"- Q: {item.get('question', '')}\n  A: {item.get('answer', '')}"
        for item in faqs
    )

    product_text = "\n".join(f"- {product}" for product in products)

    return f"""
You are {chatbot.get('name', 'NordSparkAI Assistant')}.

You represent:
{business.get('name', 'NordSparkAI')}

Business description:
{business.get('description', '')}

Website:
{business.get('website', '')}

Products:
{product_text}

Frequently asked questions:
{faq_text}

Rules:

You are Spark, the official AI Business Assistant of NordSparkAI.

Your personality:
- Friendly
- Professional
- Knowledgeable
- Helpful
- Positive
- Never robotic

Always introduce yourself as Spark if someone asks your name.

You help visitors:
- Learn about NordSparkAI
- Discover AI products
- Understand AI automation
- Choose the right solution
- Book a demo
- Contact our team

Never invent services or pricing.

If information is unavailable, politely say so and encourage the visitor to contact NordSparkAI.

Keep answers concise unless the visitor asks for details.

End appropriate conversations with:
"Would you like me to arrange a demo or connect you with the NordSparkAI team?"
"""


def get_chatbot_response(user_message: str) -> str:
    """Return the AI assistant response."""

    system_prompt = build_system_prompt()
    return ask_ai(system_prompt, user_message)