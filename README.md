[![CircleCI](https://circleci.com/gh/deeplearninc/auger-cli.svg?style=shield&circle-token=4f5b3d5d345f38b5bce6b267251a03c1ed52708b)](https://circleci.com/gh/deeplearninc/auger-cli)

# Auger CLI

A command line tool for the [Auger AI platform](https://auger.ai).

Please create account and organization to start working with CLI.

# Installation

```sh
# Pull latest version
git clone git@github.com:deeplearninc/auger-cli.git

cd auger-cli
pip3 install -e .

# Now `auger` command should be accessible
auger --help
```

# Usage scenarios

## Help

To access the usage information, simply add the `--help` option to any command or sub-command. For example:

```sh
$ auger --help
Usage: auger [OPTIONS] COMMAND [ARGS]...

  Auger command line interface.

Options:
  --help  Show this message and exit.

Commands:
  auth        Authentication with Auger.
  experiments Manage Auger Experiments.
  orgs        Manage Auger Organizations.
  help
  instances   Display available instance types for clusters.
  clusters    Manage Auger Clusters.
  projects    Manage Auger Projects.
  schema      Display current Auger schema.

```

```sh
$ auger auth --help
Usage: auger auth [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  login   Login to Auger.
  logout  Logout from Auger.
  whoami  Display the current logged in user.
```

## Login

The first step you'll need to do is login to Auger with:

```sh
auger auth login
```

Note you can login to a different Auger hub instance by passing the `--url` argument:

```sh
auger auth login --url https://test-instance.auger.ai
```

## Organizations

Organization allocates S3 bucket where all data can be stored between cluster runs.

To start using it you should be a member of any organization, check it with:
```sh
auger orgs
```

To create your own organization go to https://auger.ai:

## Experiments
### Experiment definition
To start working with Auger experiment create folder with experiment name and place file 'auger_experiment.yml' there. This file contain definition of experiment.

For more details see https://docs.auger.ai/docs/experiments/evaluation-options

auger_experiment.yml mandatory fields:
```yml
evaluation_options:
  # Path to file with data. May be URL or path in project files folder 
  data_path: files/iris_data_sample.csv

  # List of features from data file to be used to evaluate ML models
  featureColumns:
  - sepal_length
  - sepal_width
  - petal_length
  - petal_width

  # Target feature to build ML model for
  targetFeature: class

  # If some of your features are strings, add them to the categoricals, so they will be one-hot encoded
  categoricalFeatures:
  - class

  # If you want some categoricals whould be hashed instead of one-hot encoded add them to label encoded list
  labelEncodingFeatures: []

  # List of features of datetime type
  datetimeFeatures: []

  # Define type of ML models. true for 'classification', false for 'regression'
  classification: true

  # If target has two unique values, set it to true 
  binaryClassification: false

  # Score used to optimize ML model.
  # Supported scores for classification: accuracy, f1_macro, f1_micro, f1_weighted, neg_log_loss, precision_macro, precision_micro, precision_weighted, recall_macro, recall_micro, recall_weighted
  # Supported scores for binary classification: accuracy, average_precision, f1, f1_macro, f1_micro, f1_weighted, neg_log_loss, precision, precision_macro, precision_micro, precision_weighted, recall, recall_macro, recall_micro, recall_weighted, roc_auc, cohen_kappa_score, matthews_corrcoef
  # Supported scores for regression: explained_variance, neg_median_absolute_error, neg_mean_absolute_error, neg_mean_squared_error, neg_mean_squared_log_error, r2, neg_rmsle, neg_mase, mda, neg_rmse

  scoring: accuracy

  crossValidationFolds: 5
  max_total_time_mins: 60
  max_eval_time_mins: 1
  max_n_trials: 10
```

auger_experiment.yml optional fields:


## Clusters

Create cluster:
```sh
auger clusters create \
  --organization-id <org id> \
  --worker-count <count> \
  --instance-type <instance-type>
  <cluster name>
```

Supported instances types you can get with `auger instances`

To open cluster system dashboard use:
```sh
auger clusters dashboard <cluster id>
```

To terminate cluster. It will free all paid AWS resources related with this cluster.
```sh
auger clusters delete <cluster id>
```

## Projects

Create project:
```sh
auger project create --project <project name> --organization-id <organization id>
```

The project name must be unique within the organization. This means that a project can be deployed to a cluster, the cluster can be terminated, and the project can be deployed to another one. **NOTE:** If you delete the project, another project with the same name can be used.

Deploy project:
```sh
auger projects create --project <project name> --cluster-id <cluster-id>
```

Deploy uses files from `.auger` folder. From `.auger/service.yml` it takes project definition.
