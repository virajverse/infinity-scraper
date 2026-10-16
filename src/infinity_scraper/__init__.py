"""
InfinityScrape - Production-grade Web Scraping, Dynamic SPA Rendering, YouTube Transcription, and OSINT Suite.
Author: VirajVerse (https://github.com/virajverse)
"""

import sys
try:
    import httpx
except ImportError:
    try:
        import httpx2
        sys.modules['httpx'] = httpx2
    except ImportError:
        pass

__version__ = "1.0.0"
__author__ = "VirajVerse (https://github.com/virajverse)"

