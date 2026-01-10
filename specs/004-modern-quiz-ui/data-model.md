# Data Model: Modern Quiz UI

## Backend Entities

### QuizResponse
*Returned by GET / (injected into template)*
- `id` (string): Unique identifier for the quiz/city.
- `name` (string): The question text (e.g., the Kanji place name).
- `options` (list[string]): List of 4 answer choices.
- `correct_answer` (string): The correct reading.

### AnswerRequest
*Sent by POST /*
- `quiz_id` (string): ID of the quiz.
- `correct_answer` (string): The expected answer.
- `answer` (string): The user's selected option.

### AnswerResponse
*Returned by POST /*
- `result` (enum): "correct" | "incorrect"
- `correct_answer` (string): The correct answer text.

## Frontend State (Ephemeral)

### QuizUIState
The frontend manages this state during the user session.

| Field | Type | Description |
|-------|------|-------------|
| `selectedOption` | string \| null | The currently selected answer option. |
| `isSubmitting` | boolean | True while API request is in flight. |
| `submissionResult` | object \| null | The result from the API. |
| `currentQuiz` | object | The injected `quizData`. |