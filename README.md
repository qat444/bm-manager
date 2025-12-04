# Bookmark Manager

A command-line tool for managing bookmarks in a JSON file.

## Features

- Add, delete, edit, and search for bookmarks.
- Organize bookmarks by topic.
- Backup and export bookmarks.

## Usage

### Add a bookmark

```bash
python BookmarkManager.py add "http://example.com" --title "Example" --topic "testing"
```

### List all bookmarks

```bash
python BookmarkManager.py list
```

### List bookmarks by topic

```bash
python BookmarkManager.py list --topic "testing"
```

### Search for a bookmark

```bash
python BookmarkManager.py search "Example"
```

### Edit a bookmark

```bash
python BookmarkManager.py edit 1 --title "A New Title"
```

### Delete a bookmark

```bash
python BookmarkManager.py delete 1
```

### Backup bookmarks

```bash
python BookmarkManager.py backup
```

### Export bookmarks to CSV

```bash
python BookmarkManager.py export csv bookmarks.csv
```

### Export bookmarks to HTML

```bash
python BookmarkManager.py export html bookmarks.html
```
