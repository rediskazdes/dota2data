"""Basic usage example for Dota 2 Data Parser."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.parsers import LiquipediaParser, OpenDotaClient


def example_liquipedia_tournaments():
    """Example: Get tournament list from Liquipedia."""
    print("=" * 60)
    print("Example 1: Fetching Tournaments from Liquipedia")
    print("=" * 60)

    # Load configuration
    config = get_config()

    # Check if Liquipedia is enabled
    if not config.is_source_enabled('liquipedia'):
        print("Liquipedia parsing is disabled in config.yaml")
        print("To enable it, set data_sources.liquipedia.enabled to true")
        return

    # Initialize parser
    liquipedia_config = config.get_source_config('liquipedia')
    parser = LiquipediaParser(liquipedia_config)

    # Get tournaments for 2024
    print("\nFetching 2024 tournaments...")
    tournaments = parser.get_tournaments(year=2024)

    print(f"\nFound {len(tournaments)} tournaments:\n")

    # Show first 5 tournaments
    for tournament in tournaments[:5]:
        print(f"Name: {tournament['name']}")
        print(f"Tier: {tournament['tier']}")
        print(f"Dates: {tournament['dates']}")
        print(f"Prize Pool: {tournament['prize_pool']}")
        print(f"URL: {tournament['url']}")
        print("-" * 60)


def example_tournament_details():
    """Example: Get detailed tournament information."""
    print("\n" + "=" * 60)
    print("Example 2: Getting Tournament Details")
    print("=" * 60)

    config = get_config()

    if not config.is_source_enabled('liquipedia'):
        print("Liquipedia parsing is disabled")
        return

    liquipedia_config = config.get_source_config('liquipedia')
    parser = LiquipediaParser(liquipedia_config)

    # Example: Get details for The International 2023
    # Note: Adjust the path based on actual Liquipedia structure
    tournament_path = "/The_International/2023"

    print(f"\nFetching details for: {tournament_path}")
    details = parser.get_tournament_details(tournament_path)

    if details:
        print(f"\nTournament: {details['name']}")
        print(f"Dates: {details['dates']}")
        print(f"Prize Pool: {details['prize_pool']}")

        if details['teams']:
            print(f"\nParticipating Teams ({len(details['teams'])}):")
            for team in details['teams'][:10]:  # Show first 10
                print(f"  - {team['name']}")

        if details['matches']:
            print(f"\nMatches ({len(details['matches'])}):")
            for match in details['matches'][:5]:  # Show first 5
                print(f"  {match['team1']} vs {match['team2']}")
                if match['score1'] and match['score2']:
                    print(f"    Score: {match['score1']} - {match['score2']}")
    else:
        print("Could not fetch tournament details")


def example_opendota_match():
    """Example: Get match details from OpenDota."""
    print("\n" + "=" * 60)
    print("Example 3: Getting Match Details from OpenDota")
    print("=" * 60)

    config = get_config()

    if not config.is_source_enabled('opendota'):
        print("OpenDota API is disabled in config.yaml")
        return

    opendota_config = config.get_source_config('opendota')
    client = OpenDotaClient(opendota_config)

    # Example match ID (use a real one for actual testing)
    # You would typically get this from Liquipedia tournament data
    match_id = 7000000000  # Replace with actual match ID

    print(f"\nFetching match details for ID: {match_id}")
    match_data = client.get_match(match_id)

    if match_data:
        parsed = client.parse_match_details(match_data)
        print(f"\nMatch ID: {parsed['match_id']}")
        print(f"Duration: {parsed['duration']} seconds")
        print(f"Winner: {'Radiant' if parsed['radiant_win'] else 'Dire'}")
        print(f"Score: Radiant {parsed['radiant_score']} - {parsed['dire_score']} Dire")

        if parsed.get('league_name'):
            print(f"League: {parsed['league_name']}")

        print(f"\nPlayers ({len(parsed['players'])}):")
        for player in parsed['players'][:5]:  # Show first 5
            print(f"  Hero {player['hero_id']}: {player['kills']}/{player['deaths']}/{player['assists']} KDA")
    else:
        print(f"Could not fetch match data (match may not exist or be private)")


def example_integration():
    """Example: Integrate Liquipedia and OpenDota data."""
    print("\n" + "=" * 60)
    print("Example 4: Integration - Tournament to Match Details")
    print("=" * 60)

    config = get_config()

    if not config.is_source_enabled('liquipedia') or not config.is_source_enabled('opendota'):
        print("Both Liquipedia and OpenDota must be enabled for this example")
        return

    print("\nThis example would:")
    print("1. Fetch a tournament from Liquipedia")
    print("2. Extract match IDs from the tournament")
    print("3. Query OpenDota API for detailed match statistics")
    print("4. Combine the data for comprehensive tournament analysis")
    print("\nThis demonstrates the power of combining structured tournament data")
    print("from Liquipedia with detailed match statistics from OpenDota!")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Dota 2 Data Parser - Usage Examples")
    print("=" * 60)

    # Run examples
    example_liquipedia_tournaments()
    example_tournament_details()
    example_opendota_match()
    example_integration()

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)
    print("\nNote: Some examples may fail if:")
    print("  - Network connectivity issues")
    print("  - Rate limiting from APIs")
    print("  - Changes to Liquipedia's HTML structure")
    print("  - Invalid match IDs for OpenDota")
    print("\nAdjust the paths and IDs in the examples as needed!")


if __name__ == '__main__':
    main()
