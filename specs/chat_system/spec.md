# Feature Spec: Chat System

## User Stories
- As a student, I want to chat with the AI assistant about course materials so that I can get immediate answers to my questions.
- As a user, I want to see citations and source materials referenced by the AI so that I can verify the information is correct.

## Requirements
- [x] Requirement 1: Conversational history rendering in user/assistant chat bubbles.
- [x] Requirement 2: Contextual query execution integrated with the RAG pipeline.
- [x] Requirement 3: Source citations with document name, page, and similarity score.
- [x] Requirement 4: User feedback (thumbs up/down) saved to SQLite.

## Acceptance Criteria
- Given a conversational history, when a user asks a new question, then the assistant answers within the context of previous messages and the database.
- Given an AI answer, when the user clicks feedback, then the database is updated with the rating.
