# -*- coding: utf-8 -*-
"""Regression (Time Series).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_Z_1kGOWDvhk4mjMdM-DP_gOBItw5e8Q
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd

"""membaca data customer.csv"""

Customer = pd.read_csv('/content/drive/MyDrive/Dataset/Case Study - Customer.csv', sep=';')
print(Customer.head())

"""Data Cleaning"""

Customer.isnull().sum()

Customer[Customer['Marital Status'].isnull()]

Customer['Marital Status'].value_counts()

Customer['Marital Status'] = Customer['Marital Status'].fillna('Single')

Customer.isnull().sum()

Customer.duplicated().sum()

Customer['Income'] = Customer['Income'].replace(',', '.', regex=True).astype(float)

Customer.head()

"""membaca data product.csv"""

Product = pd.read_csv('/content/drive/MyDrive/Dataset/Case Study - Product.csv', sep=';')
print(Product.head())

Product.isnull().sum()

Store = pd.read_csv('/content/drive/MyDrive/Dataset/Case Study - Store.csv', sep=';')
print(Store.head())

Store['Latitude'] = Store['Latitude'].replace(',','.', regex=True).astype(float)
Store['Longitude'] = Store['Longitude'].replace(',','.', regex=True).astype(float)

"""Data Cleaning"""

Store.isnull().sum()

"""Membaca data transaction.csv"""

Transaction = pd.read_csv('/content/drive/MyDrive/Dataset/Case Study - Transaction.csv', sep=';')
print(Transaction.head())

"""Data Cleaning"""

Transaction.isnull().sum()

Transaction['TransactionID'].value_counts()

Transaction[Transaction['TransactionID']=='TR71313']

"""penggabungan beberapa dataset"""

customers_transaction = pd.merge(
    left=Customer,
    right=Transaction,
    how="left",
    left_on="CustomerID",
    right_on="CustomerID"
)
customers_transaction.head()

customers_transaction_product = pd.merge(
    left=Product,
    right=customers_transaction,
    how="left",
    left_on="ProductID",
    right_on="ProductID"
)
customers_transaction_product.head()

all_merge = pd.merge(
    left=Store,
    right=customers_transaction_product,
    how="left",
    left_on="StoreID",
    right_on="StoreID"
)
print(all_merge.head())
print(all_merge.info())

"""mengkonversi kolom 'Date'"""

all_merge['Date'] = pd.to_datetime(all_merge['Date'])

all_merge.info()

"""membuat data baru untuk regression"""

new_data = all_merge.groupby('Date').agg({'Qty' : 'sum'}).reset_index()

new_data

"""visualisasi new_data"""

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
from pandas.plotting import autocorrelation_plot

import matplotlib.pyplot as plt

decomposed = seasonal_decompose(new_data.set_index('Date'))

plt.figure(figsize = (8, 8))
plt.subplot(311)
decomposed.trend.plot(ax=plt.gca())
plt.title('Trend')
plt.subplot(312)
decomposed.seasonal.plot(ax=plt.gca())
plt.title('Seasonality')
plt.subplot(313)
decomposed.resid.plot(ax=plt.gca())
plt.title('Residuals')

plt.tight_layout()

cut_off = round(new_data.shape[0]*0.8)
df_train = new_data[:cut_off]
df_test = new_data[cut_off:].reset_index(drop=True)
df_train.shape, df_test.shape

df_train

df_test

import seaborn as sns

plt.figure(figsize =(20, 5))
sns.lineplot(data = df_train, x=df_train['Date'], y=df_train['Qty'])
sns.lineplot(data = df_test, x=df_test['Date'], y=df_test['Qty'])

"""Machine Learning Regression (Time Series)"""

from sklearn.metrics import mean_absolute_error, mean_squared_error

def rmse(y_actual, y_pred):
  """
    function to calculate RMSE
  """
  print(f'RMSE Value {mean_squared_error(y_actual, y_pred)**0.5}')

def eval(y_actual, y_pred):
  """
    function to eval machine learning modelling
  """
  rmse(y_actual, y_pred)
  print(f'MAE Value {mean_absolute_error(y_actual, y_pred)}')

#ARIMA
from statsmodels.tsa.arima.model import ARIMA

df_train = df_train.set_index('Date')
df_test = df_test.set_index('Date')

y = df_train['Qty']
ARIMAmodel = ARIMA(y, order=(40, 2, 1))
ARIMAmodel = ARIMAmodel.fit()

y_pred = ARIMAmodel.get_forecast(len(df_test))

y_pred_df = y_pred.conf_int()
y_pred_df['predictions'] = ARIMAmodel.predict(start = y_pred_df.index[0], end = y_pred_df.index[-1])
y_pred_df.index = df_test.index
y_pred_out = y_pred_df['predictions']
eval(df_test['Qty'], y_pred_out)

plt.figure(figsize =(20, 5))
plt.plot(df_train['Qty'])
plt.plot(df_test['Qty'], color='red')
plt.plot(y_pred_out, color='black', label='ARIMA predictions')
plt.legend()