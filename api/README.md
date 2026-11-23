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

### Browser origin configuration

With `CORS_ORIGIN` unset or blank, the local server allows browser reads from
`http://localhost:3000`. Set a comma-separated list of complete origins for a frontend
running elsewhere; surrounding whitespace and empty entries are ignored:

```bash
CORS_ORIGIN='http://localhost:5173,https://checklists.example.org' node server.js
```

Other browser origins receive no `Access-Control-Allow-Origin` header. Matching includes the
scheme, hostname and port. Requests without an `Origin` header continue to work normally.

Wildcard origins are rejected at startup; configure each permitted browser origin explicitly.
Credentialed CORS is not enabled. CORS controls browser access to responses; it does not
authenticate callers.

Run the regression tests with `npm test` from `api/`, using Node.js 24 as in CI.

### Request budget

Both checklist routes share a budget of **100 requests per client per 60 seconds**. The limiter
runs before JSON body parsing, corpus reads and Markdown conversion. Requests beyond the budget
receive `429` with a JSON error and a `Retry-After` header. `RateLimit` and `RateLimit-Policy`
describe the remaining budget and window; permitted browser origins can read these headers.
Successful requests, unknown IDs and invalid requests all consume the same budget.

Express retains its default `trust proxy: false`: forwarded-IP headers do not change the client
identity. IPv4 uses the socket address; IPv6 is grouped into `/56` subnets by the maintained
limiter. A deployment behind a proxy needs a reviewed, explicit proxy trust configuration before
using forwarded addresses. Do not enable blanket proxy trust.

The built-in memory store applies to one server process and resets when that process restarts.
Multiple workers or replicas need a shared store before claiming a deployment-wide budget. The
local clock/expiry regression advances a mocked clock; it does not sleep for a real minute.

`express-rate-limit` **8.7.5** is an MIT-licensed runtime dependency owned by the StandardFlow API
maintainer. It supplies the bounded counter, expiry, IPv6 keys and standard response headers.
Remove it when this local server is retired or an equivalent reviewed middleware replaces it;
the static GitHub Pages API does not use it. Exact package and transitive versions/integrity hashes
are retained in `package-lock.json`. Configuration follows the
[official documentation](https://express-rate-limit.mintlify.app/reference/configuration) and
[8.7.5 release](https://github.com/express-rate-limit/express-rate-limit/releases/tag/v8.7.5).

### Local API Endpoints

*   `GET /api/checklists`: Returns a list of all available checklists.
*   `GET /api/checklists/:id`: Returns a single checklist by its ID.

IDs use lowercase letters, digits and single hyphen separators, matching the corpus filenames.
Malformed IDs (including encoded path separators) return `400`; an unknown valid ID returns
`404`. Read failures return `500` without exposing filesystem details.
