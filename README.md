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

To get current login information:

```sh
auger auth whoami
```

To logout:

```sh
auger auth logout
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

  # Number of K-folds: is a cross validation technique for splitting data into train/test
  crossValidationFolds: 5

  # Max Total Time Minutes, the maximum time in minutes an entire training can run for before it is stopped.
  max_total_time_mins: 60

  # Max Trial Time Minutes, this is the maximum time in minutes an individual trial can run before it is stopped.
  max_eval_time_mins: 1

  # Max Trials, this is the maximum number of trials to be run before training stops.
  max_n_trials: 10

  # Build ensembles models after plain models completed. See : https://docs.auger.ai/docs/machine-learning/ensembles 
  use_ensemble: true  
```

auger_experiment.yml optional fields:
```yml
organization: auger
project: evgeny-fast

cluster:
  worker_count : 2

  # Supported instances types you can get with `auger instances`
  instance_type: c5.large
  kubernetes_stack: experimental
  # workers_per_node_count: -1
  # automatic_termination: "1 Hour"

evaluation_options:
  data_extension: ".csv"
  data_compression: gzip

  optimizers_names: []
  splitOptions: {}
  oversampling: {}
  search_space: 
  use_ensemble: true
  preprocessors: {}

```

Run experiment:
```sh
auger experiments run
```

Display leaderboard from last run:
```sh
auger experiments leaderboard
```

To export model locally:
```sh
auger experiments export_model -t <trial id>
```

Trial ID to export model for the last experiment session, if missed best trial used.

Model zip file will be downloaded into models folder. Unzip it and see readme file inside how to use it.

To deploy model to Auger HUB:
```sh
auger experiments deploy_model -t <trial id>
```

Trial ID to export model for the last experiment session, if missed best trial used.

To call predict using deployed model:
```sh
auger experiments predict -p <pipeline id> -t <trial id> -f <csv file path>
```

Pipeline ID is optional, if missed model with trial id will be automatically deployed
Trial ID to export model for the last experiment session, if missed best trial used.
CSV file path should point to local file with data for predcition

Display information about experiment:
```sh
auger experiments show
```

## Clusters

To display cluster information.
```sh
auger clusters show <cluster id>
```

To terminate cluster. It will free all paid AWS resources related with this cluster.
```sh
auger clusters delete <cluster id>
```

## Projects

To display project information.
```sh
auger projects show -p <project name>
```

To open project in web browser:
```sh
auger projects open_project -p <project name>
```

To download file from project cluster:
```sh
auger projects download_file <remote path> -l <local path> -p <project name>
```

Remote path may be full path or relative path on cluster. For examble: files/iris_data_sample.csv

Local path is optional, by default file will be downloaded to 'files' folder in current directory

Project name is optional, if missed project name will be retrieve from auger_experiment.yml

To read project log:
```sh
auger project logs <project_id>
```

To Create project:
```sh
auger project create --project <project name> --organization-id <organization id>
```

The project name must be unique within the organization. This means that a project can be deployed to a cluster, the cluster can be terminated, and the project can be deployed to another one. **NOTE:** If you delete the project, another project with the same name can be used.

To delete project:
```sh
auger projects delete -p <project name>
```
