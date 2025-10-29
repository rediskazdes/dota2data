# Usage Guide

## Enabling/Disabling Data Sources

The Dota 2 Data Parser uses a configuration file (`config.yaml`) to control which data sources are active.

### Configuration File

The main configuration is in `config.yaml`:

```yaml
data_sources:
  liquipedia:
    enabled: true          # Set to false to disable
    base_url: "https://liquipedia.net/dota2"
    rate_limit: 2          # Seconds between requests
    user_agent: "Dota2DataParser/1.0 (Educational/Research)"

  opendota:
    enabled: true          # Set to false to disable
    base_url: "https://api.opendota.com/api"
    api_key: null          # Add your API key here for higher limits
    rate_limit: 1
```

### Enabling/Disabling Liquipedia

**To enable Liquipedia parsing:**
```yaml
liquipedia:
  enabled: true
```

**To disable Liquipedia parsing:**
```yaml
liquipedia:
  enabled: false
```

When disabled, any code that tries to use Liquipedia will raise an error:
```python
RuntimeError: Liquipedia parsing is not enabled in config
```

### Enabling/Disabling OpenDota

**To enable OpenDota API:**
```yaml
opendota:
  enabled: true
```

**To disable OpenDota API:**
```yaml
opendota:
  enabled: false
```

### Programmatic Control

You can also enable/disable sources programmatically:

```python
from src.config import get_config

config = get_config()

# Enable a source
config.enable_source('liquipedia')

# Disable a source
config.disable_source('opendota')

# Check if a source is enabled
if config.is_source_enabled('liquipedia'):
    print("Liquipedia is enabled!")
```

## Rate Limiting

Both data sources respect rate limits to avoid overwhelming the servers:

- **Liquipedia**: Default 2 seconds between requests
- **OpenDota**: Default 1 second between requests

Adjust these in `config.yaml`:

```yaml
liquipedia:
  rate_limit: 3  # Wait 3 seconds between requests

opendota:
  rate_limit: 2  # Wait 2 seconds between requests
```

## OpenDota API Key

OpenDota allows higher rate limits with an API key:

1. Sign up at https://www.opendota.com/
2. Get your API key
3. Add it to `config.yaml`:

```yaml
opendota:
  api_key: "your-api-key-here"
```

## Caching

The Liquipedia parser includes caching to reduce redundant requests:

- Cached files are stored in `.cache/` directory
- Cache expires after 1 hour
- To disable caching, modify the parser initialization

## Examples

### Example 1: Only Use Liquipedia

```yaml
data_sources:
  liquipedia:
    enabled: true
  opendota:
    enabled: false
```

```python
from src.parsers import LiquipediaParser

parser = LiquipediaParser()
tournaments = parser.get_tournaments(year=2024)
```

### Example 2: Only Use OpenDota

```yaml
data_sources:
  liquipedia:
    enabled: false
  opendota:
    enabled: true
```

```python
from src.parsers import OpenDotaClient

client = OpenDotaClient()
match = client.get_match(7000000000)
```

### Example 3: Use Both (Recommended)

```yaml
data_sources:
  liquipedia:
    enabled: true
  opendota:
    enabled: true
```

```python
from src.main import Dota2DataParser

parser = Dota2DataParser()

# Get tournament structure from Liquipedia
tournaments = parser.get_tournaments(year=2024)

# Get detailed match stats from OpenDota
# (using match IDs found in tournament data)
for tournament in tournaments:
    details = parser.get_tournament_details(tournament['path'])
    # Process matches with OpenDota...
```

## Command Line Usage

The parser includes a CLI:

```bash
# List all 2024 tournaments
python -m src.main --tournaments --year 2024

# List only Premier tier tournaments
python -m src.main --tournaments --tier Premier

# Get details for a specific tournament
python -m src.main --tournament "/The_International/2024"

# Get match details from OpenDota
python -m src.main --match 7000000000
```

## Troubleshooting

### "Liquipedia parsing is not enabled"

Enable Liquipedia in `config.yaml`:
```yaml
liquipedia:
  enabled: true
```

### "OpenDota API is not enabled"

Enable OpenDota in `config.yaml`:
```yaml
opendota:
  enabled: true
```

### Rate Limiting Issues

If you're getting blocked:
1. Increase `rate_limit` values in config
2. For OpenDota, add an API key
3. Enable caching to reduce requests

### Network Errors

- Check your internet connection
- Verify the URLs in config are correct
- Check if the services are online
