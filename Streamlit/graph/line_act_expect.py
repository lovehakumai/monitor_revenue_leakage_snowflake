import pandas as pd
import streamlit as st
def line_act_expect(df):
    base_df = (
        df.groupby(['CAL_MONTH']).agg(
        {
            "MRR_AMOUNT": "sum",
            "ACT_MONTH_USD": "sum"
        })
        .reset_index()
        .rename(columns = {"MRR_AMOUNT": "Expected", "ACT_MONTH_USD":"Actual"})
    )
    
    tmp_df = (
        df[df["PAYMENT_STATUS"]!="Stop Paying"]
        .groupby(["CAL_MONTH"])[["ACCOUNT_ID"]]
        .nunique()
        .reset_index()
        .rename(columns={"ACCOUNT_ID":"ActiveUU"})
    )
    
    result = pd.merge(base_df, tmp_df, on=["CAL_MONTH"], how="left")
    result.index = result["CAL_MONTH"]
    
    st.line_chart(
        data = result, 
        x = "CAL_MONTH",
        y = ["Expected", "Actual"]
    )
    return