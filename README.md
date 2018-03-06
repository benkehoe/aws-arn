# aws-arn
## Utilities for constructing an ARN for the given service and resource.

The ARN format is `arn:{partition}:{service}:{region}:{account-id}:{resource-id}`
Some services, and some resources within services, exclude either or both of
region and account. Note that the service is given as the service namespace, 
which is most often the service name in all lowercase, but consult the AWS docs
if you are unsure. This is also the service name used in the SDK (e.g., when
creating a client).

## Main utility

Three utilities are provided: a Python function, a command line tool, and a
second Python function for use with CloudFormation templates.

The Python function `aws_arn.arn` and the command line tool `aws-arn` both
take the service and the resource as strings, with options to specify the
region and account. It is an error to not provide the region or account when
they are required by the ARN format for that service and resource. You can
optionally specify an AWS profile (as used by the CLI and SDK) to pick up the
region and/or account if they are required and have not been given (this
requires the `boto3` library be installed). You can also override the built-in
configuration to show or suppress either region or account if needed.

A CloudFormation template has access to its region and account. The Python
function `aws_arn.cloudformation(service, resource)` takes the service and 
resource and returns a JSON object (that is, a Python dict) that uses intrinsic
functions and pseudoparameters, suitable for use in building templates. The 
resource can also consist of multiple parts (i.e., a list of strings, dicts that 
correspond to intrinsic functions, etc.) that will be joined together, allowing
references to other CloudFormation resources in them.

## ARN helper functions

* `aws_arn.split(arn_string)`: returns a named tuple of the parts of an ARN
* `aws_arn.arn_config(service, resource)`: returns a tuple `(has_region, has_account)` of bools indicating whether the ARN needs a region and an account.

## CLI usage:
    aws-arn SERVICE RESOURCE [--region REGION] [--account ACCOUNT] [--profile PROFILE_NAME] [OTHER_OPTIONS]

* Region options:
    * `--region REGION` or `-r REGION`: Specify the region
    * `--force-region on`: Include the region in the ARN no matter what
    * `--force-region off`: Do not include the region in the ARN no matter what
* Account options:
    * `--account ACCOUNT` or `-a ACCOUNT`: Specify the account
    * `--fake-account`: Use the account 123456789012 (conflicts with `--account`)
    * `--force-account on`: Include the account in the ARN no matter what
    * `--force-account off`: Do not include the account in the ARN no matter what
* Profile options:
    * The profile is only accessed if region or account are needed and not specified
    * Getting the account from the profile requires a call to STS.GetCallerIdentity
    * `--profile PROFILE`: Use the given profile
    * `--default-profile`: Use the default profile (conflicts with `--profile`)
* Partition options:
    * Only needed for advanced use cases (e.g., AWS China)
    * `--partition PARTITION` use the given partition instead of `aws`
