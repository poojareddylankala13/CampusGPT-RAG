# Feature Spec: Authentication

## User Stories
- As a student or faculty member, I want to securely log in with my email and password so that I can access CampusGPT.
- As an administrator, I want to authenticate to access administrative management tools like document deletion and user listings.

## Requirements
- [x] Requirement 1: User registration with name, unique email, and hashed password (using `bcrypt`).
- [x] Requirement 2: Role-based access control (RBAC) with User and Admin roles.
- [x] Requirement 3: Streamlit session state integration for authentication state and auth guards.

## Acceptance Criteria
- Given the login page, when valid email and password are submitted, then log the user in and redirect to the dashboard.
- Given the registration page, when duplicate email is submitted, then show an error and block registration.
