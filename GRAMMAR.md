# NAVI Command Grammar

This document outlines the grammar for the NAVI (Networked Administrative Visual Interface).

## General Syntax

`command [arguments...]`

---

### `add`

Fabricates a new connection (bookmark).

**Syntax:**
`add <url> [--title <title>] [--topic <topic>] [--related <id1> <id2> ...]`

-   `<url>`: The destination URI of the bookmark. (Required)
-   `--title <title>` or `-t <title>`: A descriptor for the link. If not provided, the URL will be used as the title.
-   `--topic <topic>` or `-c <topic>`: The classification layer for the bookmark. Defaults to "general".
-   `--related <id1> <id2> ...` or `-r <id1> <id2> ...`: Link this new bookmark to one or more existing connections by their IDs.

---

### `search`

Traverses the layers for a pattern.

**Syntax:**
`search <query> [--in-title] [--in-url] [--in-topic]`

-   `<query>`: The pattern to search for. Can be a regular expression.
-   `--in-title`: Restricts the search to bookmark titles.
-   `--in-url`: Restricts the search to bookmark URLs.
-   `--in-topic`: Restricts the search to topic names.

If no scope is specified, the search will be performed across titles and topics.

---

### `list`

Reveals all established connections.

**Syntax:**
`list [topic]`

-   `[topic]`: If provided, lists all connections within a specific classification layer. If omitted, lists all connections across all topics.

---

### `topics`

Lists all classification layers.

**Syntax:**
`topics`

---

### `delete`

Severs a connection.

**Syntax:**
`delete <id>`

-   `<id>`: The identifier of the connection to sever.

---

### `edit`

Modifies an existing connection.

**Syntax:**
`edit <id> [--url <url>] [--title <title>] [--topic <topic>]`

-   `<id>`: The identifier of the connection to modify.
-   `--url <url>`: The new destination URI.
-   `--title <title>`: The new descriptor.
-   `--topic <topic>`: The new classification layer. This will move the bookmark to the new topic.

---

### `relate`

Creates a relationship between two connections.

**Syntax:**
`relate <id1> <id2>`

-   `<id1>`: The first connection ID.
-   `<id2>`: The second connection ID.

This will create a bi-directional link between the two bookmarks.

---

### `backup`

Creates a data shadow (a backup of the bookmarks file).

**Syntax:**
`backup`

---

### `export`

Translates data to a different protocol.

**Syntax:**
`export <format> <filename>`

-   `<format>`: The target protocol. Can be `csv` or `html`.
-   `<filename>`: The name for the translated data file.

---

### `clear`

Refreshes the NAVI interface.

**Syntax:**
`clear`

---

### `help`

Displays the help message.

**Syntax:**
`help`

---

### `exit`

Closes the connection to the Wired.

**Syntax:**
`exit`
