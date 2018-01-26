# aws_arn
Utilities for constructing an ARN for the given service and resource.

The ARN format is `arn:{partition}:{service}:{region}:{account-id}:{resource-id}`
Some services, and some resources within services, exclude either or both of
region and account. Note that the service is given as the service namespace, 
which is most often the service name in all lowercase, but consult the AWS docs
if you are unsure. This is also the service name used in the SDK (e.g., when
creating a client).

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

A CloudFormation template has access to its region and account. A Python
function `aws_arn.cloudformation` takes the service and resource and returns a
JSON object (that is, a Python dict) that uses intrinsic functions and
pseudoparameters, suitable for use in building templates. The resource can also
consist of multiple parts that will be joined together, allowing references to
other CloudFormation resources in them.