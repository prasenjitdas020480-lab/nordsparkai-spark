import sys
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from core.chatbot import get_chatbot_response
from core.storage import load_config, save_lead


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="NordSparkAI AI Business Assistant",
    page_icon="🤖",
    layout="wide",
)


# ---------------------------------------------------------
# LOAD CONFIG
# ---------------------------------------------------------

config = load_config()
chatbot_config = config.get("chatbot", {})


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# QUICK ACTION BUTTONS
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "What can you do?",
        use_container_width=True,
    ):
        st.session_state.suggested_question = (
            "What can you do?"
        )

    if st.button(
        "Book a demo",
        use_container_width=True,
    ):
        st.session_state.show_demo_form = True


with col2:
    if st.button(
        "Show AI products",
        use_container_width=True,
    ):
        st.session_state.suggested_question = (
            "Show me your AI products."
        )

    if st.button(
        "Contact NordSparkAI",
        use_container_width=True,
    ):
        st.session_state.suggested_question = (
            "How can I contact NordSparkAI?"
        )


# ---------------------------------------------------------
# DEMO REQUEST FORM
# ---------------------------------------------------------

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

                st.error(
                    "Please enter your name and email."
                )

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


# ---------------------------------------------------------
# INITIALIZE CHAT
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------

typed_message = st.chat_input(
    "Ask Spark anything..."
)

user_message = typed_message or st.session_state.pop(
    "suggested_question",
    None,
)


# ---------------------------------------------------------
# PROCESS MESSAGE
# ---------------------------------------------------------

if user_message:

    # Save user message in chat history
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_message)

    # Generate Spark response
    with st.chat_message("assistant"):

        with st.spinner("Spark is thinking..."):

            try:

                # -----------------------------------------
                # CONVERSATION MEMORY
                # -----------------------------------------

                conversation_context = "\n".join(
                    f"{msg['role']}: {msg['content']}"
                    for msg in st.session_state.messages[-10:]
                )

                response = get_chatbot_response(
                    conversation_context
                )


                # -----------------------------------------
                # AUTOMATIC LEAD CAPTURE FROM CHAT
                # -----------------------------------------

                email_match = re.search(
                    r"[\w\.-]+@[\w\.-]+\.\w+",
                    user_message,
                )

                phone_match = re.search(
                    r"\b\d{8,15}\b",
                    user_message,
                )

                name_match = re.search(
                    r"(?:my name is|i am|i'm)\s+"
                    r"([A-Za-z][A-Za-z .'-]{1,50}?)"
                    r"(?=\s+(?:and|my email|email|phone|number)\b|,|$)",
                    user_message,
                    re.IGNORECASE,
                )


                # Only save when an email address is supplied
                if email_match:

                    captured_name = (
                        name_match.group(1).strip()
                        if name_match
                        else "Captured from Spark chat"
                    )

                    # Determine basic interest from conversation
                    context_lower = conversation_context.lower()

                    if "chatbot" in context_lower:
                        captured_requirement = (
                            "Interested in AI Website Chatbot / Demo"
                        )

                    elif "job hunter" in context_lower:
                        captured_requirement = (
                            "Interested in AI Job Hunter"
                        )

                    elif "automation" in context_lower:
                        captured_requirement = (
                            "Interested in AI Automation Solutions"
                        )

                    elif "business assistant" in context_lower:
                        captured_requirement = (
                            "Interested in AI Business Assistant"
                        )

                    else:
                        captured_requirement = (
                            "Lead captured from Spark conversation"
                        )

                    lead_data = {
                        "Name": captured_name,
                        "Company": "",
                        "Email": email_match.group(0),
                        "Phone": (
                            phone_match.group(0)
                            if phone_match
                            else ""
                        ),
                        "Requirement": captured_requirement,
                    }

                    save_lead(lead_data)


            except Exception as error:

                response = (
                    "Unable to respond right now: "
                    f"{error}"
                )


            # Display Spark response
            st.markdown(response)


    # -----------------------------------------------------
    # SAVE ASSISTANT MESSAGE TO CHAT HISTORY
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )