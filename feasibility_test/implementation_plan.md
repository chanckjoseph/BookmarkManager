# Bookmark Manager Plan

This plan outlines the development of a centralized bookmark manager that works across multiple browsers without requiring extensions or client-side installations.

## User Review Required

> [!IMPORTANT]
> **Constraint Check**: The "No Extension" constraint means we cannot automatically sync in the background like a native browser sync. We will rely on **Bookmarklets** for easy adding and **Import/Export** handling for bulk synchronization.
>
> **Tech Stack**: Proposed stack is Node.js + Express for backend and Vanilla JS/CSS (or a lightweight framework) for the frontend to keep it accessible and deployable anywhere.

## Features Provided

1.  **Universal Web Access**: Access bookmarks from any device with a browser.
2.  **No-Install Adding (Bookmarklet)**: A special "Add to Bookmarks" link that users drag to their bookmarks bar. Clicking it on any page instantly saves that page to the manager.
3.  **Bulk Import/Export**: Support for the standard Netscape Bookmark File Format (`.html`), allowing users to move bookmarks to/from Chrome, Firefox, Safari, and Edge.
4.  **Smart Metadata**: Automatically fetches the page title, description, and favicon when a link is added.
5.  **Organization**:
    -   **Tags**: Flexible categorization.
    -   **Search**: Full-text search of titles and URLs.
    -   **Folders**: Hierarchical structure (optional, tags are often better for flat management).
6.  **Clean Reader View (Optional)**: Extract text content for reading (future feature).

## User Experience (UX)

### Dashboard (The "Hub")
-   **Aesthetics**: Glassmorphism design, dark/light mode support, vibrant accent colors.
-   **Layout**: A responsive grid of "Cards" for bookmarks, showing the favicon, title, and a snippet of the description.
-   **Interactions**: Hover effects on cards, instant search filtering, easy edit/delete actions.

### The "Add" Flow
1.  **First Run**: User is presented with a "Drag this to your bookmarks bar" button (The Bookmarklet).
2.  **Adding a Site**:
    -   User is on `example.com`.
    -   User clicks the "Save Bookmark" bookmarklet.
    -   A small popup (iframe or new window) opens, confirms the save, allows tagging, and closes automatically.

### Mobile Experience
-   Fully responsive design.
-   Uses the native "Share" functionality on Android/iOS (via Web Share Target API if installed as PWA, or simple copy-paste if not).

## Architecture

## Architecture

### Tech Stack (Updated to Python)
-   **Frontend**:
    -   HTML5, CSS3 (Modern features: Grid, Flexbox, Variables), Vanilla JS.
    -   **Design System**: Custom "Rich Aesthetics" CSS (Glassmorphism, animations).
-   **Backend**:
    -   **Runtime**: **Python 3.11+**.
    -   **Framework**: **Flask** or **FastAPI**.
        -   *Decision*: Python is excellent for the "Metadata Fetcher" (scraping) component and offers great readability.
-   **Cloud Infrastructure (Google Cloud Run)**:
    -   **Compute**: Fully managed, stateless container (scales to zero).
    -   **Persistence**: **Google Cloud Firestore**.
    -   **Containerization**: Docker.

### Node.js vs. Python Decision
> **Why Python?**
> *   **Pros**: Excellent libraries for scraping (BeautifulSoup, Playwright) which is core to the "Smart Metadata" feature. Clean syntax.
> *   **Cons**: Slightly slower startup time (cold start) than Node.js, but minimal for this use case.
> *   **Node.js Comparison**: Node shares the language (JS) with the frontend, but Python is often preferred for data-heavy tasks. Given the requirement, Python is a robust choice.

### Data Model (Firestore Schema)
-   **Collection: `bookmarks`**
    -   Document ID: UUID
    -   Fields:
        -   `url`: String
        -   `title`: String
        -   `description`: String
        -   `favicon`: String (URL)
        -   `tags`: Array<String>
        -   `created_at`: Timestamp
        -   `folder`: String (Optional, for hierarchy)

### Key Components
1.  **Bookmarklet Handler**: Python endpoint.
2.  **Metadata Fetcher**: Python service using `BeautifulSoup` or `requests-html`.
3.  **Authentication**: Simple app-level auth or Google Identity Platform.

## Feasibility Test Plan (Immediate Next Step)
Before full implementation, we will deploy a "Hello World" connectivity test:
1.  **Goal**: Verify Cloud Run can talk to Firestore and serve a page.
2.  **App**: A single Python file (`main.py`) using Flask.
3.  **Action**:
    -   Deploy to Cloud Run.
    -   Visit URL.
    -   App writes a timestamp to Firestore.
    -   App reads it back and displays "Connectivity Verified: [Timestamp]".
4.  **Verification**: Confirm successful deployment and database write/read.

## Verification Plan

### Automated Tests
-   **Backend**: Unit tests for the Metadata Fetcher (mocking HTTP requests).
-   **API**: Integration tests for adding, retrieving, and deleting bookmarks.

### Manual Verification
-   **Bookmarklet Test**: Drag the bookmarklet to the bar, visit a site (e.g., `google.com`), click the bookmarklet, and verify it appears on the dashboard.
-   **Import Test**: Export bookmarks from Chrome, import them into the app, and verify count and data integrity.
-   **Responsiveness**: Open the dashboard on a mobile viewport and verify usability.
