# Specification: User Authentication and Authorization

---

## 1. Purpose
Allows users to securely register accounts, sign in, manage active sessions, and restrict access to privileged layouts (such as the admin panel) based on roles.

---

## 2. Functional Requirements
*   **Registration**: Users can register with a name, unique email, and password.
*   **Hashing**: Passwords must be hashed using a strong salting algorithm (`bcrypt`).
*   **Authentication**: Users can authenticate with registered credentials, creating an active Streamlit session state.
*   **RBAC**: Regular users have access to query and chat dashboards, while administrative users (`admin` role) have exclusive access to document deletion and user listings.
*   **Auth Guard**: Unauthenticated session states automatically redirect users back to the login screen.

---

## 3. Inputs
*   **Registration**: `name` (string), `email` (string), `password` (string).
*   **Login**: `email` (string), `password` (string).

---

## 4. Outputs
*   **Registration**: Status string (`"success"`, `"exists"`, or `"error"`).
*   **Login**: User dictionary containing `id`, `name`, `email`, `role`, and `created_at` on successful authentication; `None` on failure.

---

## 5. Dependencies
*   Python standard SQLite library (`sqlite3`).
*   `bcrypt` hashing package.
*   Streamlit session state (`st.session_state`).

---

## 6. Error Handling
*   Attempts to register duplicate emails return `"exists"` and prevent database entry.
*   Invalid login combinations return `None` and display non-revealing error alerts (e.g. "Invalid email or password").
*   Database connection errors are logged and caught gracefully without crashing the UI.

---

## 7. Future Improvements
*   Implement JWT tokens for distributed auth management.
*   Integrate OAuth2 / SAML providers (e.g., Google OAuth, Microsoft Active Directory).
*   Add password reset workflows with email tokens.
