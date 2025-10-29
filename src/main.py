"""Main entry point for Dota 2 Data Parser."""

import argparse
from typing import List, Dict, Any
from src.config import get_config
from src.parsers import LiquipediaParser, OpenDotaClient


class Dota2DataParser:
    """Main class for collecting Dota 2 data from multiple sources."""

    def __init__(self, config_path: str = None):
        """
        Initialize the data parser.

        Args:
            config_path: Path to configuration file
        """
        self.config = get_config(config_path)

        # Initialize parsers based on configuration
        self.liquipedia = None
        self.opendota = None

        if self.config.is_source_enabled('liquipedia'):
            liquipedia_config = self.config.get_source_config('liquipedia')
            self.liquipedia = LiquipediaParser(liquipedia_config)

        if self.config.is_source_enabled('opendota'):
            opendota_config = self.config.get_source_config('opendota')
            self.opendota = OpenDotaClient(opendota_config)

    def get_tournaments(self, year: int = None, tier: str = None) -> List[Dict[str, Any]]:
        """
        Get tournaments from Liquipedia.

        Args:
            year: Filter by year
            tier: Filter by tier

        Returns:
            List of tournament dictionaries
        """
        if not self.liquipedia:
            raise RuntimeError("Liquipedia parsing is not enabled in config")

        return self.liquipedia.get_tournaments(year, tier)

    def get_tournament_details(self, tournament_path: str) -> Dict[str, Any]:
        """
        Get detailed tournament information.

        Args:
            tournament_path: Path to tournament page

        Returns:
            Tournament details dictionary
        """
        if not self.liquipedia:
            raise RuntimeError("Liquipedia parsing is not enabled in config")

        return self.liquipedia.get_tournament_details(tournament_path)

    def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """
        Get detailed match information from OpenDota.

        Args:
            match_id: Match ID

        Returns:
            Match details dictionary
        """
        if not self.opendota:
            raise RuntimeError("OpenDota API is not enabled in config")

        match_data = self.opendota.get_match(match_id)
        return self.opendota.parse_match_details(match_data)

    def get_tournament_with_match_details(self, tournament_path: str) -> Dict[str, Any]:
        """
        Get tournament data from Liquipedia and enrich with OpenDota match details.

        Args:
            tournament_path: Path to tournament page

        Returns:
            Tournament data with enriched match information
        """
        if not self.liquipedia or not self.opendota:
            raise RuntimeError("Both Liquipedia and OpenDota must be enabled")

        # Get tournament from Liquipedia
        tournament = self.liquipedia.get_tournament_details(tournament_path)

        # Enrich matches with OpenDota data
        for match in tournament.get('matches', []):
            match_id = match.get('match_id')
            if match_id:
                try:
                    match_details = self.get_match_details(int(match_id))
                    match['details'] = match_details
                except Exception as e:
                    print(f"Error getting match details for {match_id}: {e}")

        return tournament


def main():
    """Command-line interface for the parser."""
    parser = argparse.ArgumentParser(
        description='Parse Dota 2 tournament and match data'
    )

    parser.add_argument(
        '--tournaments',
        action='store_true',
        help='List tournaments'
    )

    parser.add_argument(
        '--year',
        type=int,
        help='Filter tournaments by year'
    )

    parser.add_argument(
        '--tier',
        type=str,
        choices=['Premier', 'Major', 'Minor'],
        help='Filter tournaments by tier'
    )

    parser.add_argument(
        '--tournament',
        type=str,
        help='Get details for a specific tournament (provide path)'
    )

    parser.add_argument(
        '--match',
        type=int,
        help='Get details for a specific match (provide match ID)'
    )

    args = parser.parse_args()

    # Initialize parser
    data_parser = Dota2DataParser()

    if args.tournaments:
        # List tournaments
        tournaments = data_parser.get_tournaments(year=args.year, tier=args.tier)
        print(f"Found {len(tournaments)} tournaments:\n")
        for t in tournaments:
            print(f"  {t['name']}")
            print(f"    Tier: {t['tier']}")
            print(f"    Dates: {t['dates']}")
            print(f"    Prize Pool: {t['prize_pool']}")
            print(f"    URL: {t['url']}\n")

    elif args.tournament:
        # Get tournament details
        details = data_parser.get_tournament_details(args.tournament)
        print(f"Tournament: {details['name']}")
        print(f"Dates: {details['dates']}")
        print(f"Prize Pool: {details['prize_pool']}")
        print(f"\nTeams ({len(details['teams'])}):")
        for team in details['teams']:
            print(f"  - {team['name']}")
        print(f"\nMatches ({len(details['matches'])}):")
        for match in details['matches'][:10]:  # Show first 10
            print(f"  {match['team1']} vs {match['team2']}: {match['score1']}-{match['score2']}")

    elif args.match:
        # Get match details
        match = data_parser.get_match_details(args.match)
        print(f"Match ID: {match['match_id']}")
        print(f"Duration: {match['duration']} seconds")
        print(f"Winner: {'Radiant' if match['radiant_win'] else 'Dire'}")
        print(f"Score: Radiant {match['radiant_score']} - {match['dire_score']} Dire")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
