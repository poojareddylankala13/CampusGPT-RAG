# Technical Plan: Authentication

## Architecture & Integration
- Database operations located in `modules/database.py` and `modules/auth.py`.
- Interactive login and registration interfaces located in `app.py`.

## Proposed Changes
- [MODIFY] `modules/auth.py` to ensure strict parameter typing.
- [MODIFY] `app.py` to handle session routing and views.

## Security & Type Safety Checks
- Use parameter and return type annotations for all methods in `modules/auth.py`.
- Validate hashing with `bcrypt`.
