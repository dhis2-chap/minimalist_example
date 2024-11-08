import argparse

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression


def read_pandas_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    return df

def train(csv_fn, model_fn):
    df = pd.read_csv(csv_fn)
    #print all column names (without any being skipped)
    features = ['rainfall', 'mean_temperature']
    X = df[features] #What if we wanted last months disease cases - how to easily get lagged data
    Y = df['disease_cases']
    Y = Y.fillna(0)  # set NaNs to zero (not a good solution, just for the example to work)
    model = LinearRegression()
    model.fit(X, Y)
    joblib.dump(model, model_fn)
    print("Train - model coefficients: ", list(zip(features,model.coef_)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train a minimalist forecasting model.')

    parser.add_argument('csv_fn', type=str, help='Path to the CSV file containing input data.')
    parser.add_argument('model_fn', type=str, help='Path to save the trained model.')
    args = parser.parse_args()
    train(args.csv_fn, args.model_fn)


