# Feature Spec: Document Summarization

## User Stories
- As a student or faculty member, I want to generate a structured summary of long policy documents so that I can quickly extract key guidelines and dates.
- As a user, I want the summary generation to support both local GGUF models and cloud-based Gemini.

## Requirements
- [x] Requirement 1: Extract text from PDF documents.
- [x] Requirement 2: Format summaries with distinct sections (Executive Summary, Key Highlights, Important Dates, Policies & Guidelines, Action Items).
- [x] Requirement 3: Prune long document texts for local LLM contexts (e.g. 5000 characters limit).
- [x] Requirement 4: Stream summary generation tokens to the UI.

## Acceptance Criteria
- Given an uploaded document, when summarization is triggered, then render a markdown summary containing all five required sections.
- Given a long PDF document, when summarized locally, then limit input size to fit context length.
