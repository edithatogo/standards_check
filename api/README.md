# Checklist API

This project provides two ways to access checklist data programmatically: a local Node.js server for development and a pre-generated static JSON API for production use via GitHub Pages.

---

## 1. Static API (for Public Access)

For public, read-only access, this project generates static JSON files that are served via GitHub Pages. This is the recommended way to consume the checklist data in a production environment.

**Location:** The generated files are in the `/docs/api` directory.

**Endpoints:**
*   **Index:** `https://[your-github-username].github.io/standards_check/api/index.json`
    *   Returns a list of all available checklists with their IDs, titles, and types.
*   **Individual Checklist:** `https://[your-github-username].github.io/standards_check/api/[checklist-id].json`
    *   Returns the full data for a single checklist.

### Generating the Static API

To update the static JSON files after changing any markdown checklists, run the generation script from the project root:

```bash
# Make sure you have run `npm install` in the root directory first
./scripts/generate_api_data.js
```

---

## 2. Local Development Server

For developers working on a front-end that consumes this data, a local Node.js/Express server is provided. It reads directly from the markdown files, so changes are reflected immediately.

### Getting Started (Local Server)

1.  **Navigate to the API directory:**
    ```bash
    cd api
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Start the Server:**
    ```bash
    node server.js
    ```

The local API will be available at `http://localhost:3000`.

### Local API Endpoints

*   `GET /api/checklists`: Returns a list of all available checklists.
*   `GET /api/checklists/:id`: Returns a single checklist by its ID.