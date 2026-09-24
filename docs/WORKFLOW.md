# Workflow & Collaboration Guidelines

This document outlines the development workflow, coding standards, issue tracking, and pull request requirements for contributors and AI agents working on the MEOW repository.

---

## 1. Primary Language
- Use **English** across all GitHub issues, issue comments, pull requests, commit messages, code comments, and documentation.

---

## 2. GitHub Issues & Discussions
- Track all features, enhancements, and bug reports using GitHub Issues.
- When encountering ambiguous requirements, critical design choices, or edge cases, post clarifying comments on the relevant issue before finalizing implementations.

---

## 3. Pull Request (PR) Structure
Every pull request description must be written in Markdown and adhere to the following section structure:

### `## Summary`
- High-level overview of the issue or feature addressed.
- Reference related issues (e.g., `Closes #123`, `Resolves #456`, or `Related to #789`).

### `## Implementation`
- Detailed breakdown of technical changes and modified components.
- Rationale behind key implementation decisions.

### `## Acceptance`
- Verification results and test evidence.
- Clearly separate completed automated/manual checks from any pending event-level validation:
  - `- [x] Unit tests passed (e.g., test_doi_models.py)`
  - `- [ ] Alpha testing against live event data`

### `## Decisions`
- Record architectural choices, trade-offs, and backward-compatibility considerations.

---

## 4. Development & Testing Standards
- Maintain backward compatibility where applicable.
- Write unit tests for new features and bug fixes under the `tests/` directory.
- Verify tests pass locally with `pytest` before submitting pull requests.
- Adhere to PEP 8 styling conventions.
