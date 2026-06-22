from snowflake.snowpark.context import get_active_session
session = get_active_session()

def get_log():
    session.sql("ALTER SESSION SET QUERY_TAG = 'mrr_leakage_audit_app'").collect()
    session.sql("USE DATABASE KAGGLE_SUBSCRIPTION").collect()

    log_df = session.sql("""
        SELECT 
            START_TIME
            , DATE_TRUNC(DAY, START_TIME)::DATE AS START_DATE
            , QUERY_ID
            , QUERY_TEXT
            , USER_NAME 
            , (TOTAL_ELAPSED_TIME / 1000 / 3600) AS total_hour 
            , (TOTAL_ELAPSED_TIME / 1000 / 3600) * CASE WAREHOUSE_SIZE  
                WHEN 'X-Small' THEN 1
                WHEN 'Small'   THEN 2
                WHEN 'Medium'  THEN 4
                WHEN 'Large'   THEN 8
                END AS total_credit
        FROM TABLE(KAGGLE_SUBSCRIPTION.INFORMATION_SCHEMA.QUERY_HISTORY()) 
        WHERE QUERY_TAG = 'mrr_leakage_audit_app'
        """).to_pandas()
    return log_df 