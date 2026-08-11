import streamlit as st
import sqlite3
from sqlite3 import Error
import os
import difflib
import time

# --- Configuration ---
# For this MVP, admin authentication is simplified via environment variable ADMIN_PASSWORD
# In a real system, use a proper auth provider
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adm1npass")
FAQ_DB = "faq_data.db"

# Threshold for question similarity (0 to 1, higher is more strict)
SIMILARITY_THRESHOLD = 0.6

# --- Database Setup and Operations ---
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None


def init_db(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL UNIQUE,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
    except Error as e:
        st.error(f"DB init error: {e}")


def get_all_faqs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer, created_at, updated_at FROM faqs ORDER BY created_at DESC")
    return cursor.fetchall()


def get_faq_by_id(conn, faq_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, answer FROM faqs WHERE id = ?", (faq_id,))
    return cursor.fetchone()


def create_faq(conn, question, answer):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO faqs (question, answer) VALUES (?, ?)" , (question.strip(), answer.strip()))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Duplicate question not allowed."
    except Exception as e:
        return False, str(e)


def update_faq(conn, faq_id, question, answer):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE faqs SET question = ?, answer = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (question.strip(), answer.strip(), faq_id))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Duplicate question not allowed."
    except Exception as e:
        return False, str(e)


def delete_faq(conn, faq_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)

# --- FAQ Matching Logic ---
# Use difflib SequenceMatcher on lowercase stripped text for MVP
# Returns (best_match_answer, similarity_score) or (None, 0) if no match

def find_faq_answer(conn, visitor_question):
    all_faqs = get_all_faqs(conn)
    visitor_question = visitor_question.strip().lower()
    best_score = 0
    best_answer = None
    for faq in all_faqs:
        faq_question = faq[1].strip().lower()
        score = difflib.SequenceMatcher(None, visitor_question, faq_question).ratio()
        if score > best_score:
            best_score = score
            best_answer = faq[2]
    if best_score >= SIMILARITY_THRESHOLD:
        return best_answer, best_score
    return None, 0

# --- Streamlit Application UI and Logic ---

def admin_login():
    st.sidebar.title("Admin Login")
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

    # On app start or refresh, synchronize session state with query params for persistence and rerun triggers
    query_params = st.query_params

    # Use a special flag in query params '_admin' to force login persistence
    if query_params.get("_admin", [None])[0] == "true" and not st.session_state.admin_authenticated:
        st.session_state.admin_authenticated = True
        # On setting authenticated True from query params, remove _admin flag to avoid infinite loops
        new_params = dict(query_params)
        new_params.pop("_admin", None)
        st.experimental_set_query_params(**new_params)
        # Immediately rerun after setting auth session state
        st.rerun()

    if not st.session_state.admin_authenticated:
        password = st.sidebar.text_input("Enter Admin Password", type="password")
        if st.sidebar.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.sidebar.success("Logged in as Admin.")
                # Set query param to persist admin session and trigger UI update
                params = dict(st.query_params)
                params["_admin"] = "true"
                st.experimental_set_query_params(**params)
                # Trigger rerun to apply page changes
                st.rerun()
            else:
                st.sidebar.error("Incorrect password.")
        return False
    return True


def admin_faq_management(conn):
    st.title("FAQ & Knowledge Management - Admin Dashboard")

    st.markdown("Manage Frequently Asked Questions (FAQs) for your business assistant.\n"
                "Create, edit, or delete FAQs without modifying code.")

    tabs = st.tabs(["View FAQs", "Create FAQ", "Edit FAQ"])

    # --- View FAQs Tab ---
    with tabs[0]:
        st.subheader("View and Search FAQs")
        faqs = get_all_faqs(conn)

        search_query = st.text_input("Search FAQs")

        filtered_faqs = []
        if search_query.strip():
            sq = search_query.strip().lower()
            for faq in faqs:
                if sq in faq[1].lower() or sq in faq[2].lower():
                    filtered_faqs.append(faq)
        else:
            filtered_faqs = faqs

        if filtered_faqs:
            for faq in filtered_faqs:
                with st.expander(f"Q: {faq[1]}", expanded=False):
                    st.markdown(f"**Answer:** {faq[2]}")
                    st.markdown(f"*Created at:* {faq[3]}  |  *Updated at:* {faq[4]}")
                    if st.button(f"Delete FAQ ID {faq[0]}", key=f"delete_{faq[0]}"):
                        # Confirm dialog workaround: separate confirm widget
                        if "confirm_delete_" + str(faq[0]) not in st.session_state:
                            st.session_state["confirm_delete_" + str(faq[0])] = False

                        if not st.session_state["confirm_delete_" + str(faq[0])]:
                            if st.button(f"Confirm Delete FAQ ID {faq[0]}", key=f"confirmbtn_{faq[0]}"):
                                st.session_state["confirm_delete_" + str(faq[0])] = True
                        else:
                            success, err = delete_faq(conn, faq[0])
                            if success:
                                st.success("FAQ deleted successfully. Please refresh the page to update list.")
                                # Reset confirm state
                                st.session_state["confirm_delete_" + str(faq[0])] = False
                            else:
                                st.error(f"Error deleting FAQ: {err}")
        else:
            st.info("No FAQs found.")

    # --- Create FAQ Tab ---
    with tabs[1]:
        st.subheader("Create New FAQ")
        with st.form("create_faq_form"):
            question = st.text_input("Question", max_chars=300)
            answer = st.text_area("Answer", height=150)
            submitted = st.form_submit_button("Create FAQ")

            if submitted:
                if not question.strip() or not answer.strip():
                    st.error("Question and Answer are required.")
                else:
                    # Check duplicate question in database
                    existing = [faq for faq in get_all_faqs(conn) if faq[1].strip().lower() == question.strip().lower()]
                    if existing:
                        st.error("A FAQ with this exact question already exists.")
                    else:
                        success, err = create_faq(conn, question, answer)
                        if success:
                            st.success("FAQ created successfully. Please refresh to see it in the list.")
                        else:
                            st.error(f"Error creating FAQ: {err}")

    # --- Edit FAQ Tab ---
    with tabs[2]:
        st.subheader("Edit Existing FAQ")

        faqs = get_all_faqs(conn)
        faq_options = {f"{faq[0]} - {faq[1][:50]}": faq[0] for faq in faqs}
        if faq_options:
            selected = st.selectbox("Select FAQ to edit", options=list(faq_options.keys()))

            if selected:
                faq_id = faq_options[selected]
                faq = get_faq_by_id(conn, faq_id)
                if faq:
                    with st.form("edit_faq_form"):
                        edited_question = st.text_input("Question", value=faq[1], max_chars=300)
                        edited_answer = st.text_area("Answer", value=faq[2], height=150)
                        submitted = st.form_submit_button("Update FAQ")

                        if submitted:
                            if not edited_question.strip() or not edited_answer.strip():
                                st.error("Question and Answer are required.")
                            else:
                                # Check duplicate question excluding current FAQ
                                duplicates = [f for f in get_all_faqs(conn) if f[1].strip().lower() == edited_question.strip().lower() and f[0] != faq_id]
                                if duplicates:
                                    st.error("Another FAQ with this question already exists.")
                                else:
                                    success, err = update_faq(conn, faq_id, edited_question, edited_answer)
                                    if success:
                                        st.success("FAQ updated successfully. Please refresh to see changes.")
                                    else:
                                        st.error(f"Error updating FAQ: {err}")
        else:
            st.info("No FAQs available to edit.")

# Chatbot visitor interface
# Simulates the chatbot with FAQ integration and fallback to AI assistant
# For MVP, fallback AI assistant returns canned response

def visitor_chat_interface(conn):
    st.title("Spark AI Business Assistant")
    st.markdown("Ask your question, and our assistant will try to answer from the FAQ knowledge base first.\nIf no FAQ matches well, the AI assistant will reply.")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    def send_message():
        visitor_question = st.session_state.visitor_input.strip()
        if visitor_question == "":
            return

        st.session_state.chat_history.append({"role": "visitor", "text": visitor_question})

        # Start time to track response time
        start_time = time.time()

        # Try FAQ match first
        faq_answer, score = find_faq_answer(conn, visitor_question)

        response = ""
        if faq_answer:
            response = f"**Here’s something from our FAQ:**\n{faq_answer}"
        else:
            # Fallback: Simulated AI assistant response (static for MVP)
            response = "I'm sorry, I don't have an FAQ answer for that question. Let me get you an AI-generated response..."

        st.session_state.chat_history.append({"role": "assistant", "text": response})

        # Simulate small delay
        duration = time.time() - start_time
        if duration < 0.3:
            time.sleep(0.3 - duration)

        st.session_state.visitor_input = ""

    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "visitor":
                st.markdown(f"**Visitor:** {chat['text']}")
            else:
                st.markdown(f"**Assistant:** {chat['text']}")

    st.text_input("Your question", key="visitor_input", on_change=send_message)

# --- Main execution ---
def main():
    st.set_page_config(page_title="NordSparkAI Spark Assistant with FAQ", layout="wide")
    conn = create_connection(FAQ_DB)
    if conn is None:
        st.error("Unable to connect to database.")
        return
    init_db(conn)

    menu = st.sidebar.selectbox("Navigation", ["Visitor Chatbot", "Admin Dashboard"])

    if menu == "Admin Dashboard":
        if admin_login():
            admin_faq_management(conn)
        else:
            st.info("Please log in as Admin to manage FAQs.")
    else:
        visitor_chat_interface(conn)

if __name__ == "__main__":
    main()
