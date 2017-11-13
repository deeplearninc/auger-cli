[![CircleCI](https://circleci.com/gh/deeplearninc/auger-cli.svg?style=shield&circle-token=4f5b3d5d345f38b5bce6b267251a03c1ed52708b)](https://circleci.com/gh/deeplearninc/auger-cli)

# Auger CLI

A command line tool for the [Auger AI platform](https://auger.ai).

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
  apps       Manage Auger Apps.
  auth       Authentication with Auger.
  clusters   Manage Auger Clusters.
  instances  Display available instance types for clusters.
  keys       Manage Auger SSH keys.
  orgs       Manage Auger Organizations.
```

```sh
$ auger auth --help
Usage: auger auth [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  login   Login to auger.
  logout  Logout from Auger.
  whoami  Display the current logged in user.
```

## Login

The first step you'll need to do is login to auger with:

```sh
auger auth login
```

Note you can login to a different auger hub instance by passing the `--url` argument:

```sh
auger auth login --url https://test-instance.auger.ai
```


## Organizations

Organization allocates S3 bucket where all data can be stored between cluster runs.

To start using it you should be a member of any organization, check it with:
```sh
auger orgs
```

or create your own organization:
```sh
auger orgs create --access-key="<AWS acess key>" --secret-key="<AWS secret key>" <organization name>
```

AWS key pair should have the following statements:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:ListBucketVersions"
            ],
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AssociateDhcpOptions",
                "ec2:AssociateRouteTable",
                "ec2:AttachInternetGateway",
                "ec2:AttachVolume",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CreateDhcpOptions",
                "ec2:CreateInternetGateway",
                "ec2:CreateKeyPair",
                "ec2:CreateRoute",
                "ec2:CreateSecurityGroup",
                "ec2:CreateSubnet",
                "ec2:CreateTags",
                "ec2:CreateVolume",
                "ec2:CreateVpc",
                "ec2:DeleteInternetGateway",
                "ec2:DeleteKeyPair",
                "ec2:DeleteRoute",
                "ec2:DeleteRouteTable",
                "ec2:DeleteSecurityGroup",
                "ec2:DeleteSubnet",
                "ec2:DeleteVolume",
                "ec2:DeleteVpc",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeInstances",
                "ec2:DescribeRouteTables",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeVolumes",
                "ec2:DescribeVpcs",
                "ec2:DetachInternetGateway",
                "ec2:ModifyVpcAttribute",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:RunInstances",
                "ec2:TerminateInstances"
            ],
            "Condition": {
                "StringEquals": {
                    "ec2:Region": [
                        "us-west-1",
                        "us-west-2"
                    ]
                }
            },
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::auger-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:AttachUserPolicy",
                "iam:CreateAccessKey",
                "iam:CreateUser",
                "iam:DeleteAccessKey",
                "iam:DeleteUser",
                "iam:DeleteUserPolicy",
                "iam:DetachUserPolicy",
                "iam:ListAccessKeys",
                "iam:ListAttachedUserPolicies",
                "iam:ListGroupsForUser",
                "iam:ListUserPolicies",
                "iam:PutUserPolicy",
                "iam:RemoveUserFromGroup"
            ],
            "Resource": [
                "arn:aws:iam:::user/vault-*"
            ]
        }
    ]
}
```

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
auger apps create --app <project name> --organization-id <organization id>
```

The project name must be unique within the organization. This means that a project can be deployed to a cluster, the cluster can be terminated, and the project can be deployed to another one. **NOTE** If you delete the application, another project with the same name can be used.

Deploy project:
```sh
auger apps create --app <project name> --cluster-id <cluster-id>
```

Deploy uses files from `.auger` folder. From `.auger/service.yml` it takes project definition.
