# A Guide to JSON for the NAVI System

This guide will walk you through the basics of JSON (JavaScript Object Notation) and how it's used in our NAVI bookmark management system. Understanding JSON will help you to better understand how your bookmarks are stored and managed.

## What is JSON?

JSON is a lightweight, human-readable format for structuring data. It's built on two basic structures:

-   **A collection of key-value pairs:** In various programming languages, this is realized as an *object*, *dictionary*, *hash table*, or *associative array*.
-   **An ordered list of values:** This is realized as an *array*, *list*, or *sequence*.

Our `bookmarks.json` file is essentially a database that uses these two structures to store your bookmarks in an organized way.

## Basic Syntax Rules

-   Data is in key-value pairs.
-   Data is separated by commas.
-   Curly braces `{}` hold objects.
-   Square brackets `[]` hold arrays.
-   Keys must be strings, in double quotes.
-   Values must be a valid JSON data type.

## JSON Data Types

| Data Type | Description                  | Example                      |
| :-------- | :--------------------------- | :--------------------------- |
| `String`  | Text, in double quotes.      | `"Hello, Present day."`      |
| `Number`  | An integer or floating-point.| `2023` or `3.14`             |
| `Boolean` | `true` or `false`.           | `true`                       |
| `Array`   | An ordered list of values.   | `[1, "two", true]`           |
| `Object`  | A collection of key-value pairs.| `{"name": "Lain", "age": 14}` |
| `null`    | Represents an empty value.   | `null`                       |

---

## The `bookmarks.json` Structure

Our system uses a topic-centric structure. The root of the JSON file is an **object**. Each **key** in this object is a **topic** name (as a string), and its corresponding **value** is an **array** of bookmark objects.

```json
{
  "topic_name_1": [
    // array of bookmark objects
  ],
  "topic_name_2": [
    // array of bookmark objects
  ]
}
```

### The Bookmark Object

Each bookmark is an **object** with the following key-value pairs:

-   `"id"`: A unique number to identify the bookmark.
-   `"url"`: The URL of the bookmark (a string).
-   `"title"`: The title of the bookmark (a string).
-   `"related_bookmarks"`: An array of numbers, where each number is the ID of a related bookmark.
-   `"tags"`: An object with two keys:
    -   `"manual"`: An array of strings, where each string is a tag you added manually.
    -   `"auto"`: An array of strings, where each string is a tag automatically generated from the website content.

---

## Examples

### 1. An Empty `bookmarks.json`

When you first start the program, the `bookmarks.json` file is an empty object:

```json
{}
```

### 2. Adding the First Bookmark

Let's say you add a bookmark to "lainchan.org" under the "wired" topic with a manual tag "imageboard".

**Command:** `add https://lainchan.org/ --title "LainChan" --topic wired --tags imageboard`

The `bookmarks.json` file will now look like this:

```json
{
    "wired": [
        {
            "id": 1,
            "url": "https://lainchan.org/",
            "title": "LainChan",
            "related_bookmarks": [],
            "tags": {
                "manual": [
                    "imageboard"
                ],
                "auto": [
                    "lain",
                    "chan",
                    "wired",
                    "anonymous",
                    "imageboard"
                ]
            }
        }
    ]
}
```

### 3. Adding More Bookmarks

Now, let's add a few more bookmarks.

**Command 1:** `add https://www.wired.com/ --title "Wired Magazine" --topic wired`
**Command 2:** `add https://kernel.org/ --title "Linux Kernel Archives" --topic development`

The `bookmarks.json` will be updated:

```json
{
    "wired": [
        {
            "id": 1,
            "url": "https://lainchan.org/",
            "title": "LainChan",
            "related_bookmarks": [],
            "tags": {
                "manual": [
                    "imageboard"
                ],
                "auto": [
                    "lain",
                    "chan",
                    "wired",
                    "anonymous",
                    "imageboard"
                ]
            }
        },
        {
            "id": 2,
            "url": "https://www.wired.com/",
            "title": "Wired Magazine",
            "related_bookmarks": [],
            "tags": {
                "manual": [],
                "auto": [
                    "wired",
                    "tech",
                    "science",
                    "culture",
                    "business"
                ]
            }
        }
    ],
    "development": [
        {
            "id": 3,
            "url": "https://kernel.org/",
            "title": "Linux Kernel Archives",
            "related_bookmarks": [],
            "tags": {
                "manual": [],
                "auto": [
                    "linux",
                    "kernel",
                    "git",
                    "development",
                    "open-source"
                ]
            }
        }
    ]
}
```
*Notice how the "wired" topic now has two bookmark objects in its array, and a new "development" topic has been created.*

### 4. Creating Relationships

Relationships help you connect ideas and links across different topics. Let's relate "LainChan" (ID 1) and "Wired Magazine" (ID 2).

**Command:** `relate 1 2`

Now, the `bookmarks.json` will be updated to reflect this relationship:

```json
{
    "wired": [
        {
            "id": 1,
            "url": "https://lainchan.org/",
            "title": "LainChan",
            "related_bookmarks": [2],
            "tags": {
                "manual": [
                    "imageboard"
                ],
                "auto": [
                    "lain",
                    "chan",
                    "wired",
                    "anonymous",
                    "imageboard"
                ]
            }
        },
        {
            "id": 2,
            "url": "https://www.wired.com/",
            "title": "Wired Magazine",
            "related_bookmarks": [1],
            "tags": {
                "manual": [],
                "auto": [
                    "wired",
                    "tech",
                    "science",
                    "culture",
                    "business"
                ]
            }
        }
    ],
    "development": [
        {
            "id": 3,
            "url": "https://kernel.org/",
            "title": "Linux Kernel Archives",
            "related_bookmarks": [],
            "tags": {
                "manual": [],
                "auto": [
                    "linux",
                    "kernel",
                    "git",
                    "development",
                    "open-source"
                ]
            }
        }
    ]
}
```
*The `related_bookmarks` array for both bookmarks now contains the ID of the other.*

This structured approach allows for efficient and meaningful management of your connections in the Wired. By understanding this JSON structure, you have a clearer picture of the data you are managing.
