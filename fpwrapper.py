import sys
import time
from concurrent import futures

import feedparser

class Feed(object):
    def __init__(self, feed_url: str):
        self.url = feed_url
        self.last_update = time.gmtime()
        self.etag = ""
        self.modified = ""

        # before first run of get_new_entries, pretend the feed is Gone
        self._nullupdate()

    def get_new_entries(self):
        try:
            # xml/rss parsing and feedparser are complex beasts
            d = feedparser.parse(self.url, etag=self.etag, modified=self.modified)
        except Exception as e:
            # so we just ignore anything that goes wrong with it
            # and worry about it later.
            return sys.exc_info()

        if d.get("status", None) == 301:
            # if the feed is permanently redirected, update the feed url
            self.url = d.get("href", self.url)
        if d.get("status", None) == 304:
            # if the server returns a Not Modified, return no entries
            # self.last_update is not changed as the feed may introduce entries created earlier than now in a later update
            return []
        if d.get("status", None) == 410:
            # if the feed is Gone, disable future feedparser calls
            self.get_new_entries = self._nullupdate
            return self._nullupdate()

        # populate entries with only those newer than the previous time the feed was updated
        entries = [ entry for entry in d.entries if entry.get("published_parsed", time.gmtime()) > self.last_update ]
        # update the last update time
        self.last_update = max([ entry.get("published_parsed", time.gmtime()) for entry in entries ], default=self.last_update)

        # update feed metadata
        self.metadata = {
            "title": d.feed.get("title", f"Untitled feed - {self.url}"),
            "subtitle": d.feed.get("subtitle", ""),
            "link": d.feed.get("link", self.url),
            "description": d.feed.get("description", "")
        }

        self.etag = d.get("etag", "")
        self.modified = d.get("modified", "")
        
        return entries

    def _nullupdate(self):
        self.metadata = {
            "title": f"Feed not found - {self.url}",
            "link": self.url,
        }
        return []

class FeedCollection(object):
    def __init__(self, feed_urls: list, max_workers:int=5):
        self.feeds = { url: Feed(url) for url in feed_urls }
        self.workers = max_workers
    
    def get_new_entries(self):
        with futures.ThreadPoolExecutor(max_workers=self.workers) as ex:
            fs = { url: ex.submit(feed.get_new_entries) for url, feed in self.feeds.items() }
            return { url: f.result() for url, f in fs.items() }
    
    def add_feed(self, feed_url: str):
        if feed_url in self.feeds:
            raise FeedCollectionError(feed_url, "The provided url has already previously been added")
        self.feeds[feed_url] = Feed(feed_url)
    
    def remove_feed(self, feed_url: str):
        if feed_url not in self.feeds:
            raise FeedCollectionError(feed_url, "The provided url does not exist in this FeedCollection")
        del self.feeds[feed_url]

class FeedCollectionError(Exception):
    def __init__(self, feed_url, message):
        self.feed_url = feed_url
        self.message = message