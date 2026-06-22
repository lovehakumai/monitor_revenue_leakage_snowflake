import streamlit as st
import pandas as pd

def log_extract(log_df):
    
    all_users = log_df.groupby(["CL_DATE", "USAGE_STATUS"]).agg({
        "ACCOUNT_ID": "nunique"
    }).reset_index().rename(columns={"ACCOUNT_ID": "UU_all"})
    
    all_users = all_users.pivot(
        index = "CL_DATE",
        columns = "USAGE_STATUS",
        values = "UU_all"
    )

    is_used = log_df[log_df["IS_USED"]==1].groupby(["CL_DATE"]).agg({
        "ACCOUNT_ID": "nunique"
    }).reset_index().rename(columns={"ACCOUNT_ID": "UU_used"})

    is_churned = log_df[log_df["IS_CHURNED"]==1].groupby(["CL_DATE"]).agg({
        "ACCOUNT_ID": "nunique"
    }).reset_index().rename(columns={"ACCOUNT_ID": "UU_churned"})

    is_started = log_df[log_df["IS_STARTED"]==1].groupby(["CL_DATE"]).agg({
        "ACCOUNT_ID": "nunique"
    }).reset_index().rename(columns={"ACCOUNT_ID": "UU_started"})

    suspicious_user_mst = (
        log_df[log_df["USAGE_STATUS"].str.contains("Incorrect")]["ACCOUNT_ID"].unique()
    )

    suspicious_user_log = (
        log_df[log_df["ACCOUNT_ID"].isin(suspicious_user_mst)]
    )
    return {"all_users":all_users
        , "is_used": is_used
        , "is_churned":is_churned
        , "is_started":is_started
        , "suspicious_user_log":suspicious_user_log}