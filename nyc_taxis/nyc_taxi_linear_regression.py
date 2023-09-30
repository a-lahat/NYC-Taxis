import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
sns.set()

#We will load it into the pandas DataFrame df.
yellow_tripdata=pd.read_csv('yellow_tripdata_2020-12.csv')
#data clean up


#The 2 columns pickup_datetime and
# dropoff_datetime  converted to datetime format
# which makes analysis of date and time data easier.

yellow_tripdata['pickup_datetime']=pd.to_datetime(yellow_tripdata['tpep_pickup_datetime'])
yellow_tripdata['dropoff_datetime']=pd.to_datetime(yellow_tripdata['tpep_dropoff_datetime'])

yellow_tripdata['trip_duration'] = (yellow_tripdata['dropoff_datetime'] - yellow_tripdata['pickup_datetime']).dt.seconds
print('The value of largest 10 trip duration values are as follows : \n {} '.format(yellow_tripdata['trip_duration'].nlargest(10)))
print('The the number of rows with trip duration less than 30 seconnds  is {}'.format(len(yellow_tripdata[yellow_tripdata['trip_duration']<30 ])))
df=yellow_tripdata[yellow_tripdata.trip_duration!=yellow_tripdata.trip_duration.min()]
#We create another column with the trip_duration represented in hours.
# to later use for calculating trip speed
df['duration_by_hour']=df['trip_duration']/3600
df.passenger_count.value_counts()
# we only want good values
df=df[df.passenger_count!=0]
df=df[df.passenger_count<=6]

#convert into days of the week so a pattern can be detected.

df['pickup_day']=df['pickup_datetime'].dt.day_name()
df['dropoff_day']=df['dropoff_datetime'].dt.day_name()
#distribution of this distance feature by trip_duration
sns.scatterplot(x='trip_distance',y='trip_duration',data=df)
print('The number of rows with distance of 0 is {}'.format(len(df[df.trip_distance==0])))
#  we will replace with the average distance
mean_dist=df['trip_distance'].mean()
df.loc[df['trip_distance']==0,'trip_distance']=mean_dist
#We create a new feature speed.
# This is for identifying data points where time  and distance dont make sense.
# We will  look at the distribution of the trip speed.
df['speed']=df['trip_distance']/df['duration_by_hour']
sns.boxplot(df['speed'])

sns.scatterplot(x='trip_distance',y='duration_by_hour',data=df)

df['log_distance']=np.log(df.trip_distance)
df['log_trip_duration']=np.log(df.duration_by_hour)
sns.scatterplot(x='log_distance',y='log_trip_duration',data=df)
df=df[df.log_trip_duration<2]
# data frame for model
data_for_models=df.loc[:,['passenger_count','store_and_fwd_flag','trip_duration', 'pickup_day', 'dropoff_day','PULocationID',
                'DOLocationID','speed','log_distance','trip_distance']]
# one hot encoding.
data_for_models=pd.get_dummies(data_for_models,columns=['store_and_fwd_flag','pickup_day','dropoff_day','PULocationID','DOLocationID'])
base_line_col=['trip_distance']
predictor_cols=['passenger_count','trip_distance','store_and_fwd_flag_N','store_and_fwd_flag_Y',
               'pickup_day_Friday','pickup_day_Monday','pickup_day_Saturday','pickup_day_Sunday',
               'pickup_day_Thursday','pickup_day_Tuesday','pickup_day_Wednesday','dropoff_day_Friday',
               'dropoff_day_Monday','dropoff_day_Saturday','dropoff_day_Sunday','dropoff_day_Thursday',
               'dropoff_day_Tuesday','dropoff_day_Wednesday']
target_column=['trip_duration']
from sklearn import metrics
from sklearn.model_selection import cross_val_score


def model_fit(est, data_train, data_test, predictors, target):

    # fit model
    est.fit(data_train[predictors], data_train.loc[:, target])
    train_pred = est.predict(data_train[predictors])
    cross_val = cross_val_score(est, data_train[predictors], data_train.loc[:, target], cv=20,
                               scoring='neg_mean_squared_error')

    cross_val = np.sqrt(np.abs(cross_val))
    print(
        "RMSE on Train Data: %.4g" % np.sqrt(metrics.mean_squared_error(data_train.loc[:, target].values, train_pred)))
    print("CV Score : Mean - %.4g | Std - %.4g | Min - %.4g | Max - %.4g" % (
    np.mean(cross_val), np.std(cross_val), np.min(cross_val), np.max(cross_val)))

    test_pred = est.predict(data_test[predictors])
    print("RMSE on Test Data: %.4g" % np.sqrt(metrics.mean_squared_error(data_test.loc[:, target].values, test_pred)))

    return test_pred
from sklearn.linear_model import LinearRegression
validation_size = 0.20
from sklearn.model_selection import train_test_split

seed = 7
X_train, X_test = train_test_split(data_for_models,test_size=validation_size, random_state=seed)
import math as math
#model 1 (base line)
mean_pred=np.repeat(X_train[target_column].mean(),len(X_test[target_column]))
from sklearn.metrics import mean_squared_error as mae
math.sqrt(mae(X_test[target_column],mean_pred))
#model 2
m1 = LinearRegression(normalize=True)
print('The baseline model')
y_pred=model_fit(m1, X_train, X_test,base_line_col,target_column)
coef1 = m1.coef_

# model 3 
m2 = LinearRegression(normalize=True)
y_pred=model_fit(m2, X_train, X_test, predictor_cols,target_column)
coef1 = pd.Series(m2.coef_[0], predictor_cols).sort_values()
#Residual plot
residuals=y_pred-X_test[target_column]
plt.figure(figsize=(10, 6), dpi=120, facecolor='w', edgecolor='b')
l = range(0,len(residuals))
k = [0 for i in range(0,len(residuals))]
plt.scatter( l, residuals, label = 'residuals')
plt.plot( l, k , color = 'red', label = 'regression line' )
plt.title('Residual plot')
plt.xlabel('fitted points ')
plt.ylabel('residuals')

plt.legend()
