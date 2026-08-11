import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
    
import streamlit as st

from core.chatbot import get_chatbot_response
from core.storage import load_config, save_lead


st.set_page_config(
    page_title="NordSparkAI AI Business Assistant",
    page_icon="🤖",
    layout="wide",
)

config = load_config()
chatbot_config = config.get("chatbot", {})

st.title("🤖 Spark")
st.subheader("Your AI Business Assistant")
st.caption("Powered by NordSparkAI")

st.info(
    """
🚀 Discover AI Products

💬 AI Website Chatbots

⚙️ Business Automation

📅 Book a Demo or Consultation
"""
)

st.markdown("### What can Spark help you with?")

col1, col2 = st.columns(2)

with col1:
    if st.button("What can you do?", use_container_width=True):
        st.session_state.suggested_question = "What can you do?"

    if st.button("Book a demo", use_container_width=True):
        st.session_state.show_demo_form = True

with col2:
    if st.button("Show AI products", use_container_width=True):
        st.session_state.suggested_question = "Show me your AI products."

    if st.button("Contact NordSparkAI", use_container_width=True):
        st.session_state.suggested_question = (
            "How can I contact NordSparkAI?"
        )

if st.session_state.get("show_demo_form", False):
    st.markdown("### 📅 Book a Demo")

    with st.form("demo_request_form"):
        name = st.text_input("Name")
        company = st.text_input("Company")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        requirement = st.text_area(
            "What would you like help with?"
        )

        submitted = st.form_submit_button(
            "Request Free Demo"
        )

        if submitted:
            if not name.strip() or not email.strip():
                st.error("Please enter your name and email.")
            else:
                lead_data = {
                    "Name": name.strip(),
                    "Company": company.strip(),
                    "Email": email.strip(),
                    "Phone": phone.strip(),
                    "Requirement": requirement.strip(),
                }

                try:
                    save_lead(lead_data)
                    st.success(
                        "Thank you! The NordSparkAI team "
                        "will contact you soon."
                    )
                    st.session_state.show_demo_form = False
                except Exception as error:
                    st.error(
                        f"Unable to save your request: {error}"
                    )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": chatbot_config.get(
                "welcome_message",
                "Hello! How can I help you today?",
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

typed_message = st.chat_input("Ask Spark anything...")

user_message = typed_message or st.session_state.pop(
    "suggested_question",
    None,
)

if user_message:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Spark is thinking..."):
            try:
                conversation_context = "\n".join(
                    f"{msg['role']}: {msg['content']}"
                    for msg in st.session_state.messages[-10:]
                )
                response = get_chatbot_response(
                    conversation_context
                    )
            except Exception as error:
                response = (
                    "Unable to respond right now: "
                    f"{error}"
                )

            st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )