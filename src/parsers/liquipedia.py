"""Liquipedia parser for Dota 2 tournament data."""

import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from pathlib import Path
import json
import hashlib


class LiquipediaParser:
    """Parser for extracting Dota 2 tournament data from Liquipedia."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Liquipedia parser.

        Args:
            config: Configuration dictionary. If None, uses default settings.
        """
        if config is None:
            config = {
                'base_url': 'https://liquipedia.net/dota2',
                'rate_limit': 2,
                'user_agent': 'Dota2DataParser/1.0 (Educational/Research)',
            }

        self.base_url = config.get('base_url', 'https://liquipedia.net/dota2')
        self.rate_limit = config.get('rate_limit', 2)
        self.user_agent = config.get('user_agent', 'Dota2DataParser/1.0')
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent
        })

        # Cache settings
        self.cache_enabled = True
        self.cache_dir = Path('.cache')
        if self.cache_enabled:
            self.cache_dir.mkdir(exist_ok=True)

    def _rate_limit_wait(self):
        """Wait to respect rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()

    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for a URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"

    def _get_cached(self, url: str) -> Optional[str]:
        """Get cached content for a URL."""
        if not self.cache_enabled:
            return None

        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                data = json.load(f)
                # Cache for 1 hour
                if time.time() - data['timestamp'] < 3600:
                    return data['content']
        return None

    def _save_cache(self, url: str, content: str):
        """Save content to cache."""
        if not self.cache_enabled:
            return

        cache_path = self._get_cache_path(url)
        with open(cache_path, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'content': content
            }, f)

    def _fetch_page(self, path: str) -> Optional[BeautifulSoup]:
        """
        Fetch a page from Liquipedia.

        Args:
            path: Path relative to base URL (e.g., '/Dota_Pit_League')

        Returns:
            BeautifulSoup object or None if request fails
        """
        url = f"{self.base_url}{path}"

        # Check cache first
        cached = self._get_cached(url)
        if cached:
            return BeautifulSoup(cached, 'lxml')

        self._rate_limit_wait()

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
            self._save_cache(url, content)
            return BeautifulSoup(content, 'lxml')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_tournaments(self, year: int = None, tier: str = None) -> List[Dict[str, Any]]:
        """
        Get list of tournaments.

        Args:
            year: Filter by year (e.g., 2024). If None, gets current year.
            tier: Filter by tier ('Premier', 'Major', 'Minor'). If None, gets all.

        Returns:
            List of tournament dictionaries with basic info
        """
        if year is None:
            year = datetime.now().year

        # Liquipedia organizes tournaments by year
        path = f"/Dota_2/Tournaments/{year}"
        soup = self._fetch_page(path)

        if not soup:
            return []

        tournaments = []

        # Find tournament sections (Premier, Major, Minor, etc.)
        for section in soup.find_all('div', class_='divRow'):
            # Get tier from section header
            tier_header = section.find_previous('h3')
            section_tier = tier_header.get_text().strip() if tier_header else 'Unknown'

            # Skip if filtering by tier and doesn't match
            if tier and tier.lower() not in section_tier.lower():
                continue

            # Find all tournament entries in this section
            for tournament_div in section.find_all('div', class_='tournament-card'):
                tournament_data = self._parse_tournament_card(tournament_div, year, section_tier)
                if tournament_data:
                    tournaments.append(tournament_data)

        return tournaments

    def _parse_tournament_card(self, card, year: int, tier: str) -> Optional[Dict[str, Any]]:
        """Parse a tournament card from the tournament list."""
        try:
            # Get tournament link and name
            link = card.find('a')
            if not link:
                return None

            tournament_path = link.get('href', '')
            tournament_name = link.get('title', link.get_text().strip())

            # Get dates
            date_div = card.find('div', class_='tournament-date')
            dates = date_div.get_text().strip() if date_div else 'Unknown'

            # Get prize pool
            prize_div = card.find('div', class_='prize')
            prize_pool = prize_div.get_text().strip() if prize_div else 'Unknown'

            return {
                'name': tournament_name,
                'path': tournament_path,
                'url': f"{self.base_url}{tournament_path}",
                'year': year,
                'tier': tier,
                'dates': dates,
                'prize_pool': prize_pool,
            }
        except Exception as e:
            print(f"Error parsing tournament card: {e}")
            return None

    def get_tournament_details(self, tournament_path: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tournament.

        Args:
            tournament_path: Path to tournament page (e.g., '/The_International/2024')

        Returns:
            Dictionary with detailed tournament information
        """
        soup = self._fetch_page(tournament_path)
        if not soup:
            return None

        details = {
            'path': tournament_path,
            'url': f"{self.base_url}{tournament_path}",
            'name': '',
            'dates': '',
            'prize_pool': '',
            'teams': [],
            'matches': [],
        }

        # Get tournament name from title
        title = soup.find('h1', class_='firstHeading')
        if title:
            details['name'] = title.get_text().strip()

        # Get infobox data
        infobox = soup.find('div', class_='infobox-center')
        if infobox:
            # Extract dates
            date_row = infobox.find('div', string=re.compile('Dates?:', re.I))
            if date_row:
                date_value = date_row.find_next_sibling()
                if date_value:
                    details['dates'] = date_value.get_text().strip()

            # Extract prize pool
            prize_row = infobox.find('div', string=re.compile('Prize Pool:', re.I))
            if prize_row:
                prize_value = prize_row.find_next_sibling()
                if prize_value:
                    details['prize_pool'] = prize_value.get_text().strip()

        # Get participating teams
        details['teams'] = self._parse_teams(soup)

        # Get matches
        details['matches'] = self._parse_matches(soup)

        return details

    def _parse_teams(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse participating teams from tournament page."""
        teams = []

        # Look for team sections
        team_sections = soup.find_all('div', class_='teamcard')
        for team_card in team_sections:
            team_link = team_card.find('a')
            if team_link:
                teams.append({
                    'name': team_link.get('title', team_link.get_text().strip()),
                    'path': team_link.get('href', ''),
                })

        return teams

    def _parse_matches(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse matches from tournament page."""
        matches = []

        # Look for match sections
        match_divs = soup.find_all('div', class_='brkts-match')
        for match_div in match_divs:
            match_data = self._parse_match(match_div)
            if match_data:
                matches.append(match_data)

        return matches

    def _parse_match(self, match_div) -> Optional[Dict[str, Any]]:
        """Parse a single match."""
        try:
            teams = match_div.find_all('div', class_='brkts-opponent-entry')
            if len(teams) < 2:
                return None

            team1 = teams[0].get_text().strip()
            team2 = teams[1].get_text().strip()

            # Get scores
            scores = match_div.find_all('div', class_='brkts-opponent-score')
            score1 = scores[0].get_text().strip() if len(scores) > 0 else ''
            score2 = scores[1].get_text().strip() if len(scores) > 1 else ''

            # Get match ID from data attributes (useful for OpenDota lookup)
            match_id = match_div.get('data-match-id', '')

            return {
                'team1': team1,
                'team2': team2,
                'score1': score1,
                'score2': score2,
                'match_id': match_id,
            }
        except Exception as e:
            print(f"Error parsing match: {e}")
            return None

    def search_tournament(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for tournaments by name.

        Args:
            query: Search query

        Returns:
            List of matching tournaments
        """
        # Use Liquipedia's search
        search_path = f"/api.php?action=opensearch&search={query}&format=json"
        soup = self._fetch_page(search_path)

        if not soup:
            return []

        # Parse search results
        # This is a simplified version - actual implementation may need adjustments
        results = []
        # Parse JSON response and extract tournament pages
        # ...

        return results
