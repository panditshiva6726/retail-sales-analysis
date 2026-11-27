-- Retail Sales Performance Analysis - Comprehensive SQL Queries
-- Compatible with SQLite / PostgreSQL / MySQL

-- 1. Overall Business KPIs
SELECT
    COUNT(DISTINCT Order_ID) AS total_orders,
    SUM(Quantity) AS total_units_sold,
    ROUND(SUM(Sales), 2) AS total_revenue,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2) AS profit_margin_pct,
    ROUND(AVG(Sales), 2) AS avg_order_value
FROM retail_sales;

-- 2. Monthly Revenue & Profit Trend
SELECT
    substr(Order_Date, 1, 7) AS order_month,
    COUNT(DISTINCT Order_ID) AS orders,
    ROUND(SUM(Sales), 2) AS monthly_revenue,
    ROUND(SUM(Profit), 2) AS monthly_profit
FROM retail_sales
GROUP BY order_month
ORDER BY order_month;

-- 3. Quarterly Performance Breakdown
SELECT
    'Q' || ((CAST(substr(Order_Date, 6, 2) AS INTEGER) - 1) / 3 + 1) AS quarter,
    COUNT(DISTINCT Order_ID) AS orders,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2) AS margin_pct
FROM retail_sales
GROUP BY quarter
ORDER BY quarter;

-- 4. Category-Wise Sales, Profit & Margin
SELECT
    Category,
    COUNT(DISTINCT Order_ID) AS orders,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2) AS margin_pct
FROM retail_sales
GROUP BY Category
ORDER BY total_sales DESC;

-- 5. Region-Wise Performance
SELECT
    Region,
    COUNT(DISTINCT Order_ID) AS orders,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(AVG(Sales), 2) AS avg_order_value
FROM retail_sales
GROUP BY Region
ORDER BY total_sales DESC;

-- 6. Customer Segment Analysis
SELECT
    Customer_Segment,
    COUNT(DISTINCT Order_ID) AS orders,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(AVG(Sales), 2) AS avg_order_value
FROM retail_sales
GROUP BY Customer_Segment
ORDER BY total_sales DESC;

-- 7. Weekday vs Weekend Sales Performance
SELECT
    CASE
        WHEN CAST(strftime('%w', Order_Date) AS INTEGER) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(DISTINCT Order_ID) AS orders,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(AVG(Sales), 2) AS avg_order_value
FROM retail_sales
GROUP BY day_type
ORDER BY total_sales DESC;

-- 8. Top 5 Most Profitable Products
SELECT
    Product_Name,
    Category,
    SUM(Quantity) AS units_sold,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit
FROM retail_sales
GROUP BY Product_Name, Category
ORDER BY total_profit DESC
LIMIT 5;

-- 9. Impact of Discount Tiers on Profit Margin
SELECT
    CASE
        WHEN Discount = 0 THEN '0% (No Discount)'
        WHEN Discount <= 0.15 THEN '1% - 15%'
        ELSE 'Above 15%'
    END AS discount_tier,
    COUNT(*) AS order_count,
    ROUND(SUM(Sales), 2) AS total_sales,
    ROUND(SUM(Profit), 2) AS total_profit,
    ROUND(SUM(Profit) * 100.0 / SUM(Sales), 2) AS margin_pct
FROM retail_sales
GROUP BY discount_tier
ORDER BY margin_pct DESC;
