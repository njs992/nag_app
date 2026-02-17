"""Configuration for the RPG backend server."""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    
    # Server
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "False") == "True"
    
    # Data paths
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    GAMES_DIR = os.path.join(DATA_DIR, "games")
    MAPS_DIR = os.path.join(DATA_DIR, "maps")
    CHARACTERS_DIR = os.path.join(DATA_DIR, "characters")
    
    # WebSocket
    CORS_ORIGINS = "*"  # Allow all origins for development
    
    # Game defaults
    DEFAULT_GRID_SIZE = 50
    MAX_PLAYERS_PER_GAME = 10
