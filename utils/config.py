"""
Configuration management utilities for the Confluence How-To Bot.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration class for managing environment variables."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
    
    @property
    def redshift_host(self) -> Optional[str]:
        """Get Redshift host from environment."""
        return os.getenv('REDSHIFT_HOST')
    
    @property
    def redshift_database(self) -> Optional[str]:
        """Get Redshift database from environment."""
        return os.getenv('REDSHIFT_DATABASE')
    
    @property
    def redshift_port(self) -> int:
        """Get Redshift port from environment."""
        return int(os.getenv('REDSHIFT_PORT', '5439'))
    
    @property
    def redshift_user(self) -> Optional[str]:
        """Get Redshift user from environment."""
        return os.getenv('REDSHIFT_USER')
    
    @property
    def redshift_password(self) -> Optional[str]:
        """Get Redshift password from environment."""
        return os.getenv('REDSHIFT_PASSWORD')
    
    def validate_redshift_config(self) -> bool:
        """Validate that all required Redshift configuration is present."""
        required_vars = [
            self.redshift_host,
            self.redshift_database,
            self.redshift_user,
            self.redshift_password
        ]
        return all(var is not None and var != '' for var in required_vars)


# Global config instance
config = Config()