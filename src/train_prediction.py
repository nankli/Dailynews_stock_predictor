'''Train the SVM model using Sagemaker'''

from __future__ import print_function
import argparse
import os
import pandas as pd
import numpy as np
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from sklearn import svm



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Sagemaker specific arguments. Defaults are set in the environment variables.
    #Saves Checkpoints and graphs
    parser.add_argument('--output-data-dir', type=str, default=os.environ['SM_OUTPUT_DATA_DIR'])

    #Save model artifacts
    parser.add_argument('--model-dir', type=str, default=os.environ['SM_MODEL_DIR'])

    #Train data
    parser.add_argument('--train', type=str, default=os.environ['SM_CHANNEL_TRAIN'])
    args = parser.parse_args()

    file1 = os.path.join(args.train, "merge_stock_news_amazon.csv")
    file2 = os.path.join(args.train, "merge_stock_news_tesla.csv")
    data1 = pd.read_csv(file1, engine="python")
    data2 = pd.read_csv(file2, engine="python")
    data1.loc[:,'ticker'] = 'amazon'
    data2.loc[:,'ticker'] = 'tesla'
    data = data1.append(data2)
    #change the type of Date to Datetime
    data['Date'] = pd.to_datetime(data.Date)
    data = data.sort_values('Date')

    #select features
    cols = ['Date','ticker','Weekday','Price_change','Positive', \
            'Negative', 'Neutral','Yesterday_pos','Yesterday_neg','Yesterday_neu']
    df = data[cols]
    df = df.dropna()

    # one-hot encoding 
    one_hot_encoding_columns = ['ticker','Weekday']
    df_transformed = pd.get_dummies(df, columns = one_hot_encoding_columns)

    # Input features and labels
    X = np.array(df_transformed[['Positive', 'Negative', 'Neutral','ticker_amazon', 'ticker_tesla',\
                                'Yesterday_pos','Yesterday_neg','Yesterday_neu','Weekday_Thursday',\
                                'Weekday_Wednesday','Weekday_Friday','Weekday_Tuesday']])
    y = np.array(df_transformed['Price_change'])

    # train-test splitting, the data has a time dimension
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, shuffle=False)


    model = svm.SVC(kernel='rbf', C=50, gamma='scale')
    model.fit(X_train, y_train)

    # Print the coefficients of the trained classifier, and save the coefficients
    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))


def model_fn(model_dir):
    '''Deserialized and return fitted model
    Note that this should have the same name as the serialized model in the main method
    '''
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model
