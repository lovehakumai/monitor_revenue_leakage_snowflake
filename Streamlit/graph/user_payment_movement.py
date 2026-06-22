import pandas as pd
import streamlit as st 

def user_payment_movement(df):
    base = (
        df[df["PAYMENT_STATUS"] != "Before Activate"]
        .groupby(["CAL_MONTH", "PAYMENT_STATUS"])
        .agg({"ACCOUNT_ID": "nunique"})
        .reset_index()
        .rename(columns = {"ACCOUNT_ID":"UU"})
    )

    pivot = base.pivot(
        index = "CAL_MONTH",
        columns = "PAYMENT_STATUS",
        values = "UU"
    ).reset_index()

    st.area_chart(
        data = pivot, 
        x = "CAL_MONTH",
        stack = "normalize"
    )
    return 
    