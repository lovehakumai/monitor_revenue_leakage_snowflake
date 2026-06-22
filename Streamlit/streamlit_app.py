import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session
from model.get_data import get_data
from model.get_log import get_log
from graph.line_act_expect import line_act_expect
from graph.user_payment_movement import user_payment_movement
from model.log_extract import log_extract

st.set_page_config(layout="wide")
# Initialize session_state
if "submit" not in st.session_state:
    st.session_state.submit = False

# Get monthly data
df_pd = get_data(daily_flg = False, date_range = None)
st.title("# MRR Movements & Usage Monitor Dashboard")

st.header("## MRR Movements")
ym_list = sorted(df_pd["CAL_MONTH"].unique())
ym_filter_1, ym_filter_2 = st.columns(2)
with ym_filter_1:
    ym_from = st.selectbox("FROM", ym_list)
with ym_filter_2:
    ym_to = st.selectbox("TO", sorted(ym_list, reverse=True))

df_pd = df_pd[(df_pd["CAL_MONTH"] >= ym_from) & (df_pd["CAL_MONTH"] <= ym_to) ]

col1, col2 = st.columns(2)
with col1: 
    st.subheader("Revenue Expect&Actual")
    line_act_expect(df_pd)
with col2: 
    st.subheader("User Payment Status")
    user_payment_movement(df_pd)

st.write("---")
st.header("## Usage Logs")
st.subheader("Push button and verify all user datas")

with st.form("date_range"):
    usage_logs_range_list = ["Latest 3month", "Latest 6month", "All"]
    usage_logs_range_val = st.selectbox("Date Range", usage_logs_range_list)
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        st.session_state.submit = True 

if st.session_state.submit:
    base_df = get_data(daily_flg = True, date_range = usage_logs_range_val)
    source_dic = log_extract(base_df)
    
    allusers = source_dic["all_users"]
    is_used = source_dic["is_used"]
    is_churned = source_dic["is_churned"]
    is_started = source_dic["is_started"]
    supsicious_user_log = source_dic["suspicious_user_log"]
    
    user_action_list = ["Correct", "Correct Not Used After Churn"
            , "Correct Not Used After Expiration"
            , "Correct Not Used Before Start"
            , "Incorrect Used After Churn"
            , "Incorrect Used After Expiration"
            , "Incorrect Used Before Start"]
    
    st.subheader("Daily Log")
    user_action_select = st.multiselect(
            label = "Chose User Action Type",
            options = user_action_list,
            default = [ "Incorrect Used After Churn", "Incorrect Used After Expiration", "Incorrect Used Before Start"])
    st.line_chart(
        data = allusers, 
        y = user_action_select
    )
    st.dataframe(allusers)
    
    st.subheader("Start / Churned")
    start, churn = st.columns(2)
    with start: 
        st.write("UU Started")
        st.line_chart(
            data = is_started,
            x = "CL_DATE",
            y = "UU_started"
        )
        st.dataframe(is_started)
    with churn:
        st.write("UU Churned")
        st.line_chart(
            data = is_churned,
            x = "CL_DATE",
            y = "UU_churned"
        )
        st.dataframe(is_churned)

st.write("---")
st.header("## Snowflake Query Credits")

log_df = get_log()
date_log = log_df.groupby("START_DATE").sum(["TOTAL_HOUR", "TOTAL_CREDIT"])
st.bar_chart(
    data = date_log,
    y = ["TOTAL_HOUR", "TOTAL_CREDIT"]
)
query_log = (
    log_df
    .groupby(["QUERY_TEXT"])[["TOTAL_CREDIT", "TOTAL_HOUR"]]
    .sum().reset_index()
    .sort_values(by = ["TOTAL_CREDIT"], ascending = False)
)
user_log = (
    log_df
    .groupby(["USER_NAME"])[["TOTAL_CREDIT", "TOTAL_HOUR"]]
    .sum().reset_index()
    .sort_values(by = ["TOTAL_CREDIT"], ascending = False)
)
query, user = st.columns(2)
with query: 
    st.subheader("Query Text")
    st.dataframe(query_log)
with user: 
    st.subheader("Users")
    st.dataframe(user_log)