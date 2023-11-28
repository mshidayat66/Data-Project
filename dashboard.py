#Menyiapkan semua library yang dibutuhkan
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_sum_order_items_df(all_df):
  sum_order_items_df = all_df.groupby("product_category_name").order_id.count().sort_values(ascending=False).reset_index()
  return sum_order_items_df

def create_bystate_df(all_df):
  bystate_df = all_df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
  bystate_df.rename(columns={
      "customer_unique_id": "customer_count"
  }, inplace=True)
  return bystate_df

def create_rfm_df(all_df):
  rfm_df = all_df.groupby(by="customer_unique_id", as_index=False).agg({
      "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
      "order_id": "nunique", # menghitung jumlah order
      "total_price": "sum" # menghitung jumlah revenue yang dihasilkan
  })
  rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]
  
  # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
  rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
  recent_date = pd.to_datetime(order["order_purchase_timestamp"]).dt.date.max()
  rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
  rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
  return rfm_df

all_df = pd.read_csv('all_data.csv')
order = pd.read_csv('orders_dataset.csv')

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_df["order_purchase_timestamp"] <= str(end_date))]

sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Olist Store Dashboard :sparkles:')

st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0], hue='product_category_name')
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="order_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

st.pyplot(fig)

st.subheader("Customer Demographics")

fig, ax = plt.subplots(figsize=(10, 5))
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors_,
    ax=ax  # Menentukan sumbu pada objek subplot
)
ax.set_title("Number of Customer by States", loc="center", fontsize=15)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=12)

st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

fig, axs = plt.subplots(ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=axs[0])
axs[0].set_ylabel(None)
axs[0].set_xlabel(None)
axs[0].set_title("By Recency (days)", loc="center", fontsize=18)
axs[0].tick_params(axis='x', labelsize=15)
axs[0].tick_params(axis='x', rotation=90)  # Atur rotasi label sumbu x

sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=axs[1])
axs[1].set_ylabel(None)
axs[1].set_xlabel(None)
axs[1].set_title("By Frequency", loc="center", fontsize=18)
axs[1].tick_params(axis='x', labelsize=15)
axs[1].tick_params(axis='x', rotation=90)  # Atur rotasi label sumbu x

sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=axs[2])
axs[2].set_ylabel(None)
axs[2].set_xlabel(None)
axs[2].set_title("By Monetary", loc="center", fontsize=18)
axs[2].tick_params(axis='x', labelsize=15)
axs[2].tick_params(axis='x', rotation=90)  # Atur rotasi label sumbu x

st.pyplot(fig)

st.caption('Copyright (c) Olist Store 2023')