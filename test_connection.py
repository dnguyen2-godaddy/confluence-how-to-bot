#!/usr/bin/env python3
"""
Simple test script to verify database connection without running queries.
"""

import logging
from utils.config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_configuration():
    """Test that all required configuration is present."""
    logger.info("Testing configuration...")
    
    if config.validate_redshift_config():
        logger.info("✅ All required configuration is present")
        logger.info(f"Host: {config.redshift_host}")
        logger.info(f"Database: {config.redshift_database}")
        logger.info(f"Port: {config.redshift_port}")
        logger.info(f"User: {config.redshift_user}")
        logger.info("Password: [REDACTED]")
        return True
    else:
        logger.error("❌ Missing required configuration")
        logger.error("Please ensure your .env file contains:")
        logger.error("- REDSHIFT_HOST")
        logger.error("- REDSHIFT_DATABASE")
        logger.error("- REDSHIFT_PORT")
        logger.error("- REDSHIFT_USER")
        logger.error("- REDSHIFT_PASSWORD")
        return False


if __name__ == "__main__":
    test_configuration()