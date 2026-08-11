# NordSparkFAQ - FAQ & Knowledge Management Feature for Spark AI Business Assistant

## Overview

NordSparkFAQ enhances the existing Spark AI Business Assistant by enabling Business Admins to manage a FAQ knowledge base via a secured Admin Dashboard. The visitor chatbot first attempts to answer questions using stored FAQs, falling back to the AI assistant if no FAQ matches. This MVP supports create, read, update, delete (CRUD) operations on FAQs without code changes.

---

## Features

- Admin Login (password-protected via environment variable)
- Admin Dashboard:
  - List, search, view FAQs
  - Create new FAQs (with duplicate question prevention)
  - Edit existing FAQs
  - Delete FAQs (with confirmation)
- Visitor Chatbot:
  - Query FAQ knowledge base for answers
  - Respond with best matched FAQ answer within a similarity threshold
  - Fallback to AI assistant for unmatched questions (stub response)

---

## Limitations & Known Issues

- Admin authentication uses a simple password environment variable; no multi-user support.
- FAQ answers are plain text only (no rich text or formatting).
- No tagging, categories, or version history for FAQs.
- Matching algorithm is a basic string similarity (difflib) which may not capture semantic intent.
- No automatic live refresh of the admin page after create/edit/delete; please refresh manually to see updated lists.
- No deployment automation — changes require manual code promotion.
- AI assistant fallback is simulated/stubbed.

- **Fixed:** Admin login now immediately displays the FAQ management dashboard without requiring manual refresh.
- **Fixed:** Admin login session persists across browser refresh, maintaining access to the dashboard.
- **Fixed:** Deprecated st.experimental_rerun() calls replaced with supported rerun method to prevent app crashes.
- **Fixed:** Deprecated st.experimental_get_query_params() and st.experimental_set_query_params() replaced with current st.query_params API usage.

---

## Setup Instructions

1. **Prerequisites:**
   - Python 3.9 or later installed
   - Recommended to use a virtual environment

2. **Clone or Download this package**

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set Admin Password:**

Set environment variable `ADMIN_PASSWORD` to secure the admin dashboard.

On macOS/Linux terminal:
```bash
export ADMIN_PASSWORD="your_secure_password"
```
On Windows CMD:
```cmd
set ADMIN_PASSWORD=your_secure_password
```

If not set, the default password is `adm1npass` (not recommended for production).

5. **Run the application:**

```bash
streamlit run app.py
```

6. **Access URLs:**

- Visitor chatbot UI: Default main page "Spark AI Business Assistant"
- Admin Dashboard: Select "Admin Dashboard" from the sidebar, enter admin password

---

## Usage

### Admin Dashboard

- Log in with the admin password.
- Use tabs for viewing FAQs, creating new FAQs, and editing existing FAQs.
- Use search on the View FAQs tab to filter FAQs.
- Create new FAQs by entering a question and answer. Duplicates are prevented.
- Edit FAQs by selecting one and modifying the question or answer.
- Delete FAQs with confirmation to remove outdated or irrelevant questions.

### Visitor Chatbot

- Visitors enter questions in the chatbot text input.
- FAQs are matched by similarity; if matched, the FAQ answer is shown prefixed with "Here's something from our FAQ:".
- If no FAQ is matched well, the chatbot returns a fallback AI assistant message.

---

## Development and Deployment Notes

- The FAQ data is stored in a local SQLite database file `faq_data.db` for simplicity.
- The matching algorithm uses `difflib.SequenceMatcher` for basic similarity scoring.
- For future improvements:
  - Replace duplicate admin password login with full authentication system.
  - Implement semantic search or vector embeddings for improved matching.
  - Add FAQ tags, categories, and search filters.
  - Add rich text or markdown support for answers.
  - Add analytics on FAQ usage.
  - Automate deployment processes to publish FAQ changes.

---

## Security Considerations

- Keep the admin password secret and change the default immediately.
- Restrict access and deployment environment to trusted personnel.
- Consider integrating OAuth or other secure authentication for admin access in future releases.

---

## Support

For questions or feature requests, please contact the NordSparkAI development team.

Thank you for using NordSparkFAQ.

---

## Call to Action

### Business Admins  
**Build Smarter Customer Support with NordSparkAI**  
Unlock the power of efficient FAQ management directly from your Admin Dashboard. Take control of your customer support knowledge base without relying on engineering resources.

### Business Leaders / Founders  
Drive innovation and customer satisfaction by leveraging AI-powered knowledge management integrated seamlessly with your existing chatbot and lead-capture tools. Empower your teams to deliver consistent and accurate customer interactions at scale.
