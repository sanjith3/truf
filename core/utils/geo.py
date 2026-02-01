import re
import urllib.request
from urllib.parse import urlparse, parse_qs

class GoogleMapsParser:
    """
    Utility class to extract latitude and longitude from various Google Maps URL formats.
    Works without paid APIs by parsing URL patterns and following redirects.
    """
    
    # Pattern for @lat,lon (Common in full Google Maps URLs)
    COORD_PATTERN_AT = re.compile(r'@(-?\d+\.\d+),(-?\d+\.\d+)')
    
    # Pattern for !3dLAT!4dLON (Found in some Google Maps internal state URLs)
    COORD_PATTERN_BANG = re.compile(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)')

    @staticmethod
    def extract_lat_lon(url):
        """
        Main entry point. Handles redirection and multiple URL formats.
        Returns (latitude, longitude) or (None, None)
        """
        if not url:
            return None, None
            
        url = url.strip()
        
        # 1. Handle Short URLs (goo.gl, maps.app.goo.gl)
        # We follow the redirect to get the full URL which contains the coords
        if "goo.gl" in url or "maps.app.goo.gl" in url:
            try:
                # We only need the headers to find the redirect location
                # CRITICAL: Google blocks default python user-agents, so we must spoof a browser.
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                request = urllib.request.Request(url, headers=headers, method='HEAD')
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    url = response.geturl()
            except Exception as e:
                # If we can't follow redirect, we can't parse short URLs
                print(f"Error resolving short URL: {e}")
                return None, None

        # 2. Try parsing Query Parameters (q=lat,lon)
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        
        if 'q' in params:
            q_val = params['q'][0]
            # Check if q is in format "lat,lon"
            q_match = re.match(r'(-?\d+\.\d+),(-?\d+\.\d+)', q_val)
            if q_match:
                return float(q_match.group(1)), float(q_match.group(2))

        # 3. Try parsing from Path (@lat,lon)
        at_match = GoogleMapsParser.COORD_PATTERN_AT.search(url)
        if at_match:
            return float(at_match.group(1)), float(at_match.group(2))

        # 4. Try parsing internal bang format (!3dlat!4dlon)
        bang_match = GoogleMapsParser.COORD_PATTERN_BANG.search(url)
        if bang_match:
            return float(bang_match.group(1)), float(bang_match.group(2))

        return None, None

    @staticmethod
    def is_valid_link(url):
        """Simple validation to check if it's a google maps link"""
        if not url: return False
        valid_domains = ['google.com/maps', 'maps.google.com', 'goo.gl/maps', 'maps.app.goo.gl']
        return any(domain in url for domain in valid_domains)
