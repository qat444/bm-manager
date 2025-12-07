
import json
import os
import re
import shutil
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import sys

# Add the site-packages path to sys.path for google.generativeai
sys.path.append(r"C:\Users\jordi\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages")

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

    def _generate_info_from_url(self, url):
        try:
            script_dir = Path(__file__).parent
            config_path = script_dir / 'config.json'

            with open(config_path, 'r') as f:
                config = json.load(f)
            
            gemini_api_key = config.get('gemini_api_key')

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            for script in soup(["script", "style"]):
                script.extract()

            text = ""
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'a', 'span', 'div', 'title']):
                text += element.get_text(separator=' ', strip=True) + ' '

            for meta in soup.find_all('meta'):
                if meta.get('name') == 'description':
                    text += meta.get('content', '') + ' '
                if meta.get('name') == 'keywords':
                    text += meta.get('content', '') + ' '

            if not text:
                return {}

            if gemini_api_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-pro-latest')
                prompt = f"Based on the following text from a website, please provide a suitable title, a single topic category, and a list of 5-10 relevant keywords. Return the result as a JSON object with keys 'title', 'topic', and 'tags'. For example: {{\"title\": \"Example Title\", \"topic\": \"Technology\", \"tags\": [\"keyword1\", \"keyword2\"]}}.\n\nText: {text[:2000]}"
                response = model.generate_content(prompt)
                
                # Clean the response text before parsing
                clean_response = response.text.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                
                try:
                    return json.loads(clean_response)
                except json.JSONDecodeError:
                    return {} # Return empty dict if JSON is malformed
            else:
                from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
                custom_stop_words = list(ENGLISH_STOP_WORDS) + [
                    "com", "disable", "fret", "privacy", "try", "login", "signup", "register", "home", "about", 
                    "contact", "search", "menu", "navigation", "share", "like", "follow", "copyright", "rights", 
                    "reserved", "policy", "terms", "conditions", "cookies", "settings", "preferences", "close", 
                    "accept", "decline", "manage", "continue", "next", "previous", "back", "more", "read", "view", 
                    "open", "new", "window", "tab", "email", "password", "username", "account", "profile", "edit", 
                    "save", "cancel", "submit", "send", "message", "subscribe", "unsubscribe", "download", "upload", 
                    "cart", "checkout", "buy", "sell", "price", "shipping", "returns", "support", "help", "faq", 
                    "blog", "news", "events", "jobs", "careers", "press", "investors", "partners", "api", "docs", 
                    "documentation", "forum", "community", "support", "feedback", "sitemap", "english", "espanol", 
                    "francais", "deutsch", "italiano", "portugues", "русский", "zhongwen", "nihongo", "hangukeo", 
                    "login", "log", "in", "out", "forgot", "your", "password", "remember", "me", "don't", "have", 
                    "an", "account", "create", "one", "by", "clicking", "here", "or", "connect", "with", "google", 
                    "facebook", "twitter", "linkedin", "github", "apple", "microsoft", "amazon"
                ]

                vectorizer = TfidfVectorizer(stop_words=custom_stop_words, max_features=5)
                vectorizer.fit_transform([text])
                tags = vectorizer.get_feature_names_out()
                return {"tags": list(tags)}
        except Exception as e:
            print(f"Error generating info for {url}: {e}")
            return {}

    def add_bookmark(self, url, title, topic, related_bookmarks=None, tags=None):
        if '://' not in url:
            url = 'https://' + url
        
        # Check for duplicates
        all_bookmarks = self.list_bookmarks()
        for bookmark in all_bookmarks:
            if bookmark['url'] == url:
                return None  # Duplicate found

        data = self._read_data()
        bookmark_id = self._get_next_id()
        
        generated_info = self._generate_info_from_url(url)
        auto_title = generated_info.get('title')
        auto_topic = generated_info.get('topic')
        auto_tags = generated_info.get('tags', [])

        final_title = title or auto_title or url
        
        # If the user provides a topic other than "general", use it.
        # Otherwise, use the auto-generated topic, or default to "general".
        if topic and topic != "general":
            final_topic = topic
        else:
            final_topic = auto_topic or "general"

        new_bookmark = {
            "id": bookmark_id,
            "url": url,
            "title": final_title,
            "related_bookmarks": related_bookmarks or [],
            "tags": {
                "manual": tags or [],
                "auto": list(auto_tags)
            }
        }

        if final_topic not in data:
            data[final_topic] = []
        
        data[final_topic].append(new_bookmark)
        self._write_data(data)
        return bookmark_id

    def search_bookmarks(self, query, in_title=False, in_url=False, in_topic=False, in_tags=False):
        data = self._read_data()
        results = []
        all_bookmarks = [(b, topic) for topic, bookmarks in data.items() for b in bookmarks]

        try:
            regex = re.compile(query, re.IGNORECASE)
        except re.error:
            # Fallback to simple search if regex is invalid
            query = query.lower()
            for bookmark, topic_name in all_bookmarks:
                tags = bookmark.get('tags', {})
                if isinstance(tags, dict):
                    manual_tags = tags.get('manual', [])
                    auto_tags = tags.get('auto', [])
                    all_tags = manual_tags + auto_tags
                else:
                    all_tags = tags
                if (not in_title and not in_url and not in_topic and not in_tags) or \
                   (in_title and query in bookmark['title'].lower()) or \
                   (in_url and query in bookmark['url'].lower()) or \
                   (in_topic and query in topic_name.lower()) or \
                   (in_tags and any(query in tag.lower() for tag in all_tags)):
                    results.append({**bookmark, "topic": topic_name})
            return results

        for bookmark, topic_name in all_bookmarks:
            tags = bookmark.get('tags', {})
            if isinstance(tags, dict):
                manual_tags = tags.get('manual', [])
                auto_tags = tags.get('auto', [])
                all_tags = manual_tags + auto_tags
            else:
                all_tags = tags
            if (not in_title and not in_url and not in_topic and not in_tags) or \
               (in_title and regex.search(bookmark['title'])) or \
               (in_url and regex.search(bookmark['url'])) or \
               (in_topic and regex.search(topic_name)) or \
               (in_tags and any(regex.search(tag) for tag in all_tags)):
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

    def delete_all_bookmarks(self):
        self._write_data({})
        return True

    def edit_bookmark(self, bookmark_id, new_url=None, new_title=None, new_topic=None, new_tags=None):
        data = self._read_data()
        for topic, bookmarks in data.items():
            for bookmark in bookmarks:
                if bookmark['id'] == bookmark_id:
                    if new_url:
                        if '://' not in new_url:
                            new_url = 'https://' + new_url
                        bookmark['url'] = new_url
                    if new_title:
                        bookmark['title'] = new_title
                    if new_tags:
                        bookmark['tags']['manual'] = new_tags
                    
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

    def find_duplicate_bookmarks(self):
        data = self._read_data()
        all_bookmarks = self.list_bookmarks()
        
        urls = {}
        for bookmark in all_bookmarks:
            url = bookmark['url']
            if url not in urls:
                urls[url] = []
            urls[url].append(bookmark['id'])
            
        duplicates = [ids for ids in urls.values() if len(ids) > 1]
        return duplicates

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
                writer.writerow(["ID", "URL", "Title", "Topic", "Manual Tags", "Auto Tags", "Related IDs"])
                for b in bookmarks:
                    tags = b.get('tags', {})
                    manual_tags = ','.join(tags.get('manual', []))
                    auto_tags = ','.join(tags.get('auto', []))
                    related_ids = ','.join(map(str, b.get('related_bookmarks', [])))
                    writer.writerow([b['id'], b['url'], b['title'], b['topic'], manual_tags, auto_tags, related_ids])
            return True
        elif export_format == "html":
            with open(filename, 'w') as f:
                f.write("<html><head><title>Bookmarks</title></head><body>")
                f.write("<h1>Bookmarks</h1>")
                for topic, topic_bookmarks in self._read_data().items():
                    f.write(f"<h2>{topic}</h2><ul>")
                    for b in topic_bookmarks:
                        tags = b.get('tags', {})
                        manual_tags_str = f" (Manual Tags: {', '.join(tags.get('manual', []))})" if tags.get('manual') else ""
                        auto_tags_str = f" (Auto Tags: {', '.join(tags.get('auto', []))})" if tags.get('auto') else ""
                        related_str = f" (Related: {', '.join(map(str, b.get('related_bookmarks', [])))})" if b.get('related_bookmarks') else ""
                        f.write(f"<li><a href='{b['url']}'>{b['title']}</a>{manual_tags_str}{auto_tags_str}{related_str}</li>")
                    f.write("</ul>")
                f.write("</body></html>")
            return True
        return False

    def get_bookmark_by_id(self, bookmark_id):
        all_bookmarks = self.list_bookmarks()
        for bookmark in all_bookmarks:
            if bookmark['id'] == bookmark_id:
                return bookmark
        return None

    def get_stats(self):
        data = self._read_data()
        total_bookmarks = sum(len(bookmarks) for bookmarks in data.values())
        total_topics = len(data)
        bookmarks_per_topic = {topic: len(bookmarks) for topic, bookmarks in data.items()}
        return {
            "total_bookmarks": total_bookmarks,
            "total_topics": total_topics,
            "bookmarks_per_topic": bookmarks_per_topic,
        }
