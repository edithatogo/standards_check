# Development Plan: Interactive Web Portal

This document outlines the plan for creating an interactive web portal for the reporting standards checklists.

## Suggested Approach: Static Site Generation with Client-Side Interactivity

The approach is to extend the existing build process to generate a static HTML website that can be hosted on GitHub Pages. All interactivity will be handled client-side with JavaScript.

### Advantages
*   **Leverages Existing Work:** Reuses `source/index.yml` and Markdown files.
*   **Low Maintenance:** No server or database required.
*   **Follows Project Conventions:** Integrates into the current `Makefile` and script-based build system.
*   **High Performance & Security:** Static sites are inherently fast and secure.

---

## Development Phases

### Phase 1: Static HTML Generation
1.  **Create an HTML Template:** Design a simple HTML5 template using a lightweight CSS framework (e.g., Bootstrap via CDN).
2.  **Update the Build Process:** Modify the `Makefile` to add a new `make html` command that uses `pandoc` to convert Markdown checklists into standalone HTML files.
3.  **Generate an Index Page:** Create a script (`scripts/generate_html_index.sh`) to read `source/index.yml` and generate a main `index.html` page listing all checklists.

### Phase 2: Client-Side Interactivity
- [x] **Add Interactive Elements:** Write a JavaScript file (`assets/js/app.js`) to dynamically transform list items into interactive elements (checkboxes, note fields).
- [x] **UI/UX Enhancements:** Add features like a progress bar to track completion.

### Phase 3: State Management (Saving Progress)
- [x] **Local Storage:** Use the browser's `localStorage` to automatically save user progress (checked items, notes).
- [x] **Export/Import Functionality:** Add buttons to export progress to a JSON file and import it back.

---

## Implementation Steps

- [x] Create a new directory `html/` to store the generated web portal.
- [x] Create a template file at `templates/pandoc/html_template.html`.
- [x] Create a new script `scripts/generate_html_index.sh`.
- [x] Modify the `Makefile` to implement the `html` build target.
