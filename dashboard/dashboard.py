import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set_theme(style="dark")

st.set_page_config(layout="wide")

def create_delivery_speed_reviews_df(df):
    delivery_speed_reviews_df = df.groupby(by="delivery_speed").agg({
        "review_score": "mean"
    }).reset_index()
    
    return delivery_speed_reviews_df

def create_product_category_reviews_df(df):
    product_category_reviews_df = df.groupby(by="product_category_name_english").review_score.mean().sort_values(ascending=False).reset_index()
    
    return product_category_reviews_df

def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime("%Y-%m")
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.columns = ["order_date", "total_orders", "total_revenue"]

    return monthly_orders_df

def create_customers_demography_df(df):
    customers_demography_df = df.groupby(by=["customer_state", "delivery_speed"]).agg({
        "customer_id": "nunique",
        "process_delivery_time": "mean",
        "review_score": "mean"
    }).sort_values(by="process_delivery_time", ascending=True).reset_index()
    customers_demography_df.columns = ["customer_state", "delivery_speed", "total_customers", "avg_delivery_time", "avg_review_score"]

    return customers_demography_df


all_data_df = pd.read_csv("main_data.csv", sep=",")

datetime_columns = ['order_purchase_timestamp']

for column in datetime_columns:
    all_data_df[column] = pd.to_datetime(all_data_df[column])

all_data_df['order_year'] = all_data_df['order_purchase_timestamp'].dt.year

min_year = all_data_df["order_year"].min()
max_year = all_data_df["order_year"].max()

with st.sidebar:
    st.title("Proyek Analisis Data Dicoding")
    st.write("Pilih tahun untuk melihat analisis data")

    start_year, end_year = st.slider(
        "Pilih tahun untuk melihat analisis data",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

main_df = all_data_df[(all_data_df['order_year'] >= start_year) & (all_data_df['order_year'] <= end_year)]

delivery_speed_reviews_df = create_delivery_speed_reviews_df(main_df)
product_category_reviews_df = create_product_category_reviews_df(main_df)
monthly_orders_df = create_monthly_orders_df(main_df)
customers_demography_df = create_customers_demography_df(main_df)

st.header("Proyek Analisis Data Dicoding")

st.subheader("Monthly Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.total_orders.sum()
    st.metric(label="Total Orders", value=total_orders)

with col2:
    total_revenue = monthly_orders_df.total_revenue.sum()
    st.metric(label="Total Revenue", value=format_currency(total_revenue, 'BRL', locale='pt_BR'))

fig, ax = plt.subplots(figsize=(20, 10))

ax.plot(
    monthly_orders_df["order_date"],
    monthly_orders_df["total_orders"],
    marker="o",
    linestyle="-",
    color="#CC5803"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)

st.pyplot(fig)

st.subheader("Delivery Speed Reviews")

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="delivery_speed",
    y="review_score",
    data=delivery_speed_reviews_df,
    color="#CC5803",
    ax=ax
)
ax.set_title("Delivery Speed vs Review Score", loc="center", size=30)
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)

st.pyplot(fig)

st.subheader("Best and Worst Product Category by Review Score")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(40, 15))

colors = ["#CC5803", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="review_score", y="product_category_name_english", data=product_category_reviews_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Review Score", fontsize=30)
ax[0].set_title("Best 5 Product Category", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="review_score", y="product_category_name_english", data=product_category_reviews_df.sort_values(by="review_score", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Review Score", fontsize=50)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst 5 Product Category", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].set_xlim(ax[0].get_xlim()[::-1])

st.pyplot(fig)

st.subheader("Delivery Time in Every Customer State")

fig, ax = plt.subplots(figsize=(15, 6))

sns.barplot(data=customers_demography_df, x="customer_state", y="avg_delivery_time", hue="delivery_speed", ax=ax)
ax.set_title("Average Delivery Time in Every Customer State", loc="center", size=20)
ax.set_xlabel("Customer State", size=15)
ax.set_ylabel("Average Delivery Time", size=15)
plt.legend(title="Delivery Speed", title_fontsize="13", fontsize="10", loc="upper right")
ax.tick_params(axis='x', labelsize=10, rotation=45)

st.pyplot(fig)

st.subheader("Delivery Speed Impact on Review Score in Every Customer State")

fig, ax = plt.subplots(figsize=(15, 6))

sns.barplot(data=customers_demography_df, x="customer_state", y="avg_review_score", hue="delivery_speed", ax=ax)
ax.set_title("Average Review Score by Delivery Speed", loc="center", fontsize=20)
ax.set_xlabel("Customer State", size=15)
ax.set_ylabel("Average Review Score", size=15)
plt.legend(title="Delivery Speed", title_fontsize="13", fontsize="10", loc="upper right")
ax.tick_params(axis='x', labelsize=10, rotation=45)

st.pyplot(fig)
