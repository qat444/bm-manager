
import json
import os
import re
import shutil
import time
from pathlib import Path

class BookmarkStorage:
    def __init__(self, filename="bookmarks.json"):
        script_dir = Path(__file__).parent
        self.filename = script_dir / filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({}, f)

    def _read_data(self):
        with open(self.filename, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _write_data(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def _get_next_id(self):
        data = self._read_data()
        if not data:
            return 1
        all_bookmarks = [b for topic_bookmarks in data.values() for b in topic_bookmarks]
        if not all_bookmarks:
            return 1
        return max(b['id'] for b in all_bookmarks) + 1

    def add_bookmark(self, url, title, topic, related_bookmarks=None):
        data = self._read_data()
        bookmark_id = self._get_next_id()
        
        new_bookmark = {
            "id": bookmark_id,
            "url": url,
            "title": title or url,
            "related_bookmarks": related_bookmarks or []
        }

        if topic not in data:
            data[topic] = []
        
        data[topic].append(new_bookmark)
        self._write_data(data)
        return bookmark_id

    def search_bookmarks(self, query, in_title=False, in_url=False, in_topic=False):
        data = self._read_data()
        results = []
        all_bookmarks = [(b, topic) for topic, bookmarks in data.items() for b in bookmarks]

        try:
            regex = re.compile(query, re.IGNORECASE)
        except re.error:
            # Fallback to simple search if regex is invalid
            query = query.lower()
            for bookmark, topic_name in all_bookmarks:
                if (not in_title and not in_url and not in_topic) or \
                   (in_title and query in bookmark['title'].lower()) or \
                   (in_url and query in bookmark['url'].lower()) or \
                   (in_topic and query in topic_name.lower()):
                    results.append({**bookmark, "topic": topic_name})
            return results

        for bookmark, topic_name in all_bookmarks:
            if (not in_title and not in_url and not in_topic) or \
               (in_title and regex.search(bookmark['title'])) or \
               (in_url and regex.search(bookmark['url'])) or \
               (in_topic and regex.search(topic_name)):
                results.append({**bookmark, "topic": topic_name})
        
        return results

    def list_bookmarks(self, topic=None):
        data = self._read_data()
        if topic:
            return data.get(topic, [])
        
        all_bookmarks = []
        for topic_name, bookmarks in data.items():
            for bookmark in bookmarks:
                all_bookmarks.append({**bookmark, "topic": topic_name})
        return all_bookmarks

    def list_topics(self):
        data = self._read_data()
        return list(data.keys())

    def delete_bookmark(self, bookmark_id):
        data = self._read_data()
        for topic, bookmarks in data.items():
            updated_bookmarks = [b for b in bookmarks if b['id'] != bookmark_id]
            if len(updated_bookmarks) < len(bookmarks):
                data[topic] = updated_bookmarks
                # If the topic is now empty, remove it
                if not data[topic]:
                    del data[topic]
                self._write_data(data)
                return True
        return False

    def edit_bookmark(self, bookmark_id, new_url=None, new_title=None, new_topic=None):
        data = self._read_data()
        for topic, bookmarks in data.items():
            for bookmark in bookmarks:
                if bookmark['id'] == bookmark_id:
                    if new_url:
                        bookmark['url'] = new_url
                    if new_title:
                        bookmark['title'] = new_title
                    
                    if new_topic and new_topic != topic:
                        # Move bookmark to a new topic
                        if new_topic not in data:
                            data[new_topic] = []
                        data[new_topic].append(bookmark)
                        bookmarks.remove(bookmark)
                        # If the old topic is now empty, remove it
                        if not bookmarks:
                            del data[topic]
                    
                    self._write_data(data)
                    return True
        return False
        
    def relate_bookmarks(self, id1, id2):
        data = self._read_data()
        bookmark1_found = False
        bookmark2_found = False

        all_bookmarks = [b for topic_bookmarks in data.values() for b in topic_bookmarks]

        for bookmark in all_bookmarks:
            if bookmark['id'] == id1:
                if id2 not in bookmark['related_bookmarks']:
                    bookmark['related_bookmarks'].append(id2)
                bookmark1_found = True
            if bookmark['id'] == id2:
                if id1 not in bookmark['related_bookmarks']:
                    bookmark['related_bookmarks'].append(id1)
                bookmark2_found = True
        
        if bookmark1_found and bookmark2_found:
            self._write_data(data)
            return True
        
        return False

    def backup_bookmarks(self):
        backup_filename = f"bookmarks_backup_{int(time.time())}.json"
        shutil.copy(self.filename, backup_filename)
        return backup_filename

    def export_bookmarks(self, export_format, filename):
        bookmarks = self.list_bookmarks()
        if export_format == "csv":
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "URL", "Title", "Topic", "Related IDs"])
                for b in bookmarks:
                    writer.writerow([b['id'], b['url'], b['title'], b['topic'], ','.join(map(str, b.get('related_bookmarks', [])))])
            return True
        elif export_format == "html":
            with open(filename, 'w') as f:
                f.write("<html><head><title>Bookmarks</title></head><body>")
                f.write("<h1>Bookmarks</h1>")
                for topic, topic_bookmarks in self._read_data().items():
                    f.write(f"<h2>{topic}</h2><ul>")
                    for b in topic_bookmarks:
                        related_str = f" (Related: {', '.join(map(str, b.get('related_bookmarks', [])))})" if b.get('related_bookmarks') else ""
                        f.write(f"<li><a href='{b['url']}'>{b['title']}</a>{related_str}</li>")
                    f.write("</ul>")
                f.write("</body></html>")
            return True
        return False
