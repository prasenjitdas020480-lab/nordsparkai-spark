import streamlit as st

from core.storage import load_config, save_config


st.set_page_config(
    page_title="Business Settings",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Business Settings")
st.caption(
    "Update the business information and assistant settings "
    "without changing the code."
)

config = load_config()

business = config.get("business", {})
chatbot = config.get("chatbot", {})
products = config.get("products", [])


tab1, tab2, tab3 = st.tabs(
    [
        "🏢 Business Information",
        "🤖 Assistant Settings",
        "📦 Products",
    ]
)


# ---------------------------------------------------------
# BUSINESS INFORMATION
# ---------------------------------------------------------

with tab1:
    st.subheader("Business Information")

    with st.form("business_settings_form"):
        business_name = st.text_input(
            "Business Name",
            value=business.get("name", ""),
        )

        website = st.text_input(
            "Website",
            value=business.get("website", ""),
        )

        email = st.text_input(
            "Contact Email",
            value=business.get("email", ""),
        )

        phone = st.text_input(
            "Phone Number",
            value=business.get("phone", ""),
        )

        address = st.text_input(
            "Business Address",
            value=business.get("address", ""),
        )

        description = st.text_area(
            "Business Description",
            value=business.get("description", ""),
            height=150,
        )

        save_business = st.form_submit_button(
            "💾 Save Business Information",
            use_container_width=True,
        )

        if save_business:
            if not business_name.strip():
                st.error("Business name is required.")
            else:
                config["business"] = {
                    "name": business_name.strip(),
                    "website": website.strip(),
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "address": address.strip(),
                    "description": description.strip(),
                }

                try:
                    save_config(config)
                    st.success(
                        "Business information saved successfully."
                    )
                except Exception as error:
                    st.error(
                        f"Unable to save business information: {error}"
                    )


# ---------------------------------------------------------
# ASSISTANT SETTINGS
# ---------------------------------------------------------

with tab2:
    st.subheader("Assistant Settings")

    with st.form("assistant_settings_form"):
        assistant_name = st.text_input(
            "Assistant Name",
            value=chatbot.get("name", "Spark"),
        )

        assistant_title = st.text_input(
            "Assistant Title",
            value=chatbot.get(
                "title",
                "Your AI Business Assistant",
            ),
        )

        welcome_message = st.text_area(
            "Welcome Message",
            value=chatbot.get(
                "welcome_message",
                "Hello! How can I help you today?",
            ),
            height=160,
        )

        fallback_message = st.text_area(
            "Fallback Message",
            value=chatbot.get(
                "fallback_message",
                (
                    "I do not have that information yet. "
                    "Please contact our team for assistance."
                ),
            ),
            height=120,
        )

        save_assistant = st.form_submit_button(
            "💾 Save Assistant Settings",
            use_container_width=True,
        )

        if save_assistant:
            if not assistant_name.strip():
                st.error("Assistant name is required.")
            else:
                config["chatbot"] = {
                    "name": assistant_name.strip(),
                    "title": assistant_title.strip(),
                    "welcome_message": welcome_message.strip(),
                    "fallback_message": fallback_message.strip(),
                }

                try:
                    save_config(config)
                    st.success(
                        "Assistant settings saved successfully."
                    )
                except Exception as error:
                    st.error(
                        f"Unable to save assistant settings: {error}"
                    )


# ---------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------

with tab3:
    st.subheader("Products and Services")

    st.info(
        "Enter one product or service per line."
    )

    products_text = st.text_area(
        "Products",
        value="\n".join(products),
        height=250,
    )

    if st.button(
        "💾 Save Products",
        use_container_width=True,
    ):
        updated_products = [
            product.strip()
            for product in products_text.splitlines()
            if product.strip()
        ]

        config["products"] = updated_products

        try:
            save_config(config)
            st.success("Products saved successfully.")
        except Exception as error:
            st.error(f"Unable to save products: {error}")


st.divider()

st.caption(
    "Changes are stored in data/config.json and will be used "
    "by Spark automatically."
)