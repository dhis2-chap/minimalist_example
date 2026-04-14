# Minimalist example of model integration with CHAP

> ## ⚠️ Deprecated
>
> This repository is deprecated. Please use one of these maintained examples instead:
>
> - [Minimalist example (Python + uv)](https://github.com/dhis2-chap/minimalist_example_uv)
> - [Minimalist example (R + renv)](https://github.com/dhis2-chap/minimalist_example_renv)
> - [Minimalist example (R)](https://github.com/dhis2-chap/minimalist_example_r)

This document demonstrates a minimalist example of how to write a CHAP-compatible forecasting model. The example is written in Python, uses few variables without any lag and a standard machine learning model. It simply learns a linear regression from rain and temperature to disease cases in the same month, without considering any previous disease or climate data. It also assumes and works only with a single region. The model is not meant to accurately capture any interesting relations - the purpose is just to show how CHAP integration works in a simplest possible setting. This repository is now deprecated; please use the maintained examples linked above.

## Setting Up the Environment

Before running this example, you need to have Python installed on your system.

We recommend that you create a virtual environment to isolate the dependencies for this project. You can do this using the built-in `venv` module in Python (explained beneath) or by using the tool `uv`. If you are new to virtual environments, you can check out our [guide on virtual environments](https://chap.dhis2.org/tech-intro/virtual-environments/).

If you are on Windows, we assume you are using WSL ([see our terminal setup guide here](https://chap.dhis2.org/tech-intro/terminal/)).

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

```bash
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the model without CHAP integration

Before getting a new model to work as part of CHAP, it can be useful to develop and debug it while running it directly a small dataset from file.

The example can be run in isolation (e.g. from the command line) using the file isolated_run.py:

```
python isolated_run.py
```

This file only contains two code lines:

- A call to a function "train", which trains a model from an input file "trainData.csv" and stores the trained model in a file "model.bin":

```python
train("input/trainData.csv", "output/model.bin")
```

- A call to a function "predict" uses the stored model to forecast future disease cases (to a file "predictions.csv") based on input data on future climate predictions (from a file futureClimateData.csv):

```python
predict("output/model.bin", "input/trainData.csv", "input/futureClimateData.csv", "output/predictions.csv")
```

### Training data

The example uses a minimalist input data containing rainfall, temperature and disease cases for a single region and two time points ("traindata.csv"):

```csv
time_period,rainfall,mean_temperature,disease_cases,location
2023-05,10,30,200,loc1
2023-06,2,30,100,loc1
```

### Training the model

The file "train.py" contains the code to train a model. It reads in training data from a csv file to a Pandas data frame. It learns a linear regression from rainfall and mean_temperature (X) to disease_cases (Y). The trained model is stored to file using the joblib library:

```
def train(csv_fn, model_fn):
    df = pd.read_csv(csv_fn)
    features = ['rainfall', 'mean_temperature']
    X = df[features]
    Y = df['disease_cases']
    Y = Y.fillna(0)  # set NaNs to zero (not a good solution, just a simplest possible solution for the example to work)
    model = LinearRegression()
    model.fit(X, Y)
    joblib.dump(model, model_fn)
    print("Train - model coefficients: ", list(zip(features,model.coef_)))
```

### Future climate data

A minimalist future (predicted) climate data is provided in a file "futureClimateData.csv". This file contains climate data for what is considered to be future periods (weather forecasts). It naturally contains no disease data):

```
time_period,rainfall,mean_temperature,location
2023-07,20,20,loc1
2023-08,30,20,loc1
2023-09,30,30,loc1
```

### Generating forecasts

The file "predict.py" contains the code to forecast disease cases ahead in time based on future climate data (weather forecasts) and a previously trained model read from file. The disease forecasts are stored as a column in a csv file predictions_fn:

```
def predict(model_fn, historic_data_fn, future_climatedata_fn, predictions_fn):
    df = pd.read_csv(future_climatedata_fn)
    X = df[['rainfall', 'mean_temperature']]
    model = joblib.load(model_fn)

    y_pred = model.predict(X)
    df['sample_0'] = y_pred
    df.to_csv(predictions_fn, index=False)
    return y_pred
```

## Running the minimalist model as part of CHAP

To run the minimalist model in CHAP, we first define the model interface in an MLFlow-based yaml specification (in the file "MLproject", which defines :

```yaml
name: min_py_ex

entry_points:
  train:
    parameters:
      train_data: path
      model: str
    command: "python train.py {train_data} {model}"
  predict:
    parameters:
      historic_data: path
      future_data: path
      model: str
      out_file: path
    command: "python predict.py {model} {historic_data} {future_data} {out_file}"
```

After you have installed chap-core ([installation instructions](https://dhis2-chap.github.io/chap-core/chap-cli/chap-core-cli-setup.html)), you can run this minimalist model through CHAP as follows (remember to replace '/path/to/your/model/directory' with your local path, which you can see in the terminal by running `pwd`):

```
chap evaluate --model-name /path/to/your/model/directory --dataset-name ISIMIP_dengue_harmonized --dataset-country brazil --report-filename report.pdf --ignore-environment  --debug
```
