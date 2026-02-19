# AdventureWorks_Sales_Analysis_Python

# Import Pandas to read the files
import pandas as pd

calendar = pd.read_csv("AdventureWorks Calendar Lookup.csv")

# Matplotlib and Seaborn for the graph, charts and trending
import matplotlib.pyplot as plt
import seaborn as seb

# Now we read the files and under the variable names
p_category = pd.read_csv("AdventureWorks Product Categories Lookup.csv")
product = pd.read_csv("AdventureWorks Product Lookup.csv")
p_subcategories = pd.read_csv("AdventureWorks Product Subcategories Lookup.csv")

territory = pd.read_csv("AdventureWorks Territory Lookup.csv")
returns = pd.read_csv("AdventureWorks Returns Data.csv")

sales_2020 = pd.read_csv("AdventureWorks Sales Data 2020.csv")
sales_2021 = pd.read_csv("AdventureWorks Sales Data 2021.csv")
sales_2022 = pd.read_csv("AdventureWorks Sales Data 2022.csv")

# Due to path issues we use encoding latin1 to read the file
customers = pd.read_csv(
    r"AdventureWorks Customer Lookup.csv",
    encoding="latin1"
)

# We join all the yearly sales file into a single file
sales = pd.concat([sales_2020, sales_2021, sales_2022], ignore_index = True)

# Need to check the file shape and head for the confirmation after the concatination
sales.shape
sales.head()

# Check the column relationships between the file
sales.columns
p_category.columns
calendar.columns
customers.columns
product.columns
p_subcategories.columns
territory.columns
returns.columns

# Check the column relationships between the file
product.columns
p_subcategories.columns
p_category.columns

# Merge the files and under new variable name
full_production = pd.merge(product, p_subcategories, on="ProductSubcategoryKey", how="left")


# By this we are going to create a dimension table and fact table
full_production = pd.merge(full_production, p_category, on = "ProductCategoryKey", how = "left")

# Check the data are properly merged
full_production.head()

# Check any empty or not filled rows are present
full_production.isna().sum()

# Filling empty rows in ProductColor as NA using "fillna"
full_production['ProductColor'].fillna('NA', inplace=True)
full_production.isna().sum()

# Check any empty or not filled rows are present
sales.isna().sum()
sales.duplicated().sum()

# Check relationship between the "sales" and "full_production" to merge them
sales.columns
full_production.columns
total_sales = pd.merge(sales, full_production, on = "ProductKey", how = "left")

total_sales.shape
total_sales.head()
total_sales.isna().sum()

# Check the relationship in columns and check not filled rows
total_sales.columns
customers.columns

customers.isna().sum()

# Droping the empty sets 
customers.dropna(subset=['CustomerKey'], inplace=True)

# Filling the rows using the "fillna"
customers['Prefix'].fillna('Unknown', inplace=True)
customers['Gender'].fillna('Not Specified', inplace=True)
customers.isna().sum()

# Removing the error and filling the DOB based on their median values
customers['BirthDate'] = pd.to_datetime(customers['BirthDate'], errors='coerce')
customers['BirthDate'].fillna(customers['BirthDate'].median(), inplace=True)
customers.isna().sum()

# 
text_cols = [
    'FirstName','LastName','EmailAddress',
    'MaritalStatus','EducationLevel',
    'Occupation','HomeOwner'
]

customers[text_cols] = customers[text_cols].fillna('Unknown')
customers['AnnualIncome'].fillna(customers['AnnualIncome'].median(), inplace=True)
customers.isna().sum()


customers['TotalChildren'].fillna(customers['TotalChildren'].median(), inplace=True)


#Filling with median values
customers[~customers['CustomerKey'].astype(str).str.isnumeric()]
customers['CustomerKey'] = pd.to_numeric(customers['CustomerKey'], errors='coerce')
customers.dropna(subset=['CustomerKey'], inplace=True)
customers['CustomerKey'] = customers['CustomerKey'].astype(int)

total_sales['CustomerKey'] = pd.to_numeric(
    total_sales['CustomerKey'],
    errors='coerce'
)

total_sales.dropna(subset=['CustomerKey'], inplace=True)
total_sales['CustomerKey'] = total_sales['CustomerKey'].astype(int)

# Merging the tables
overall_sales = pd.merge(
    total_sales,
    customers,
    on='CustomerKey',
    how='left'
)


overall_sales.head()

# Renameing the Column 
overall_sales.columns
territory.columns

territory.rename(columns={'SalesTerritoryKey': 'TerritoryKey'}, inplace=True)



# Checking the data type
overall_sales['TerritoryKey'].dtype
territory['TerritoryKey'].dtype



# Merging the table to the final data
final_df = pd.merge(
    overall_sales,
    territory,
    on='TerritoryKey',
    how='left',
    suffixes=('', '_territory'),
    validate='many_to_one'
)

# Checking the error or empty rows
final_df.isna().sum().head()

# This is like DAX function in Power BI
final_df['Revenue'] = final_df['OrderQuantity'] * final_df['ProductPrice']
final_df['Cost'] = final_df['OrderQuantity'] * final_df['ProductCost']
final_df['Profit'] = final_df['Revenue'] - final_df['Cost']
final_df['ProfitMargin'] = (final_df['Profit'] / final_df['Revenue']) * 100
final_df[['Revenue', 'Cost', 'Profit', 'ProfitMargin']].describe()

# 
final_df['OrderDate'] = pd.to_datetime(final_df['OrderDate'])
final_df['Year'] = final_df['OrderDate'].dt.year
final_df['Month'] = final_df['OrderDate'].dt.month
final_df['MonthName'] = final_df['OrderDate'].dt.month_name()

# Grouping to get the vizualisation
final_df.groupby('Year')['Revenue'].sum()

# %%
final_df.groupby('ProductName')['Revenue'] \
        .sum() \
        .sort_values(ascending=False) \
        .head(10)

# %%
final_df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)

# %%
final_df.groupby('CategoryName')['Profit'].sum().sort_values(ascending=False)

# %%
final_df.shape
final_df.info()

# %%
total_revenue = final_df['Revenue'].sum()
total_profit = final_df['Profit'].sum()
total_orders = final_df['OrderQuantity'].sum()

total_revenue, total_profit, total_orders

# Visualizing the trend chart
yearly_sales = final_df.groupby('Year')['Revenue'].sum()
yearly_sales

plt.figure(figsize=(8,5))
yearly_sales.plot(kind='line', marker='o')
plt.title('Year-wise Revenue Trend')
plt.xlabel('Year')
plt.ylabel('Revenue')
plt.grid(True)
plt.show()

# %%
monthly_sales = final_df.groupby(['Year','Month'])['Revenue'].sum()
monthly_sales

# Finding the Top 10 product details 
top_products = (
    final_df.groupby('ProductName')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
top_products

plt.figure(figsize=(10,6))
top_products.plot(kind='bar')
plt.title('Top 10 Products by Revenue')
plt.xlabel('Product')
plt.ylabel('Revenue')
plt.xticks(rotation=45, ha='right')
plt.show()

# Checing the profit by category 
profit_by_category = (
    final_df.groupby('CategoryName')['Profit']
    .sum()
    .sort_values(ascending=False)
)
profit_by_category

# %%
region_sales = (
    final_df.groupby('Region')['Revenue']
    .sum()
    .sort_values(ascending=False)
)
region_sales

# %%
top_customers = (
    final_df.groupby('CustomerKey')['Revenue']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
top_customers

# Revenue by product category
category_sales = final_df.groupby('CategoryName')['Revenue'].sum()

plt.figure(figsize=(8,5))
category_sales.plot(kind='bar')
plt.title('Revenue by Product Category')
plt.xlabel('Category')
plt.ylabel('Revenue')
plt.show()

# Profit by region 
region_profit = final_df.groupby('Region')['Profit'].sum()

plt.figure(figsize=(8,5))
region_profit.plot(kind='bar')
plt.title('Profit by Region')
plt.xlabel('Region')
plt.ylabel('Profit')
plt.show()

# Monthly Revenue Trend by Year
monthly_sales = final_df.groupby(['Year','Month'])['Revenue'].sum().reset_index()

plt.figure(figsize=(10,5))
seb.lineplot(data=monthly_sales, x='Month', y='Revenue', hue='Year')
plt.title('Monthly Revenue Trend by Year')
plt.show()

# Pie chart usign the Matplotlib
import matplotlib.pyplot as plt

# Example data
labels = ['Bikes', 'Accessories', 'Clothing', 'Components']
sizes = [45, 25, 20, 10]

plt.figure()
plt.pie(
    sizes,
    labels=labels,
    autopct='%1.1f%%',
    startangle=90
)
plt.title('Sales Distribution by Category')
plt.legend(title = "Category", loc = "lower left")
plt.show()


