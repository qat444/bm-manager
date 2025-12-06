# Bookmark Manager

A command-line tool for managing bookmarks in a JSON file.

## Features

- Add, delete, edit, and search for bookmarks.
- Organize bookmarks by topic.
- Automatic tagging of bookmarks based on website content.
- Hierarchical tags (manual and auto).
- Backup and export bookmarks.

## Usage

### Add a bookmark

The `add` command is flexible and can handle multi-word titles without quotes.

```bash
python BookmarkManager.py add http://example.com --title Example title with multiple words --topic testing --tags manual-tag-1 manual-tag-2
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
python BookmarkManager.py search "Example" --in-tags
```

### Edit a bookmark

```bash
python BookmarkManager.py edit 1 --title "A New Title" --tags new-manual-tag
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
