"""OpenDota API client for detailed match and player data."""

import time
import requests
from typing import Dict, Any, List, Optional


class OpenDotaClient:
    """Client for interacting with the OpenDota API."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize OpenDota API client.

        Args:
            config: Configuration dictionary. If None, uses default settings.
        """
        if config is None:
            config = {
                'base_url': 'https://api.opendota.com/api',
                'api_key': None,
                'rate_limit': 1,
            }

        self.base_url = config.get('base_url', 'https://api.opendota.com/api')
        self.api_key = config.get('api_key')
        self.rate_limit = config.get('rate_limit', 1)
        self.last_request_time = 0
        self.session = requests.Session()

        if self.api_key:
            self.session.params = {'api_key': self.api_key}

    def _rate_limit_wait(self):
        """Wait to respect rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """
        Make a request to the OpenDota API.

        Args:
            endpoint: API endpoint (e.g., '/matches/123456')
            params: Query parameters

        Returns:
            JSON response or None if request fails
        """
        self._rate_limit_wait()

        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_match(self, match_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific match.

        Args:
            match_id: Dota 2 match ID

        Returns:
            Dictionary with match details or None if not found
        """
        return self._make_request(f"/matches/{match_id}")

    def get_player(self, account_id: int) -> Optional[Dict[str, Any]]:
        """
        Get player profile information.

        Args:
            account_id: Player's account ID

        Returns:
            Dictionary with player info or None if not found
        """
        return self._make_request(f"/players/{account_id}")

    def get_player_matches(self, account_id: int, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent matches for a player.

        Args:
            account_id: Player's account ID
            limit: Number of matches to retrieve (default 20, max 100)

        Returns:
            List of match dictionaries or None if request fails
        """
        params = {'limit': min(limit, 100)}
        return self._make_request(f"/players/{account_id}/matches", params)

    def get_team(self, team_id: int) -> Optional[Dict[str, Any]]:
        """
        Get team information.

        Args:
            team_id: Team ID

        Returns:
            Dictionary with team info or None if not found
        """
        return self._make_request(f"/teams/{team_id}")

    def get_team_matches(self, team_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent matches for a team.

        Args:
            team_id: Team ID

        Returns:
            List of match dictionaries or None if request fails
        """
        return self._make_request(f"/teams/{team_id}/matches")

    def search_players(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Search for players by name.

        Args:
            query: Search query (player name)

        Returns:
            List of matching players or None if request fails
        """
        params = {'q': query}
        return self._make_request("/search", params)

    def get_pro_matches(self, less_than_match_id: int = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of professional matches.

        Args:
            less_than_match_id: Get matches with ID less than this (for pagination)

        Returns:
            List of pro match dictionaries or None if request fails
        """
        params = {}
        if less_than_match_id:
            params['less_than_match_id'] = less_than_match_id

        return self._make_request("/proMatches", params)

    def get_heroes(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of all Dota 2 heroes.

        Returns:
            List of hero dictionaries or None if request fails
        """
        return self._make_request("/heroes")

    def parse_match_details(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and extract key information from match data.

        Args:
            match_data: Raw match data from API

        Returns:
            Simplified match information
        """
        if not match_data:
            return {}

        return {
            'match_id': match_data.get('match_id'),
            'duration': match_data.get('duration'),
            'start_time': match_data.get('start_time'),
            'radiant_win': match_data.get('radiant_win'),
            'radiant_score': match_data.get('radiant_score'),
            'dire_score': match_data.get('dire_score'),
            'league_id': match_data.get('leagueid'),
            'league_name': match_data.get('league', {}).get('name'),
            'radiant_team_id': match_data.get('radiant_team_id'),
            'dire_team_id': match_data.get('dire_team_id'),
            'players': [
                {
                    'account_id': p.get('account_id'),
                    'hero_id': p.get('hero_id'),
                    'kills': p.get('kills'),
                    'deaths': p.get('deaths'),
                    'assists': p.get('assists'),
                    'gold_per_min': p.get('gold_per_min'),
                    'xp_per_min': p.get('xp_per_min'),
                }
                for p in match_data.get('players', [])
            ],
        }
