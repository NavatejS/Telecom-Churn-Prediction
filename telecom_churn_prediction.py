# -*- coding: utf-8 -*-
# Telecom Churn Prediction.ipynb

### Import Libraries

# Import Libraries
import numpy as np
import pandas as pd
from numpy import math
from numpy import loadtxt
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline
from matplotlib import rcParams
!pip install pymysql
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

import numpy as np
import seaborn as sns
from scipy.stats import *
import math

from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn import metrics
from sklearn.metrics import roc_curve
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold
from xgboost import XGBClassifier
from xgboost import XGBRFClassifier
from sklearn.tree import export_graphviz

!pip install shap==0.40.0
import shap
import graphviz
sns.set_style('darkgrid')

import warnings
warnings.filterwarnings('ignore')

### Dataset Loading

# Load Dataset
def mysql(query:'Write the query here .'):
    try:
        engine_db = create_engine('mysql+pymysql://almafolk:8l39zk60q@learning-activity.cejogcrmn6il.ap-south-1.rds.amazonaws.com:3306/assignment', poolclass=NullPool )
        conn = engine_db.connect()
        # Reading Data
        df = pd.read_sql_query(query, conn)

        #if your connection object is named conn
        if not conn.closed:
            conn.close()
        engine_db.dispose()
        return df
    except Exception as e:
        print(e)

# Importing the dataset
dataset = mysql('''SELECT * FROM telecom_churn''')

# Dataset First
dataset.head()

# Dataset Rows & Columns
dataset.shape

# Dataset Info
dataset.info()

# Dataset Duplicate Value Count
len(dataset[dataset.duplicated()])

# Missing Values/Null Values Count
print(dataset.isnull().sum())

# Visualizing the missing values
# Checking Null Value by plotting Heatmap
sns.heatmap(dataset.isnull(), cbar=False)

# Dataset Columns
dataset.columns

# Dataset Describe
dataset.describe(include='all')

"""### Data Wrangling Code"""

# Write your code to make your dataset analysis ready.
# Create a copy of the current dataset and assigning to df
df=dataset.copy()
# Checking Shape of True Value
print("No. of customers Churning : -",len(df[df['Churn']==True]))
# Assigning churn customers data to variable df_churn
df_churn=df[(df['Churn']==True)]

# Churn data groupby Area Code Wise
pd.DataFrame(df.groupby('Area code')['Churn'].value_counts().reset_index(name="Count"))

# Function to get all area code mean & median while passing area code and dataframe.
def get_mean_median(df,areacode):
  try:
    return pd.concat([df[(df['Churn']==True)&(df['Area code']==areacode)].describe().iloc[1],
            df[(df['Churn']==True)&(df['Area code']==areacode)].describe().iloc[5]],
            axis=1).rename(columns={"50%":"median"}).fillna("-")
  except:
    print("Invalid Area Code")

# Getting Mean Median for area code 408
get_mean_median(df=df,areacode=408)

# Getting Mean Median for area code 415
get_mean_median(df=df,areacode=415)

# Getting Mean Median for area code 510
get_mean_median(df=df,areacode=510)

# Getting Unique States
print(df['State'].unique())
print(" ")
# Getting Unique States Count
print("Unique States Count is ",df['State'].nunique(),".")

# Churn Counts grouby State wise
pd.DataFrame(df.groupby('State')['Churn'].value_counts(  ).reset_index(name="Count"))

# Assigning churn customers data with no international plan
df_churn_intl_no=df_churn[df_churn['International plan']=='No']
# Assigning churn customers data with international plan
df_churn_intl_yes=df_churn[df_churn['International plan']=='Yes']

# Churn customers data with no international plan value counts
df_churn_intl_no['Area code'].value_counts()

# Creating call duration column for customers with no international plan
df_churn_intl_no['Days_1call_duration']=df_churn_intl_no['Total day minutes']/df_churn_intl_no['Total day calls']
df_churn_intl_no['intern_1call_duration']=df_churn_intl_no['Total intl minutes']/df_churn_intl_no['Total intl calls']

df_churn_intl_no['evening_1call_duration']=df_churn_intl_no['Total eve minutes']/df_churn_intl_no['Total eve calls']
df_churn_intl_no['night_1call_duration']=df_churn_intl_no['Total night minutes']/df_churn_intl_no['Total night calls']

# Creating price rate per minute column for customers with international plan
df_churn_intl_yes['international_rate_per_min']=df_churn_intl_yes['Total intl charge']/df_churn_intl_yes['Total intl minutes']
df_churn_intl_yes['day_rate_per_min']=df_churn_intl_yes['Total day charge']/df_churn_intl_yes['Total day minutes']
df_churn_intl_yes['eve_rate_per_min']=df_churn_intl_yes['Total eve charge']/df_churn_intl_yes['Total eve minutes']
df_churn_intl_yes['night_rate_per_min']=df_churn_intl_yes['Total night charge']/df_churn_intl_yes['Total night minutes']

# Getting Mean Median for area code 408 with no international plan
get_mean_median(df=df_churn_intl_no,areacode=408)

# Getting Mean Median for area code 415 with no international plan
get_mean_median(df=df_churn_intl_no,areacode=415)

# Getting Mean Median for area code 510 with no international plan
get_mean_median(df=df_churn_intl_no,areacode=510)

# Getting Mean Median for area code 408 with international plan
get_mean_median(df=df_churn_intl_yes,areacode=408)

# Getting Mean Median for area code 415 with international plan
get_mean_median(df=df_churn_intl_yes,areacode=415)

# Getting Mean Median for area code 510 with international plan
get_mean_median(df=df_churn_intl_yes,areacode=510)

# Checking Number of voice mail sent for customers with no international plan
df_churn_intl_no['Number vmail messages'].value_counts().reset_index(name="User Count")

# Checking Number of voice mail sent for customers with international plan
df_churn_intl_yes['Number vmail messages'].value_counts().reset_index(name="User Count")

# Assigning Customers data with no international plan and voice mail plan
voice_mail_plan_yes =df_churn_intl_no[df_churn_intl_no['Voice mail plan']=='Yes']
voice_mail_plan_yes.describe()

# Assigning customers data with international plan and no voice mail plan
voice_mail_plan_yes=df_churn_intl_yes[df_churn_intl_yes['Voice mail plan']=='Yes']
voice_mail_plan_yes.describe()

# Assigning customers data with international plan and no voice plan
df_true_intl=df_churn[(df_churn['International plan']=='Yes')&(df_churn['Voice mail plan']=='No')]
df_true_intl.describe()

# Assigning Customers data with no international plan and having voice mail plan
df_true_voice=df_churn[(df_churn['International plan']=='No')&(df_churn['Voice mail plan']=='Yes')]
df_true_voice.describe()

# Assigning Customers data with no international plan and no voice mail plan
df_true_no=df_churn[(df_churn['International plan']=='No')&(df_churn['Voice mail plan']=='No')]
df_true_no.describe()

# Assigning Customers data with both international plan and voice mail plan
df_true_yes=df_churn[(df_churn['International plan']=='Yes')&(df_churn['Voice mail plan']=='Yes')]
df_true_yes.describe()

print("Churned Customer Shape:-",df_churn.shape)
print(" ")
print("customers data with international plan and no voice plan:-",df_true_intl.shape)
print(" ")
print("Customers data with no international plan and having voice mail plan:-",df_true_voice.shape)
print(" ")
print("Customers data with no international plan and no voice mail plan:-",df_true_no.shape)
print(" ")
print("Customers data with both international plan and voice mail plan:-",df_true_yes.shape)
print(" ")

print("Customers data with no international plan and having voice mail plan maximum voice message sent:-",df_true_voice['Number vmail messages'].max())
print(" ")
# Assigning customers data to respective area codes
df_true_voice_415=df_true_voice[df_true_voice['Area code']==415]
df_true_voice_510=df_true_voice[df_true_voice['Area code']==510]
df_true_voice_408=df_true_voice[df_true_voice['Area code']==408]

print("Customers data with no international plan and having voice mail plan voice message sent in area 415 mean, median:-",df_true_voice_415['Number vmail messages'].mean(),",",df_true_voice_415['Number vmail messages'].median())
print(" ")

print("Customers data with no international plan and having voice mail plan customer service calls in area 415 mean, median:-",df_true_voice_415['Customer service calls'].mean(),",",df_true_voice_415['Customer service calls'].median())
print(" ")

print("Customers data with no international plan and having voice mail plan voice message sent in area 510 max, mean, median & customer service calls in area 510 mean, median:-"
,df_true_voice_510['Number vmail messages'].max(),",",df_true_voice_510['Number vmail messages'].mean(),",",df_true_voice_510['Number vmail messages'].median(),",",df_true_voice_510['Customer service calls'].mean(),",",df_true_voice_510['Customer service calls'].median())
print(" ")

print("Customers data with no international plan and having voice mail plan voice message sent in area 408 max, mean, median & customer service calls in area 408 mean, median:-"
,df_true_voice_408['Number vmail messages'].max(),",",df_true_voice_408['Number vmail messages'].mean(),",",df_true_voice_408['Number vmail messages'].median(),",",df_true_voice_408['Customer service calls'].mean(),",",df_true_voice_408['Customer service calls'].median())
print(" ")
# Assigning customers data to respective area codes
df_true_yes_415=df_true_yes[df_true_yes['Area code']==415]
df_true_yes_510=df_true_yes[df_true_yes['Area code']==510]
df_true_yes_408=df_true_yes[df_true_yes['Area code']==408]

print("Customers data with both international plan and voice mail plan customer service calls mean & voice mail sent max :-"
,df_true_yes['Customer service calls'].mean(),df_true_yes['Number vmail messages'].max())
print(" ")
print("Customers data with both international plan and voice mail plan in area 415 voice mail sent max, mean, median :-"
,df_true_yes_415['Number vmail messages'].max(),",",df_true_yes_415['Number vmail messages'].mean(),",",df_true_yes_415['Number vmail messages'].median())
print(" ")
print("Customers data with both international plan and voice mail plan in area 510 voice mail sent max, mean, median :-"
,df_true_yes_510['Number vmail messages'].max(),",",df_true_yes_510['Number vmail messages'].mean(),",",df_true_yes_510['Number vmail messages'].median())
print(" ")
print("Customers data with both international plan and voice mail plan in area 408 voice mail sent max, mean, median :-"
,df_true_yes_408['Number vmail messages'].max(),",",df_true_yes_408['Number vmail messages'].mean(),",",df_true_yes_408['Number vmail messages'].median())

# Assigning customers data with no international plan and having voice mail plan state list in area 415
df_true_voice_415_states=list(df_true_voice_415['State'].unique())
print("States list where customers data with no international plan and having voice mail plan in area 415 :-",df_true_voice_415_states)
print(" ")
# Assigning customers data  with both international plan and voice mail plan state list in area 415
df_true_yes_415_states=list(df_true_yes_415['State'].unique())
print("States List where customers data  with both international plan and voice mail plan in area 415 :-",df_true_yes_415_states)
print(" ")
# Getting Poor Network connectivity states based on our hypothetical logic
poor_netwok_states_415=set(df_true_voice_415_states).intersection(set(df_true_yes_415_states))
print("Poor Network connectivity states in area 415 :-",list(poor_netwok_states_415))

# Assigning Customers data with no international plan and having voice mail plan state list in area 408
df_true_voice_408_states=list(df_true_voice_408['State'].unique())
print("States list Customers data with no international plan and having voice mail plan state list in area 408 :-",df_true_voice_408_states)
print(" ")
# Assigning customers data  with both international plan and voice mail plan state list in area 408
df_true_yes_408_states=list(df_true_yes_408['State'].unique())
print("States list customers data  with both international plan and voice mail plan state list in area 408 :-",df_true_yes_408_states)
print(" ")
# Getting Poor Network connectivity states based on our hypothetical logic
poor_netwok_states_408=set(df_true_voice_408_states).intersection(set(df_true_yes_408_states))
# Getting Common Poor Network connectivity states based on our hypothetical logic from both area 408 & 415
poor_network_states=poor_netwok_states_415.union(poor_netwok_states_408)
print("Poor Network connectivity states in both area 415, 408 :-",list(poor_network_states))

# Assigning Customers data with no international plan and having voice mail plan state list in area 510
df_true_voice_510_states=list(df_true_voice_510['State'].unique())
print("States list Customers data with no international plan and having voice mail plan state list in area 510 :-",df_true_voice_510_states)
print(" ")
# Assigning customers data  with both international plan and voice mail plan state list in area 510
df_true_yes_510_states=list(df_true_yes_510['State'].unique())
print("States list customers data  with both international plan and voice mail plan state list in area 510 :-",df_true_yes_510_states)
print(" ")
# Getting Common  Network Maintainance states based on our hypothetical logic from area 510
maintainence_states=set(df_true_voice_510_states).intersection(set(df_true_yes_510_states))
print("Network needs to be maintenanced in states :-",list(maintainence_states))

print(f"Poor Netwok States are {list(poor_network_states)} and Network needs to be maintenanced in states {list(maintainence_states)}.")

# Chart - 1 visualization code
# Dependant Column Value Counts
print(dataset.Churn.value_counts())
print(" ")
# Dependant Variable Column Visualization
dataset['Churn'].value_counts().plot(kind='pie',
                              figsize=(15,6),
                               autopct="%1.1f%%",
                               startangle=90,
                               shadow=True,
                               labels=['Not Churn(%)','Churn(%)'],
                               colors=['skyblue','red'],
                               explode=[0,0]
                              )

# Chart - 2 visualization code
# Showing Average True Churn Percentage state wise
# Showing top 10 churned state
print((dataset.groupby(['State'])['Churn'].mean()*100).sort_values(ascending = False).reset_index(name="Average True CHurn %").head(10))
print(" ")

# State vs. average true churn percantage visualization code
# Vizualizing top 10 churned state
plt.rcParams['figure.figsize'] = (12, 7)
color = plt.cm.copper(np.linspace(0, 0.5, 20))
((dataset.groupby(['State'])['Churn'].mean())*100).sort_values(ascending = False).head(10).plot.bar(color = ['violet','indigo','b','g','y','orange','r'])
plt.title(" State with most churn percentage", fontsize = 20)
plt.xlabel('state', fontsize = 15)
plt.ylabel('percentage', fontsize = 15)
plt.show()

# Showing Average True Churn Percentage state wise
# Showing top 10 churned state
print((dataset.groupby(['State'])['Churn'].mean()*100).sort_values(ascending = True).reset_index(name="Average True CHurn %").head(10))
print(" ")

# State vs. average true churn percantage visualization code
# Vizualizing bottom 10 churned state
plt.rcParams['figure.figsize'] = (12, 7)
color = plt.cm.copper(np.linspace(0, 0.5, 20))
((dataset.groupby(['State'])['Churn'].mean())*100).sort_values(ascending = True).head(10).plot.bar(color = ['violet','indigo','b','g','y','orange','r'])
plt.title(" State with most churn percentage", fontsize = 20)
plt.xlabel('state', fontsize = 15)
plt.ylabel('percentage', fontsize = 15)
plt.show()

# Chart - 3 visualization code
# One Digit Account Length
print(dataset[dataset['Account length']<=9].loc[:,['Churn']].value_counts())
print(" ")

# Visualizing One Digit Account Length Based on Churn percentage
dataset[dataset['Account length']<=9].loc[:,['Churn']].value_counts().plot(kind='pie',
                              figsize=(15,6),
                               autopct="%1.1f%%",
                               startangle=90,
                               shadow=True,
                               labels=['No','Yes'],
                               colors=['skyblue','red'],
                               explode=[0,0]
                              )

# Two Digit Account Length
print(dataset[(dataset['Account length']<=99) & (dataset['Account length']>=10)].loc[:,['Churn']].value_counts())
print(" ")

# Visualizing Two Digit Account Length Based on Churn percentage
dataset[(dataset['Account length']<=99) & (dataset['Account length']>=10)].loc[:,['Churn']].value_counts().plot(kind='pie',
                              figsize=(15,6),
                               autopct="%1.1f%%",
                               startangle=90,
                               shadow=True,
                               labels=['No','Yes'],
                               colors=['skyblue','red'],
                               explode=[0,0]
                              )

# Three Digit Account Length
print(dataset[(dataset['Account length']<=dataset['Account length'].max()) & (dataset['Account length']>=100)].loc[:,['Churn']].value_counts())
print(" ")

# Visualizing Three Digit Account Length Based on Churn percentage
dataset[(dataset['Account length']<=dataset['Account length'].max()) & (dataset['Account length']>=100)].loc[:,['Churn']].value_counts().plot(kind='pie',
                              figsize=(15,6),
                               autopct="%1.1f%%",
                               startangle=90,
                               shadow=True,
                               labels=['No','Yes'],
                               colors=['skyblue','red'],
                               explode=[0,0]
                              )

# Box Plot for Account Length attribute
dataset.boxplot(column='Account length',by='Churn')

# Chart - 4 visualization code
# Area Code wise average churn Percentage
print(dataset.groupby('Area code')['Churn'].mean()*100)
print(" ")

# Visualizing code for Area Code wise average churn percentage
a1= list(['408','415' , '510'])
b1= dataset.groupby('Area code')['Churn'].mean()*100
plt.bar(a1,b1, color=['r','b','g'])

plt.rcParams['figure.figsize'] = (6, 5)


plt.xlabel('Area code', fontsize = 15)
plt.ylabel('churn percentage', fontsize = 15)
plt.show()

# Chart - 5 visualization code
# Visualizing Percentage of customers taken international plan
dataset['International plan'].value_counts().plot(kind='pie',
                              figsize=(15,6),
                               autopct="%1.1f%%",
                               startangle=90,
                               shadow=True,
                               labels=['No','Yes'],
                               colors=['skyblue','red'],
                               explode=[0,0]
                              )

# Assigning values for furthur charts
i1 = dataset['International plan'].unique()
i2 = dataset.groupby('International plan')['Churn'].mean()*100
i3 = dataset.groupby(['International plan'])['Total intl charge'].mean()
i4 = dataset.groupby(["Churn"])['Total intl minutes'].mean()

# Visualizing code for people churning percentage having international plan
plt.rcParams['figure.figsize'] = (6, 7)

plt.bar(i1,i2 , color=['b','r'])

plt.title(" Percentage of people leaving", fontsize = 20)
plt.xlabel('International plan', fontsize = 15)
plt.ylabel('percentage', fontsize = 15)
plt.show()

# Visualizing code for average calling charge of customers having international plan
plt.rcParams['figure.figsize'] = (6, 7)

plt.bar(i1,i3, color=['b','r'])
plt.title(" Average charge of people", fontsize = 20)
plt.xlabel('International plan', fontsize = 15)
plt.ylabel(' charge', fontsize = 15)
plt.show()

# Visualizing code for average minutes takled by customers having international plan
plt.rcParams['figure.figsize'] = (6, 7)

plt.bar(i1,i4, color=['b','r'])
plt.title(" Average minute people talk", fontsize = 20)
plt.xlabel('International plan', fontsize = 15)
plt.ylabel(' Minutes', fontsize = 15)
plt.show()

"""#### Chart - 6 - Voice Mail (Univariate + Bivariate)"""

# Chart - 5 visualization code
# vizualizing code for customers percentage having voice mail plan
dataset['Voice mail plan'].value_counts().plot(kind='pie',
                              figsize=(15,6),
                               autopct="%1.1f%%",
                               startangle=90,
                               shadow=True,
                               labels=['No','Yes'],
                               colors=['skyblue','red'],
                               explode=[0,0]
                              )

# Vizualizing code for customers churning while having voice mail plan
plt.rcParams['figure.figsize'] = (6, 7)

cc1=list(['no','yes'])
cc2=dataset.groupby('Voice mail plan')['Churn'].mean()*100
plt.bar(cc1,cc2, color=['b','r'])

plt.title(" Percentage of people leaving", fontsize = 20)
plt.xlabel('Voice mail plan', fontsize = 15)
plt.ylabel('percentage', fontsize = 15)
plt.show()

"""#### Chart - 7- Overall Calls (Bivariate)"""

# Chart - 7 visualization code
# Geeting means of churn vs total day calls, total day minutes, total day charge
print(dataset.groupby(["Churn"])['Total day calls'].mean())
print(" ")
print(dataset.groupby(["Churn"])['Total day minutes'].mean())
print(" ")
print(dataset.groupby(["Churn"])['Total day charge'].mean())

# 18% more min    18% more charge    no insight

# Vizualizing Total day minutes vs total day charge
cdd = sns.scatterplot(x="Total day minutes", y="Total day charge", hue="Churn", data=dataset)

# Geeting means of churn vs total eve calls, total eve minutes, total evening charge
print(dataset.groupby(["Churn"])['Total eve calls'].mean())
print(" ")
print(dataset.groupby(["Churn"])['Total eve minutes'].mean())
print(" ")
print(dataset.groupby(["Churn"])['Total eve charge'].mean())

# Vizualizing total evening minutes vs total evening charge
cdd = sns.scatterplot(x="Total eve minutes", y="Total eve charge", hue="Churn", data=dataset)

# Getting means of churn vs total night calls, total m=night minutes, total night charge
print(dataset.groupby(["Churn"])['Total night calls'].mean())
print(" ")
print(dataset.groupby(["Churn"])['Total night minutes'].mean())
print(" ")
print(dataset.groupby(["Churn"])['Total night charge'].mean())

# Vizualizing Total nights minutes vs total night charge
cdd = sns.scatterplot(x="Total night minutes", y="Total night charge", hue="Churn", data=dataset)

# Import pandas library
import pandas as pd

# initialize list of lists
data1 = [['Total day minutes',175.17 , 206.91], ['Total day charge',29.78, 35.17]]

#7.012,6.12,6.86

# Create the pandas DataFrame
minutes_code1 = pd.DataFrame(data1, columns = ['day', 'dont churn',' churn'])

# print dataframe.
minutes_code1

# Vizualizing code for the above created dataframe
plt.rcParams['figure.figsize'] = (8, 6)


minutes_code1.plot(kind='bar', x='day',ylabel='mean  ')

# Import pandas library
import pandas as pd

# initialize list of lists
data2 = [ ['Total eve minutes',199.04, 212.41], ['Total night minutes',200.13,205.23]]

#7.012,6.12,6.86

# Create the pandas DataFrame
minutes_code2 = pd.DataFrame(data2, columns = ['minutes', 'dont churn',' churn'])

# print dataframe.
minutes_code2

# Vizualizing teh above created dataframe
plt.rcParams['figure.figsize'] = (8,6)


minutes_code2.plot(kind='bar', x='minutes',xlabel='minutes',ylabel='mean of churn ')

# Import pandas library
import pandas as pd

# initialize list of lists
data3 = [ ['Total eve charge',16.91, 18.05], ['Total night charge',9,9.23]]


# Create the pandas DataFrame
minutes_code3 = pd.DataFrame(data3, columns = ['charge', 'dont churn',' churn'])

# print dataframe.
minutes_code3

# Vizualizing code for the above dataset
plt.rcParams['figure.figsize'] = (8,6)


minutes_code3.plot(kind='bar', x='charge',ylabel='mean charge')

"""#### Chart - 8 - Customer Service Calls (Bivariate)"""

# Chart - 8 visualization code
# Visualizing churn rate per customer service calls
plt.rcParams['figure.figsize'] = (12, 8)


s1=list(dataset['Customer service calls'].unique())
s2=list(dataset.groupby(['Customer service calls'])['Churn'].mean()*100)
plt.bar(s1,s2, color = ['violet','indigo','b','g','y','orange','r'])


plt.title(" Churn rate per service call", fontsize = 20)
plt.xlabel('No of cust service call', fontsize = 15)
plt.ylabel(' percentage', fontsize = 15)
plt.show()

# Chart - 9 visualization code
# Visualizing code of hist plot for each columns to know the data distibution
for col in dataset.describe().columns:
  fig=plt.figure(figsize=(9,6))
  ax=fig.gca()
  feature= (dataset[col])
  sns.distplot(dataset[col])
  ax.axvline(feature.mean(),color='magenta', linestyle='dashed', linewidth=2)
  ax.axvline(feature.median(),color='cyan', linestyle='dashed', linewidth=2)
  ax.set_title(col)
plt.show()

# Visualizing code of box plot for each columns to know the data distibution
for col in dataset.describe().columns:
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()
    dataset.boxplot( col, ax = ax)
    ax.set_title('Label by ' + col)
    #ax.set_ylabel("Churn")
plt.show()

# Correlation Heatmap visualization code
corr = dataset.corr()
cmap = cmap=sns.diverging_palette(5, 250, as_cmap=True)

def magnify():
    return [dict(selector="th",
                 props=[("font-size", "7pt")]),
            dict(selector="td",
                 props=[('padding', "0em 0em")]),
            dict(selector="th:hover",
                 props=[("font-size", "12pt")]),
            dict(selector="tr:hover td:hover",
                 props=[('max-width', '200px'),
                        ('font-size', '12pt')])
]

corr.style.background_gradient(cmap, axis=1)\
    .set_properties(**{'max-width': '80px', 'font-size': '10pt'})\
    .set_caption("Hover to magify")\
    .set_precision(2)\
    .set_table_styles(magnify())

"""#### Chart - 11 - Pair Plot"""

# Pair Plot visualization code
sns.pairplot(dataset, hue="Churn")

# Creating Parameter Class
class findz:
  def proportion(self,sample,hyp,size):
    return (sample - hyp)/math.sqrt(hyp*(1-hyp)/size)
  def mean(self,hyp,sample,size,std):
    return (sample - hyp)*math.sqrt(size)/std
  def varience(self,hyp,sample,size):
    return (size-1)*sample/hyp

variance = lambda x : sum([(i - np.mean(x))**2 for i in x])/(len(x)-1)
zcdf = lambda x: norm(0,1).cdf(x)
# Creating a function for getting P value
def p_value(z,tailed,t,hypothesis_number,df,col):
  if t!="true":
    z=zcdf(z)
    if tailed=='l':
      return z
    elif tailed == 'r':
      return 1-z
    elif tailed == 'd':
      if z>0.5:
        return 2*(1-z)
      else:
        return 2*z
    else:
      return np.nan
  else:
    z,p_value=stats.ttest_1samp(df[col],hypothesis_number)
    return p_value

# Conclusion about the P - Value
def conclusion(p):
  significance_level = 0.05
  if p>significance_level:
    return f"Failed to reject the Null Hypothesis for p = {p}."
  else:
    return f"Null Hypothesis rejected Successfully for p = {p}"

# Initializing the class
findz = findz()

### Hypothetical Statement - 1

# Perform Statistical Test to obtain P-Value
hypo_1=dataset[(dataset["Churn"]==False) & (dataset["Voice mail plan"]=="Yes")]
# Getting the required parameter values for hypothesis testing
hypothesis_number = 30
sample_mean = hypo_1["Number vmail messages"].mean()
size = len(hypo_1)
std=(variance(hypo_1["Number vmail messages"]))**0.5

# Getting Z value
z = findz.mean(hypothesis_number,sample_mean,size,std)
# Getting P - Value
p = p_value(z=z,tailed='l',t="false",hypothesis_number=hypothesis_number,df=hypo_1,col="Number vmail messages")
# Getting Conclusion
print(conclusion(p))

# Visualizing code of hist plot for required columns to know the data distibution

fig=plt.figure(figsize=(9,6))
ax=fig.gca()
feature= (hypo_1["Number vmail messages"])
sns.distplot(hypo_1["Number vmail messages"])
ax.axvline(feature.mean(),color='magenta', linestyle='dashed', linewidth=2)
ax.axvline(feature.median(),color='cyan', linestyle='dashed', linewidth=2)
ax.set_title(col)
plt.show()

### Hypothetical Statement - 2

# Perform Statistical Test to obtain P-Value
hypo_2=dataset[(dataset["Churn"]==False)]
# Getting the required parameter values for hypothesis testing
hypothesis_number = 2
sample_mean = hypo_2["Customer service calls"].mean()
size = len(hypo_2)
std=(variance(hypo_2["Customer service calls"]))**0.5

# Getting Z value
z = findz.mean(hypothesis_number,sample_mean,size,std)
# Getting P - Value
p = p_value(z=z,tailed='r',t="false",hypothesis_number=hypothesis_number,df=hypo_2,col="Customer service calls")
# Getting Conclusion
print(conclusion(p))

mean_median_difference=hypo_2["Customer service calls"].mean()- hypo_2["Customer service calls"].median()
print("Mean Median Difference is :-",mean_median_difference)

### Hypothetical Statement - 3

# Perform Statistical Test to obtain P-Value
hypo_3=dataset[(dataset["Churn"]==True)]
hypo_3["total call minutes"]=hypo_3["Total day minutes"]+hypo_3["Total eve minutes"]+hypo_3["Total night minutes"]+hypo_3["Total intl minutes"]
# Getting the required parameter values for hypothesis testing
hypothesis_number = 500
sample_mean = hypo_3["total call minutes"].mean()
size = len(hypo_3)
std=(variance(hypo_3["total call minutes"]))**0.5

# Getting Z value
z = findz.mean(hypothesis_number,sample_mean,size,std)
# Getting P - Value
p = p_value(z=z,tailed='d',t="true",hypothesis_number=hypothesis_number,df=hypo_3,col="total call minutes")
# Getting Conclusion
print(conclusion(p))

# Visualizing code of hist plot for required columns to know the data distibution

fig=plt.figure(figsize=(9,6))
ax=fig.gca()
feature= (hypo_3["total call minutes"])
sns.distplot(hypo_3["total call minutes"])
ax.axvline(feature.mean(),color='magenta', linestyle='dashed', linewidth=2)
ax.axvline(feature.median(),color='cyan', linestyle='dashed', linewidth=2)
ax.set_title(col)
plt.show()

mean_median_difference=hypo_3["total call minutes"].median()- hypo_3["total call minutes"].mean()
print("Mean Median Difference is :-",mean_median_difference)

# Creating a copy of the dataset for further feature engineering
df=dataset.copy()

# Handling Missing Values & Missing Value Imputation
# Missing Values/Null Values Count
print(df.isnull().sum())

# Visualizing the missing values
# Checking Null Value by plotting Heatmap
sns.heatmap(df.isnull(), cbar=False)

# Handling Outliers & Outlier treatments
# To separate the symmetric distributed features and skew symmetric distributed features
df["Area code"]=df["Area code"].astype('str')
symmetric_feature=[]
non_symmetric_feature=[]
for i in df.describe().columns:
  if abs(df[i].mean()-df[i].median())<0.2:
    symmetric_feature.append(i)
  else:
    non_symmetric_feature.append(i)

# Getting Symmetric Distributed Features
print("Symmetric Distributed Features : -",symmetric_feature)

# Getting Skew Symmetric Distributed Features
print("Skew Symmetric Distributed Features : -",non_symmetric_feature)

# Removing Customer Service Calls column from the list as it's an important factor
# which can't be treated as outliers here will is already leading to higher churn as we have seen furing analysis.
non_symmetric_feature.pop()

# For Symmetric features defining upper and lower boundry
def outlier_treatment(df,feature):
  upper_boundary= df[feature].mean()+3*df[feature].std()
  lower_boundary= df[feature].mean()-3*df[feature].std()
  return upper_boundary,lower_boundary

# Restricting the data to lower and upper boundry
for feature in symmetric_feature:
  df.loc[df[feature]<= outlier_treatment(df=df,feature=feature)[1], feature]=outlier_treatment(df=df,feature=feature)[1]
  df.loc[df[feature]>= outlier_treatment(df=df,feature=feature)[0], feature]=outlier_treatment(df=df,feature=feature)[0]

# For Skew Symmetric features defining upper and lower boundry
#Outer Fence
def outlier_treatment_skew(df,feature):
  IQR= df[feature].quantile(0.75)- df[feature].quantile(0.25)
  lower_bridge =df[feature].quantile(0.25)-3*IQR
  upper_bridge =df[feature].quantile(0.25)+3*IQR
  return upper_bridge,lower_bridge

# Restricting the data to lower and upper boundry
for feature in non_symmetric_feature:
  df.loc[df[feature]<= outlier_treatment_skew(df=df,feature=feature)[1], feature]=outlier_treatment_skew(df=df,feature=feature)[1]
  df.loc[df[feature]>= outlier_treatment_skew(df=df,feature=feature)[0], feature]=outlier_treatment_skew(df=df,feature=feature)[0]

# After Outlier Treatment showing the dataset distribution using strip plot
# Visualising  code for the numerical columns
for col in df.describe().columns:
  fig=plt.figure(figsize=(9,6))
  sns.stripplot(df[col])

# Encode your categorical columns
# Getting the categorical columns
categorical_columns=list(set(df.columns.to_list()).difference(set(df.describe().columns.to_list())))
print("Categorical Columns are :-", categorical_columns)

# Getting dictionaries for Label Encoding
dict1={True:1,False:0}
dict2={"Yes":1,"No":0}
area_code_list=sorted(list(df["Area code"].unique()))
dict3=dict(zip(area_code_list,range(0,len(area_code_list))))

# Label Encoding in the dataset
# df['Churn']=df['Churn'].map(dict1)
df['International plan']=df['International plan'].map(dict2)
df['Voice mail plan']=df['Voice mail plan'].map(dict2)
df['Area code']=df['Area code'].map(dict3)

# One Hot Encoding on State Column
df=pd.get_dummies(df,drop_first= True)

df["Churn"]

### Feature Manipulation

# Manipulate Features to minimize feature correlation and create new features
# Creating call duration column for customers with no international plan
df['Days_1call_duration']=df['Total day minutes']/df['Total day calls']
df['intern_1call_duration']=df['Total intl minutes']/df['Total intl calls']

df['evening_1call_duration']=df['Total eve minutes']/df['Total eve calls']
df['night_1call_duration']=df['Total night minutes']/df['Total night calls']

# Creating price rate per minute column for customers with international plan
df['international_rate_per_min']=df['Total intl charge']/df['Total intl minutes']
df['day_rate_per_min']=df['Total day charge']/df['Total day minutes']
df['eve_rate_per_min']=df['Total eve charge']/df['Total eve minutes']
df['night_rate_per_min']=df['Total night charge']/df['Total night minutes']

np.isinf(df).values.sum()
df.replace([np.inf, -np.inf], 0, inplace=True)

### Feature Selection

# Checking the shape of dataset
df.shape

# Dropping Constant and Quasi Constant Feature
def dropping_constant(data):
  from  sklearn.feature_selection import VarianceThreshold
  var_thres= VarianceThreshold(threshold=0.05)
  var_thres.fit(data)
  concol = [column for column in data.columns
          if column not in data.columns[var_thres.get_support()]]
  if "Churn" in concol:
    concol.remove("Churn")
  else:
    pass
  df_removed_var=data.drop(concol,axis=1)
  return df_removed_var

# Calling the function
df_removed_var=dropping_constant(df)

# Checking the shape after feature dropped
df_removed_var.shape

# Getting important column names
dataset_columns_required=dataset.columns.to_list()[1:-1]
dataset_columns_required.extend(['Days_1call_duration','intern_1call_duration','evening_1call_duration','night_1call_duration','international_rate_per_min','day_rate_per_min','eve_rate_per_min','night_rate_per_min'])

# Correlation Heatmap visualization code
corr = df_removed_var.corr()
cmap = cmap=sns.diverging_palette(5, 250, as_cmap=True)

def magnify():
    return [dict(selector="th",
                 props=[("font-size", "7pt")]),
            dict(selector="td",
                 props=[('padding', "0em 0em")]),
            dict(selector="th:hover",
                 props=[("font-size", "12pt")]),
            dict(selector="tr:hover td:hover",
                 props=[('max-width', '200px'),
                        ('font-size', '12pt')])
]

corr.style.background_gradient(cmap, axis=1)\
    .set_properties(**{'max-width': '80px', 'font-size': '10pt'})\
    .set_caption("Hover to magify")\
    .set_precision(2)\
    .set_table_styles(magnify())

# Checking Variable Inflation Factor
# the independent variables set
X = df_removed_var.copy()

# VIF dataframe
vif_data = pd.DataFrame()
vif_data["feature"] = X.columns

# calculating VIF for each feature
vif_data["VIF"] = [variance_inflation_factor(X.values, i)
                          for i in range(len(X.columns))]

for i in range(len(vif_data)):
  vif_data.loc[i,"VIF"]=vif_data.loc[i,"VIF"].round(2)
  if vif_data.loc[i,"VIF"]>=8:
    print(vif_data.loc[i,"feature"])

# Check Feature Correlation and finding multicolinearity
def correlation(df,threshold):
  col_corr=set()
  corr_matrix= df.corr()
  for i in range (len(corr_matrix.columns)):
    for j in range(i):
      if abs (corr_matrix.iloc[i,j])>threshold:
        colname=corr_matrix.columns[i]
        col_corr.add(colname)
  return list(col_corr)

# Getting multicolinear columns and dropping them
highly_correlated_columns=correlation(df_removed_var,0.5)

if "Churn" in highly_correlated_columns:
  highly_correlated_columns.remove("Churn")
else:
  pass

df_removed=df_removed_var.drop(highly_correlated_columns,axis=1)
df_removed.shape

# Correlation after dropping the required columns
# Correlation Heatmap visualization code
corr = df_removed.corr()
cmap = cmap=sns.diverging_palette(5, 250, as_cmap=True)

def magnify():
    return [dict(selector="th",
                 props=[("font-size", "7pt")]),
            dict(selector="td",
                 props=[('padding', "0em 0em")]),
            dict(selector="th:hover",
                 props=[("font-size", "12pt")]),
            dict(selector="tr:hover td:hover",
                 props=[('max-width', '200px'),
                        ('font-size', '12pt')])
]

corr.style.background_gradient(cmap, axis=1)\
    .set_properties(**{'max-width': '80px', 'font-size': '10pt'})\
    .set_caption("Hover to magify")\
    .set_precision(2)\
    .set_table_styles(magnify())

# Manipulate Features to minimize feature correlation and create new features
# Creating call duration column for customers with no international plan
df_removed['Days_1call_duration']=df_removed['Total day minutes']/df_removed['Total day calls']
df_removed['intern_1call_duration']=df_removed['Total intl minutes']/df_removed['Total intl calls']

df_removed['evening_1call_duration']=df_removed['Total eve minutes']/df_removed['Total eve calls']
df_removed['night_1call_duration']=df_removed['Total night minutes']/df_removed['Total night calls']

df_removed.drop(['Total day minutes','Total day calls','Total intl minutes','Total intl calls','Total eve minutes','Total eve calls','Total night minutes','Total night calls'],axis=1,inplace=True)

# Replacing Infinite and null values
np.isinf(df_removed).values.sum()
df_removed.replace([np.inf, -np.inf], 0, inplace=True)

# Checking correlation between new manipulated features
# Correlation Heatmap visualization code
corr = df_removed.corr()
cmap = cmap=sns.diverging_palette(5, 250, as_cmap=True)

def magnify():
    return [dict(selector="th",
                 props=[("font-size", "7pt")]),
            dict(selector="td",
                 props=[('padding', "0em 0em")]),
            dict(selector="th:hover",
                 props=[("font-size", "12pt")]),
            dict(selector="tr:hover td:hover",
                 props=[('max-width', '200px'),
                        ('font-size', '12pt')])
]

corr.style.background_gradient(cmap, axis=1)\
    .set_properties(**{'max-width': '80px', 'font-size': '10pt'})\
    .set_caption("Hover to magify")\
    .set_precision(2)\
    .set_table_styles(magnify())

# Again checking VIF post-dropped features
# the independent variables set
X = df_removed.copy()

# VIF dataframe
vif_data = pd.DataFrame()
vif_data["feature"] = X.columns

# calculating VIF for each feature
vif_data["VIF"] = [variance_inflation_factor(X.values, i)
                          for i in range(len(X.columns))]

for i in range(len(vif_data)):
  vif_data.loc[i,"VIF"]=vif_data.loc[i,"VIF"].round(2)
  if vif_data.loc[i,"VIF"]>=8:
    print(vif_data.loc[i,"feature"])

# After Feature Selection checking the shape left with
df_removed.shape

df_removed.columns

# Embedded Method of validating the feature importances of selected features
def randomforest_embedded(x,y):
  # Create the random forest eith hyperparameters
  model= RandomForestClassifier(n_estimators=550)
  # Fit the mmodel
  model.fit(x,y)
  # get the importance of thr resulting features
  importances= model.feature_importances_
  # Create a data frame for visualization
  final_df= pd.DataFrame({"Features": pd.DataFrame(x).columns, "Importances": importances})
  final_df.set_index('Importances')
  # Sort in ascending order to better visualization
  final_df= final_df.sort_values('Importances')
  # Plot the feature importances in bars
  # final_df.plot.bar(color='teal')
  return final_df

# Getting feature importance of selected features
randomforest_embedded(x=df_removed.drop(["Churn"],axis=1),y=df["Churn"])

"""### Data Transformation"""

# Getting symmetric and skew symmetric features from the cplumns
symmetric_feature=[]
non_symmetric_feature=[]
for i in df_removed.describe().columns:
  if abs(df_removed[i].mean()-df_removed[i].median())<0.1:
    symmetric_feature.append(i)
  else:
    non_symmetric_feature.append(i)

# Getting Symmetric Distributed Features
print("Symmetric Distributed Features : -",symmetric_feature)
# Removing Customer Service Calls column from the list as it's an important factor
# which can't be treated as outliers here will is already leading to higher churn as we have seen furing analysis.
non_symmetric_feature.remove('Churn')
non_symmetric_feature.remove('Customer service calls')
non_symmetric_feature.remove('Voice mail plan')
# Getting Skew Symmetric Distributed Features
print("Skew Symmetric Distributed Features : -",non_symmetric_feature)

# Transform Your data
# Exponential Transforming the required column
df_removed['intern_1call_duration']=(df_removed['intern_1call_duration'])**0.25
df_removed['evening_1call_duration']=(df_removed['evening_1call_duration'])**0.25

# Visualizing code of hist plot for each columns to know the data distibution
for col in df_removed.loc[:,non_symmetric_feature]:
  fig=plt.figure(figsize=(9,6))
  ax=fig.gca()
  feature= (df_removed[col])
  sns.distplot(df_removed[col])
  ax.axvline(feature.mean(),color='magenta', linestyle='dashed', linewidth=2)
  ax.axvline(feature.median(),color='cyan', linestyle='dashed', linewidth=2)
  ax.set_title(col)
plt.show()

# Scaling your data
# Checking the data
df_removed.head()

# Visualizing code of hist plot for each columns to know the data distibution

fig=plt.figure(figsize=(9,6))
ax=fig.gca()
feature= (df_removed["Account length"])
sns.distplot(df_removed["Account length"])
ax.axvline(feature.mean(),color='magenta', linestyle='dashed', linewidth=2)
ax.axvline(feature.median(),color='cyan', linestyle='dashed', linewidth=2)
ax.set_title("Account length")
plt.show()

# Standardizing the required column
df_removed["Account length"] = StandardScaler().fit_transform(df_removed["Account length"].values.reshape(-1, 1))

# Checking the dataset
df_removed.head()

# Split your data to train and test. Choose Splitting ratio wisely.
# Split your data to train and test. Choose Splitting ratio wisely.
 # split into 70:30 ratio
X_train, X_test, y_train, y_test = train_test_split(df_removed.drop("Churn",axis=1),df_removed["Churn"], test_size = 0.3, random_state = 0)

# describes info about train and test set
print("Number transactions X_train dataset: ", X_train.shape)
print("Number transactions y_train dataset: ", y_train.shape)
print("Number transactions X_test dataset: ", X_test.shape)
print("Number transactions y_test dataset: ", y_test.shape)

# Chart - 1 visualization code
# Dependant Column Value Counts
print(dataset.Churn.value_counts())
print(" ")
# Dependant Variable Column Visualization
dataset['Churn'].value_counts().plot(kind='pie',
                              figsize=(15,6),
                               autopct="%1.1f%%",
                               startangle=90,
                               shadow=True,
                               labels=['Not Churn(%)','Churn(%)'],
                               colors=['skyblue','red'],
                               explode=[0,0]
                              )

# Handling Imbalanced Dataset (If needed)
# Handaling imbalance dataset using SMOTE
# sm = SMOTE(random_state=42)
# X_train, y_train = sm.fit_resample(X_train, y_train)

# describes info about train and test set
print("Number transactions X_train dataset: ", X_train.shape)
print("Number transactions y_train dataset: ", y_train.shape)
print("Number transactions X_test dataset: ", X_test.shape)
print("Number transactions y_test dataset: ", y_test.shape)

"""## ***ML Model Implementation***

### ML Model - 1 - **Implementing Logistic Regression**
"""

# ML Model - 1 Implementation
clf = LogisticRegression(fit_intercept=True, max_iter=10000)
# Fit the Algorithm
clf.fit(X_train, y_train)

# Checking the coefficients
clf.coef_

# Checking the intercept value
clf.intercept_

# Predict on the model
# Get the predicted probabilities
train_preds = clf.predict_proba(X_train)
test_preds = clf.predict_proba(X_test)

# Get the predicted classes
train_class_preds = clf.predict(X_train)
test_class_preds = clf.predict(X_test)

# Get the accuracy scores
train_accuracy = accuracy_score(train_class_preds,y_train)
test_accuracy = accuracy_score(test_class_preds,y_test)

print("The accuracy on train data is ", train_accuracy)
print("The accuracy on test data is ", test_accuracy)

# Visualizing evaluation Metric Score chart
# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_train, train_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_test, test_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax); #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

print(metrics.classification_report(train_class_preds, y_train))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_train, train_class_preds))

print(metrics.classification_report(test_class_preds, y_test))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_test, test_class_preds))

# ML Model - 1 Implementation with hyperparameter optimization techniques (i.e., GridSearch CV, RandomSearch CV, Bayesian Optimization etc.)
model = LogisticRegression(max_iter=10000)
solvers = ['lbfgs']
penalty = ['10','l2','14','16','20','18']
c_values = [1000,100, 10, 1.0, 0.1, 0.01,0.001]
# define grid search
grid = dict(solver=solvers,penalty=penalty,C=c_values)
cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=-1, cv=cv, scoring='f1',error_score=0)

# Fit the Algorithm
grid_result=grid_search.fit(X_train, y_train)

print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))


# Predict on the model
# Get the predicted classes
train_class_preds = grid_result.predict(X_train)
test_class_preds = grid_result.predict(X_test)

print(metrics.classification_report(train_class_preds, y_train))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_train, train_class_preds))

print(metrics.classification_report(test_class_preds, y_test))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_test, test_class_preds))

"""### ML Model - 2 - **Implementing Random Forest Classifier**"""

# ML Model - 2 Implementation
# Create an instance of the RandomForestClassifier
rf_model = RandomForestClassifier()

# Fit the Algorithm
rf_model.fit(X_train,y_train)

# Predict on the model
# Making predictions on train and test data
train_class_preds = rf_model.predict(X_train)
test_class_preds = rf_model.predict(X_test)

# Calculating accuracy on train and test
train_accuracy = accuracy_score(y_train,train_class_preds)
test_accuracy = accuracy_score(y_test,test_class_preds)

print("The accuracy on train dataset is", train_accuracy)
print("The accuracy on test dataset is", test_accuracy)

# Visualizing evaluation Metric Score chart# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_train, train_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_test, test_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

print(metrics.classification_report(train_class_preds, y_train))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_train, train_class_preds))

print(metrics.classification_report(test_class_preds, y_test))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_test, test_class_preds))

importances = rf_model.feature_importances_

importance_dict = {'Feature' : list(X_train.columns),
                   'Feature Importance' : importances}

importance_df = pd.DataFrame(importance_dict)
importance_df['Feature Importance'] = round(importance_df['Feature Importance'],2)

importance_df.sort_values(by=['Feature Importance'],ascending=False)

features = X_train.columns
importances = rf_model.feature_importances_
indices = np.argsort(importances)

plt.title('Feature Importance')
plt.barh(range(len(indices)), importances[indices], color='red', align='center')
plt.yticks(range(len(indices)), [features[i] for i in indices])
plt.xlabel('Relative Importance')

plt.show()

# ML Model - 2 Implementation with hyperparameter optimization techniques (i.e., GridSearch CV, RandomSearch CV, Bayesian Optimization etc.)
# Number of trees
n_estimators = [50,80,100]

# Maximum depth of trees
max_depth = [4,6,8]

# Minimum number of samples required to split a node
min_samples_split = [50,100,150]

# Minimum number of samples required at each leaf node
min_samples_leaf = [40,50]

# HYperparameter Grid
param_dict = {'n_estimators' : n_estimators,
              'max_depth' : max_depth,
              'min_samples_split' : min_samples_split,
              'min_samples_leaf' : min_samples_leaf}

# Create an instance of the RandomForestClassifier
rf_model = RandomForestClassifier()

# Grid search
rf_grid = GridSearchCV(estimator=rf_model,
                       param_grid = param_dict,
                       cv = 5, verbose=2, scoring='f1')


# Fit the Algorithm
rf_grid.fit(X_train,y_train)


# Predict on the model
# Making predictions on train and test data
train_class_preds = rf_grid.predict(X_train)
test_class_preds = rf_grid.predict(X_test)

print("Best: %f using %s" % (rf_grid.best_score_, rf_grid.best_params_))

# Visualizing evaluation Metric Score chart# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_train, train_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_test, test_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

print(metrics.classification_report(train_class_preds, y_train))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_train, train_class_preds))

# Hypertuned Random Forest
print(metrics.classification_report(test_class_preds, y_test))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_test, test_class_preds))

"""### ML Model - 3 - **Implementing XgBoost Classifier**"""

# ML Model - 3 Implementation
# Create an instance of the RandomForestClassifier
xg_model = XGBClassifier()

# Fit the Algorithm
xg_models=xg_model.fit(X_train,y_train)

# Predict on the model
# Making predictions on train and test data

train_class_preds = xg_models.predict(X_train)
test_class_preds = xg_models.predict(X_test)

# Visualizing evaluation Metric Score chart
# Visualizing evaluation Metric Score chart# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_train, train_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_test, test_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

print(metrics.classification_report(train_class_preds, y_train))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_train, train_class_preds))

print(metrics.classification_report(test_class_preds, y_test))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_test, test_class_preds))

importances = xg_model.feature_importances_

importance_dict = {'Feature' : list(X_train.columns),
                   'Feature Importance' : importances}

importance_df = pd.DataFrame(importance_dict)
importance_df['Feature Importance'] = round(importance_df['Feature Importance'],2)

importance_df.sort_values(by=['Feature Importance'],ascending=False)

features = X_train.columns
importances = xg_model.feature_importances_
indices = np.argsort(importances)

plt.title('Feature Importance')
plt.barh(range(len(indices)), importances[indices], color='red', align='center')
plt.yticks(range(len(indices)), [features[i] for i in indices])
plt.xlabel('Relative Importance')

plt.show()

# ML Model - 3 Implementation with hyperparameter optimization techniques (i.e., GridSearch CV, RandomSearch CV, Bayesian Optimization etc.)
# Number of trees
n_estimators = [50,80,100]

# Maximum depth of trees
max_depth = [4,6,8]

# Minimum number of samples required to split a node
min_samples_split = [50,100,150]

# Minimum number of samples required at each leaf node
min_samples_leaf = [40,50]

# HYperparameter Grid
param_dict = {'n_estimators' : n_estimators,
              'max_depth' : max_depth,
              'min_samples_split' : min_samples_split,
              'min_samples_leaf' : min_samples_leaf}

# Create an instance of the RandomForestClassifier
xg_model = XGBClassifier()

# Fit the Algorithm
# Grid search
xg_grid = GridSearchCV(estimator=xg_model,
                       param_grid = param_dict,
                       cv = 5, verbose=2, scoring='roc_auc')

xg_grid1=xg_grid.fit(X_train,y_train)
# Predict on the model
# Making predictions on train and test data

train_class_preds = xg_grid1.predict(X_train)
test_class_preds = xg_grid1.predict(X_test)

print("Best: %f using %s" % (xg_grid.best_score_, xg_grid.best_params_))

# Visualizing evaluation Metric Score chart
# Visualizing evaluation Metric Score chart# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_train, train_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

# Get the confusion matrix for both train and test

labels = ['Retained', 'Churned']
cm = confusion_matrix(y_test, test_class_preds)
print(cm)

ax= plt.subplot()
sns.heatmap(cm, annot=True, ax = ax) #annot=True to annotate cells

# labels, title and ticks
ax.set_xlabel('Predicted labels')
ax.set_ylabel('True labels')
ax.set_title('Confusion Matrix')
ax.xaxis.set_ticklabels(labels)
ax.yaxis.set_ticklabels(labels)

print(metrics.classification_report(train_class_preds, y_train))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_train, train_class_preds))

print(metrics.classification_report(test_class_preds, y_test))
print(" ")

print("roc_auc_score")
print(metrics.roc_auc_score(y_test, test_class_preds))

#Get shap values
explainer = shap.Explainer(xg_models)
shap_values = explainer(X_test)

# Waterfall plot for first observation
shap.plots.waterfall(shap_values[0])

# Initialize JavaScript visualizations in notebook environment
shap.initjs()
# Forceplot for first observation
shap.plots.force(shap_values[0])

# Get expected value and shap values array
expected_value = explainer.expected_value
shap_array = explainer.shap_values(X_test)

#Descion plot for first 10 observations
shap.decision_plot(expected_value, shap_array[0:10],feature_names=list(X_test.columns))

#Mean SHAP
shap.plots.bar(shap_values)

# Beeswarm plot
shap.plots.beeswarm(shap_values)
