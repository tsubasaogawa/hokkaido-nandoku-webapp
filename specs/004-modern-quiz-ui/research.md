# Research: Modern Quiz UI

## Technical Decisions

### 1. Frontend Technology
**Decision**: Vanilla JavaScript + Custom CSS (Inline/Internal)
**Rationale**:
- **Simplicity**: The project currently uses a single Jinja2 template (`index.html`). Introducing a build pipeline (Webpack/Vite) or a heavy framework (React/Vue) would complicate the deployment process (currently just copying files) and require significant refactoring of the backend to serve static assets or separate frontend hosting.
- **Performance**: A simple quiz app doesn't need the overhead of a framework. Vanilla JS is sufficient for the "fetch -> update DOM" cycle.
- **Maintenance**: Inline CSS (or a single `<style>` block) ensures that the styles are deployed atomically with the template, avoiding potential caching issues or path resolution issues in the Lambda URL environment where relative paths can be tricky without a proper static file server setup.

### 2. CSS Strategy
**Decision**: Custom CSS with CSS Variables
**Rationale**:
- **Theming**: The requirement calls for a specific "Hokkaido/Nature" palette. A generic framework (Bootstrap) would fight this or require overriding.
- **Responsiveness**: Flexbox and Grid in modern CSS make it easy to achieve the "Card" layout and mobile responsiveness without a grid framework.
- **Weight**: We can keep the CSS under 5-10KB, ensuring fast load times on mobile.

### 3. Visual Design (Hokkaido Theme)
**Decision**:
- **Primary Color**: `#0052A5` (Win-Winter Blue) or `#228B22` (Forest Green). Let's go with a snowy/nature mix.
- **Background**: `#F5F9FC` (Snow/Ice white-blue tint).
- **Cards**: White `#FFFFFF` with soft shadow `box-shadow: 0 4px 6px rgba(0,0,0,0.1)`.
- **Text**: `#333333` (Dark Gray) for readability, not pure black.
- **Feedback**:
    - Correct: `#2A9D8F` (Teal/Green).
    - Incorrect: `#E63946` (Red).

### 4. Interaction Design
**Decision**:
- **Input Method**: Clickable "Card" areas for answers (wrapping `<input type="radio">`).
- **Feedback Loop**:
    1. User clicks Answer Card -> Selected state (border highlight).
    2. User clicks "Answer" button -> Button loading state -> Result Card appears.
    3. Result Card shows "Correct/Incorrect" + "Next" button.
- **Accessibility**:
    - Use semantic `<fieldset>` and `<legend>` for the question group.
    - Ensure `:focus-visible` styles are present for keyboard navigation.

## Alternatives Considered

### A. CSS Framework (Bootstrap/Tailwind)
- **Rejected**: Bootstrap is too heavy and looks "generic" without heavy customization. Tailwind requires a build step (CLI) which isn't currently set up in the repo, or a CDN link which prevents purging unused styles (large file size).

### B. Single Page Application (React/Vue)
- **Rejected**: Would require setting up a separate build process and potentially separating the frontend deployment to S3+CloudFront, which changes the infrastructure significantly from the current "Lambda Function URL" single-endpoint model.

### C. HTMX
- **Rejected**: While HTMX is great for this, the current Vanilla JS is already working and minimal. Switching to HTMX would be a lateral move for code style but wouldn't inherently solve the "UI Design" requirement better than CSS + current JS.
