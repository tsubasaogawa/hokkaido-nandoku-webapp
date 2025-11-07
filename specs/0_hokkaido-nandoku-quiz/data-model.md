# Data Model: Hokkaido Nandoku Quiz

This document outlines the data structures used for the Hokkaido Nandoku Quiz feature. As this is a stateless application, the model primarily defines the shape of data exchanged with the backend API.

## Entities

### Quiz

Represents a single quiz question.

- **`id`** (string): A unique identifier for the quiz question.
- **`name`** (string): The difficult-to-read place name (e.g., "札幌").
- **`options`** (array of strings): A list of four possible readings (e.g., `["さっぽろ", "さつぽろ", "さぶろ", "さごろ"]`).
- **`correct_answer`** (string): The correct reading (e.g., "さっぽろ").

## Relationships

- There are no persistent relationships between entities in this application. Each `Quiz` is retrieved and handled as a standalone object.

## State Transitions

- The application does not manage complex state transitions. The flow is a simple request-response cycle with the API for each quiz question.
