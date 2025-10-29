"""Data source parsers for Dota 2 data."""

from .liquipedia import LiquipediaParser
from .opendota import OpenDotaClient

__all__ = ['LiquipediaParser', 'OpenDotaClient']
