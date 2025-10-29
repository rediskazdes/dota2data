"""Configuration management for Dota 2 Data Parser."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manages configuration for data sources and parsing options."""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config.yaml. Defaults to project root.
        """
        if config_path is None:
            # Default to config.yaml in project root
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config.yaml"

        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def is_source_enabled(self, source_name: str) -> bool:
        """
        Check if a data source is enabled.

        Args:
            source_name: Name of the data source (e.g., 'liquipedia', 'opendota')

        Returns:
            True if source is enabled, False otherwise
        """
        sources = self._config.get('data_sources', {})
        source = sources.get(source_name, {})
        return source.get('enabled', False)

    def get_source_config(self, source_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific data source.

        Args:
            source_name: Name of the data source

        Returns:
            Configuration dictionary for the source
        """
        sources = self._config.get('data_sources', {})
        return sources.get(source_name, {})

    def get_parsing_config(self) -> Dict[str, Any]:
        """Get general parsing configuration."""
        return self._config.get('parsing', {})

    def enable_source(self, source_name: str):
        """
        Enable a data source.

        Args:
            source_name: Name of the data source to enable
        """
        if 'data_sources' not in self._config:
            self._config['data_sources'] = {}
        if source_name not in self._config['data_sources']:
            self._config['data_sources'][source_name] = {}

        self._config['data_sources'][source_name]['enabled'] = True
        self._save_config()

    def disable_source(self, source_name: str):
        """
        Disable a data source.

        Args:
            source_name: Name of the data source to disable
        """
        if 'data_sources' in self._config and source_name in self._config['data_sources']:
            self._config['data_sources'][source_name]['enabled'] = False
            self._save_config()

    def _save_config(self):
        """Save configuration back to YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)


# Global config instance
_config_instance = None


def get_config(config_path: str = None) -> Config:
    """
    Get the global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
