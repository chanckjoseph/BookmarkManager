# Smart Sync Logic Specification

## Core Philosophy
The Bookmark Manager acts as the **Static Source of Truth**. Browsers (Firefox, Chrome) are "Feeders". 
We aim for **Manual, Bulk Synchronization** where the user explicitly pulls the latest state from a browser.

**Key Rule**: 
> "We don't really need delete. We can mark as deleted, and the user can delete on our app manually if they really don't need it."

## The Sync Algorithm

When the user triggers a "Sync" from a specific browser profile (e.g., Firefox), the system performs a **Differential Analysis** against the internal database.

### 1. Matching Logic
We identify bookmarks primarily by their **Normalized URL**.
- **Normalization**: Strip trailing slashes, ignoring `http` vs `https` if needed (currently exact match), ignore query params? (MVP: Exact URL match).

### 2. Handling Incoming Items (The "Feed")
For every bookmark found in the Browser (Source):
1.  **Check Existence**: Does this URL exist in our DB?
2.  **Case A: NEW (URL not found)**
    -   **Action**: Create a `PendingChange` (Type: `new`).
    -   **Commit Result**: Insert new row into `bookmarks` table.
3.  **Case B: EXISTING (URL found)**
    -   **Check Consistency**: Does the Title or Folder Path match?
    -   **If Match**: **IGNORE**. (No change needed).
    -   **If Different**: Create a `PendingChange` (Type: `update`).
        -   **Commit Result**: Update the existing row's Title/Folder/Source metadata.

### 3. Handling Missing Items (The "Soft Delete")
For every bookmark in our DB that is associated with this Source (e.g., `source='firefox'`) but is **NOT** in the incoming list:
1.  **Case C: MISSING (Soft Delete)**
    -   **Action**: Create a `PendingChange` (Type: `mark_deleted`).
    -   **Commit Result**: 
        -   **Do NOT remove the row.**
        -   Update `status` column to `'absent_on_source'`.
        -   Update UI to visually dim/flag this item.
        -   User must explicitly click "Delete" in the App Dashboard to permanently remove it.

## Data States

| State | Description |
| :--- | :--- |
| `synced` | Item exists in both App and Browser. |
| `absent_on_source` | Item exists in App, but was deleted from Browser. (Soft Deleted) |
| `manual` | Item was added manually or from a file import. Ignored by Browser Sync. |

## User Workflow
1.  **Click Sync**: "Pull latest from Firefox".
2.  **Review**: See a list of changes:
    -   🟢 **[NEW]** 15 items
    -   🟡 **[UPDATE]** 3 items (Title changed)
    -   🔴 **[FLAGGED]** 2 items (Removed from Firefox)
3.  **Approve**: 
    -   New items are added.
    -   Updates are applied.
    -   Flagged items are marked as `absent_on_source` (but stay visible).
