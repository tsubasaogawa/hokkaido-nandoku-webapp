# Tasks: Modern Quiz UI

**Branch**: `004-modern-quiz-ui` | **Spec**: [specs/004-modern-quiz-ui/spec.md](specs/004-modern-quiz-ui/spec.md)

## Implementation Strategy
- **Approach**: Refactor the existing `templates/index.html` in-place using a "Strangler Fig" approach where possible (add new styles/structure, then remove old), or a direct rewrite since the file is small.
- **MVP Scope**: User Story 1 (Responsive Layout) is the MVP. It ensures usability on mobile.
- **Testing**: Manual browser testing after each task using the local server (`uvicorn`).

## Dependencies
1. **Setup & Foundation** (Must be done first)
2. **User Story 1** (Responsive Layout)
3. **User Story 2** (Visual Feedback - depends on US1 structure)
4. **Polish**

## Phase 1: Setup
*Goal: Prepare the environment for frontend refactoring.*

- [x] T001 Verify local server runs and renders current quiz correctly (`uvicorn src.main:app --reload`).

## Phase 2: Foundation
*Goal: Establish the modern HTML shell and design system tokens.*

- [x] T002 Add `<meta name="viewport">` tag and import modern fonts (e.g., Google Fonts or system stack) in `templates/index.html`.
- [x] T003 Define CSS Variables for the "Hokkaido Nature" theme (colors, spacing, radius) in the `<style>` block of `templates/index.html`.
- [x] T004 Create the main responsive container structure (`.container`, `.quiz-card`) in `templates/index.html` to replace the raw `<body>` content.

## Phase 3: User Story 1 - Responsive & Accessible Layout
*Goal: Make the quiz usable on mobile devices with touch-friendly targets.*
*Priority: P1*

- [x] T005 [US1] Refactor answer options from plain radio buttons to `<label class="answer-card">` elements wrapping the input in `templates/index.html`.
- [x] T006 [US1] Implement CSS Grid/Flexbox layout for the answer options (stack on mobile, 2x2 grid on desktop) in `templates/index.html`.
- [x] T007 [US1] Style the "Submit" and "Next" buttons as large, primary action targets (min-height 44px) in `templates/index.html`.
- [x] T008 [US1] Ensure the question text (Kanji) is responsive and wraps correctly on small screens in `templates/index.html`.

## Phase 4: User Story 2 - Modern Visual Feedback
*Goal: Add interactivity and clear result states to improve UX.*
*Priority: P2*

- [x] T009 [US2] Implement CSS `:hover`, `:focus-within`, and `:checked` states for `.answer-card` (borders, background color changes) in `templates/index.html`.
- [x] T010 [US2] Create specific CSS classes for feedback states (`.correct`, `.incorrect`) with high-contrast colors in `templates/index.html`.
- [x] T011 [US2] Update the JavaScript `submitQuiz` function to apply these feedback classes to the result banner and/or selected card in `templates/index.html`.
- [x] T012 [US2] Add a simple transition/animation for the result appearance in `templates/index.html`.

## Phase 5: Polish & Cross-Cutting Concerns
*Goal: Final quality checks and cleanup.*

- [x] T013 Verify accessibility (tab navigation, aria-labels) and contrast ratios in `templates/index.html`.
- [x] T014 Remove any unused legacy CSS or inline styles from the original template in `templates/index.html`.
