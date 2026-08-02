"""
Web tools — search, fetch pages, and global news briefings.
"""

import httpx
import xml.etree.ElementTree as ET
import asyncio  # Required for parallel execution
import re
from datetime import datetime
import sys
import webbrowser

async def open_url_and_restore_focus(url: str):
    """
    Opens a URL in a new browser window/tab and restores focus to the previously
    active window on Windows, so the user can continue their interaction/prompt.
    """
    hwnd = None
    is_windows = sys.platform == "win32"
    
    if is_windows:
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
        except Exception:
            pass

    def _open():
        try:
            webbrowser.open_new(url)
        except Exception:
            try:
                webbrowser.open(url)
            except Exception:
                pass

    await asyncio.to_thread(_open)

    if is_windows and hwnd:
        await asyncio.sleep(0.8)
        try:
            import ctypes
            ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

SEED_FEEDS = [
    'https://feeds.bbci.co.uk/news/world/rss.xml',
    'https://www.cnbc.com/id/100727362/device/rss/rss.html',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.aljazeera.com/xml/rss/all.xml'
]

FINANCE_SEED_FEEDS = [
    'https://www.cnbc.com/id/10000664/device/rss/rss.html',
    'https://feeds.bloomberg.com/markets/news.rss',
    'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best',
    'https://feeds.marketwatch.com/marketwatch/topstories/',
    'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',
]

async def fetch_and_parse_feed(client, url):
    """Helper function to handle a single feed request and parse its XML."""
    try:
        response = await client.get(url, headers={'User-Agent': 'TARA-AI/1.0'}, timeout=5.0)
        if response.status_code != 200:
            return []

        root = ET.fromstring(response.content)
        source_name = url.split('.')[1].upper()
        
        feed_items = []
        items = root.findall(".//item")[:5]
        for item in items:
            title = item.findtext("title")
            description = item.findtext("description")
            link = item.findtext("link")
            
            if description:
                description = re.sub('<[^<]+?>', '', description).strip()

            feed_items.append({
                "source": source_name,
                "title": title,
                "summary": description[:200] + "..." if description else "",
                "link": link
            })
        return feed_items
    except Exception:
        return []

def register(mcp):

    @mcp.tool()
    async def get_world_news() -> str:
        """
        Fetches the latest global headlines from major news outlets simultaneously.
        Use this when the user asks 'What's going on in the world?' or for recent events.
        """
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            tasks = [fetch_and_parse_feed(client, url) for url in SEED_FEEDS]
            results_of_lists = await asyncio.gather(*tasks)
            all_articles = [item for sublist in results_of_lists for item in sublist]

        if not all_articles:
            return "The global news grid is unresponsive. I'm unable to pull headlines."

        report = ["### GLOBAL NEWS BRIEFING (LIVE)\n"]
        for entry in all_articles[:12]:
            report.append(f"**[{entry['source']}]** {entry['title']}")
            report.append(f"{entry['summary']}")
            report.append(f"Link: {entry['link']}\n")

        return "\n".join(report)

    @mcp.tool()
    async def get_world_finance_news() -> str:
        """
        Fetches the latest finance and market headlines from major financial outlets simultaneously.
        Use this when the user asks about finance news, market updates, or economic developments.
        """

        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            tasks = [fetch_and_parse_feed(client, url) for url in FINANCE_SEED_FEEDS]
            results_of_lists = await asyncio.gather(*tasks)
            all_articles = [item for sublist in results_of_lists for item in sublist]

        if not all_articles:
            return "The financial feeds are unresponsive right now. I can't pull market headlines."

        report = ["### FINANCE BRIEFING (LIVE)\n"]
        for entry in all_articles[:12]:
            report.append(f"**[{entry['source']}]** {entry['title']}")
            report.append(f"{entry['summary']}")
            report.append(f"Link: {entry['link']}\n")

        return "\n".join(report)

    @mcp.tool()
    async def search_web(query: str) -> str:
        """Search the web for a given query and return a summary of results."""
        return f"[stub] Search results for: {query}"

    @mcp.tool()
    async def fetch_url(url: str) -> str:
        """Fetch the raw text content of a URL."""
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text[:4000]
    
    @mcp.tool()
    async def open_world_monitor() -> str:
        """
        Opens the World Monitor dashboard (worldmonitor.app) in the system's web browser.
        Use this when the user wants a visual overview of global events or a real-time map.
        """
        url = "https://worldmonitor.app/"
        
        try:
            await open_url_and_restore_focus(url)
            return "Displaying the World Monitor on your primary screen now."
        except Exception as e:
            return f"I'm unable to initialize the visual monitor: {str(e)}"

    @mcp.tool()
    async def open_finance_world_monitor() -> str:
        """
        Opens the Finance World Monitor dashboard (finance.worldmonitor.app) in the system's web browser.
        Use this when the user wants a visual overview of global financial markets and trends.
        """
        url = "https://finance.worldmonitor.app/"

        try:
            await open_url_and_restore_focus(url)
            return "Displaying the Finance World Monitor on your primary screen now."
        except Exception as e:
            return f"I'm unable to initialize the finance monitor: {str(e)}"

    @mcp.tool()
    async def open_youtube(query: str = "") -> str:
        """
        Opens YouTube in the web browser.
        If a search query is provided, opens YouTube search results for that query.
        """
        if query and query.strip():
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query.strip())
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            msg = f"Opening YouTube search for '{query}' on your primary screen now."
        else:
            url = "https://www.youtube.com"
            msg = "Opening YouTube on your primary screen now."

        try:
            await open_url_and_restore_focus(url)
            return msg
        except Exception as e:
            return f"I'm unable to open YouTube: {str(e)}"

    @mcp.tool()
    async def open_whatsapp() -> str:
        """
        Opens WhatsApp Web (web.whatsapp.com) in the web browser.
        Use this when the user asks to open or check WhatsApp.
        """
        url = "https://web.whatsapp.com/"

        try:
            await open_url_and_restore_focus(url)
            return "Opening WhatsApp Web on your primary screen now."
        except Exception as e:
            return f"I'm unable to open WhatsApp Web: {str(e)}"