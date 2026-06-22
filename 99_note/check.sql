ALTER SESSION SET QUERY_TAG = 'mrr_leakage_audit_app';

SELECT * FROM STG_RAW_RAVENSTACK_CHURN_EVENTS WHERE account_id = 'A-bcf664' ORDER BY churn_date
;
USE DATABASE KAGGLE_SUBSCRIPTION;
USE SCHEMA INFORMATION_SCHEMA;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY WHERE QUERY_TAG = 'mrr_leakage_audit_app' ORDER BY START_TIME DESC;

SELECT STSRT_TIME, QUERY_ID, QUERY_TEXT, (TOTAL_ELAPSED_TIME / 1000 / 3600)  * CASE WAREHOUSE_SIZE 
    WHEN 'X-Small' THEN 1
    WHEN 'Small'   THEN 2
    WHEN 'Medium'  THEN 4
    WHEN 'Large'   THEN 8
    END
FROM TABLE(KAGGLE_SUBSCRIPTION.INFORMATION_SCHEMA.QUERY_HISTORY()) WHERE QUERY_TAG = 'mrr_leakage_audit_app'
;
SELECT * FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS WHERE account_id = 'A-bcf664'
;
SELECT * FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS WHERE account_id = 'A-659280'
;
WITH 
base AS (SELECT * FROM fct_monthly__calc_act)
, account_agg AS (
    SELECT 
        subscription_id
        , account_id
        , month_trunc
        , is_churned
        , SUM(mrr_amount) AS mrr_amount
        , SUM(refund_amount_usd) AS refund_amount_usd
        , SUM(act_month_usd) AS act_month_usd
        , SUM(usage_count) AS usage_count
    FROM base 
    GROUP BY 
        subscription_id
        , account_id
        , month_trunc
        , is_churned
)
SELECT * FROM account_agg WHERE account_id = 'A-bcf664' ORDER BY subscription_id, month_trunc
;
SELECT COUNT(DISTINCT CONCAT(subscription_id, start_date)) FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS;
SELECT COUNT(1) FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS;
SELECT SUM(mrr_amount) FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS;
SELECT SUM(mrr_amount) FROM KAGGLE_SUBSCRIPTION.DBT_PJT.FCT_RAVENSTACK__ADD_USAGE;
USE DATABASE KAGGLE_SUBSCRIPTION;
USE SCHEMA DBT_PJT;

SELECT * FROM STG_RAW_RAVENSTACK_ACCOUNTS LIMIT 10;
SELECT * FROM STG_RAW_RAVENSTACK_CHURN_EVENTS LIMIT 10;
SELECT * FROM STG_RAW_RAVENSTACK_FEATURE_USAGE LIMIT 10;
SELECT * FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS LIMIT 10;
SELECT * FROM STG_RAW_RAVENSTACK_SUPPORT_TICKETS LIMIT 10;
DESCRIBE VIEW STG_RAW_RAVENSTACK_CHURN_EVENTS;
SELECT DISTINCT MRR_AMOUNT FROM STG_RAW_RAVENSTACK_CHURN_EVENTS WHERE plan_tier = 'Enterprise' AND billing_frequency='monthly';
SELECT DISTINCT feature_name FROM STG_RAW_RAVENSTACK_FEATURE_USAGE ORDER BY 1;
SELECT DISTINCT plan_tier FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS;

-- How downgrade works?
-- 1 subscription 1 tier
SELECT subscription_id , COUNT(DISTINCT plan_tier)
FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS
GROUP BY subscription_id
HAVING COUNT(DISTINCT plan_tier) = 1
;
-- How we can see if the user keep using premium feature after downgrade?
-- Build 1 systematic plan_tier table

-- Systematic definition : account_id, subscription_id, plan_tier, day  | create from subscription
-- Actual definition : account_id, subscription_id, plan_tier, day | create from usage-subscription
-- Merge : 
    -- account_id, day
    -- system : subscription_id, plan_tier
    -- actual : subscription_id, plan_tier

-- Can user have several subscription in a same period?
WITH 
base AS (
    SELECT 
        SUBSCRIPTION_ID
        , ACCOUNT_ID
        , START_DATE
        , NVL(END_DATE, '2999-01-01'::DATE) AS END_DATE
        , PLAN_TIER
        , SEATS
        , MRR_AMOUNT
        , ARR_AMOUNT
        , IS_TRIAL
        , UPGRADE_FLAG
        , DOWNGRADE_FLAG
        , CHURN_FLAG
        , BILLING_FREQUENCY
        , AUTO_RENEW_FLAG
    FROM STG_RAW_RAVENSTACK_SUBSCRIPTIONS
)
, FROM base 