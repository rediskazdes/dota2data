# Dota 2 Data Parser

A Python tool for collecting Dota 2 tournament and match data from multiple sources.

## Features

- **Liquipedia Parser**: Extract tournament information, schedules, and results from Liquipedia
- **OpenDota API Integration**: Fetch detailed match statistics using tournament data
- **Configurable Data Sources**: Enable/disable specific data sources as needed

## Project Structure

```
dota2data/
├── src/
│   ├── parsers/
│   │   ├── liquipedia.py    # Liquipedia tournament parser
│   │   └── opendota.py      # OpenDota API client
│   ├── config.py            # Configuration management
│   └── main.py              # Main entry point
├── config.yaml              # Data source configuration
├── requirements.txt         # Python dependencies
└── examples/                # Example usage scripts
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to enable/disable data sources:

```yaml
data_sources:
  liquipedia:
    enabled: true
    rate_limit: 2  # seconds between requests
  opendota:
    enabled: true
    api_key: null  # Optional API key
```

## Usage

```python
from src.parsers.liquipedia import LiquipediaParser

# Parse tournament data
parser = LiquipediaParser()
tournaments = parser.get_tournaments(year=2024)

for tournament in tournaments:
    print(f"{tournament['name']}: {tournament['dates']}")
```

## Liquipedia Parsing

The Liquipedia parser can extract:
- Tournament lists and details
- Team rosters
- Match schedules and results
- Prize pool information

## OpenDota Integration

Use tournament data from Liquipedia to query OpenDota API for:
- Detailed match statistics
- Player performance data
- Hero picks and bans
- Match timelines

## License

MIT
