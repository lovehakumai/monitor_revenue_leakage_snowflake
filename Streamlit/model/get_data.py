import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session

@st.cache_data(max_entries="3", ttl="600")
def get_data(daily_flg, date_range):
    
    session = get_active_session()
    session.sql("ALTER SESSION SET QUERY_TAG = 'mrr_leakage_audit_app'")
    session.sql("USE DATABASE KAGGLE_SUBSCRIPTION").collect()
    session.sql("USE SCHEMA DBT_PJT").collect()
    
    if not daily_flg:
        table_name = "MART_MONTHLY__ACCOUNT_AGG"
        df_pd = session.sql(f"SELECT * FROM {table_name}").to_pandas()
    else:
        table_name = "MART_DAILY__LOG"
        range_map = {"Latest 3month":3, "Latest 6month":6, "All":0}
        if date_range != "All":
            df_pd = session.sql(
                f"WITH date_range AS (SELECT MAX(CL_DATE) AS max_date FROM {table_name}) SELECT * FROM {table_name} WHERE DATEADD(MONTH, -{range_map[date_range]}, (SELECT max_date FROM date_range))<=CL_DATE").to_pandas()
                
        else: 
            df_pd = session.sql(f"SELECT * FROM {table_name}").to_pandas()
    
    return df_pd 