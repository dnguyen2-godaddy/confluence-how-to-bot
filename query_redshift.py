import pandas as pd
import redshift_connector
import logging
from utils.config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_scorecard_query():
    """Execute the scorecard query and return results."""
    logger.info("Script started")
    
    # Validate configuration
    if not config.validate_redshift_config():
        logger.error("Missing required Redshift configuration. Please check your .env file.")
        raise ValueError("Invalid Redshift configuration")
    
    try:
        conn = redshift_connector.connect(
            host=config.redshift_host,
            database=config.redshift_database,
            port=config.redshift_port,
            user=config.redshift_user,
            password=config.redshift_password
        )
        logger.info("Successfully connected to Redshift")
    except Exception as e:
        logger.error(f"Failed to connect to Redshift: {e}")
        raise

    query = """
    SELECT 
      TO_CHAR(metric_report_mst_month, 'MM-YYYY') AS metric_report_mst_month,
      entry_type,
      business_unit, 
      metric_name, 
      region_name, 
      CASE 
        WHEN higher_is_better = 1 THEN 'true'
        WHEN higher_is_better = 0 THEN 'false'
        ELSE NULL
      END AS higher_is_better,
      SUM(metric_value) AS metric_value
    FROM ba_corporate.scorecard_test_dn
    WHERE metric_report_mst_month >= '2025-01-01'
    AND business_unit = 'CARE & SERVICES'
    GROUP BY 
      metric_report_mst_month,
      entry_type,
      business_unit, 
      metric_name, 
      region_name, 
      higher_is_better
    ORDER BY 
      metric_report_mst_month,
      business_unit;
    """

    try:
        logger.info("Executing query...")
        df = pd.read_sql(query, conn)
        logger.info(f"Query executed successfully. Retrieved {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    # Run the query and display results
    result_df = run_scorecard_query()
    print("\nQuery Results:")
    print("=" * 50)
    print(result_df)
    print("=" * 50)