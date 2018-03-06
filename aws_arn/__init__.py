"""Utilities for constructing an ARN for the given service and resource.

Copyright 2018 iRobot Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import argparse
import sys
import re
import json
import pkg_resources
import collections

import six
import codecs

def _get_version():
    if not pkg_resources.resource_exists(__name__, '_version'):
        return '0.0.0'
    with pkg_resources.resource_stream(__name__, '_version') as fp:
        return codecs.getreader('utf-8')(fp).read().strip()
__version__ = _get_version()

with pkg_resources.resource_stream(__name__, 'config.json') as fp:
    _reader = codecs.getreader('utf-8')
    CONFIG = json.load(_reader(fp))
"""The config file is a JSON object with a single key "services" containing
a list of objects of the form
{
  "service": <service-namespace>,
  "resource": <optional regex for the resource>,
  "region": <bool, assumed true if absent>,
  "account": <bool, assumed true if absent>
}
"""

_arn_tuple = collections.namedtuple('ARN', ['partition', 'service', 'region', 'account', 'resource'])

def split(arn):
    """Return a namedtuple of the parts of the ARNs"""
    return _arn_tuple(*arn.split(':', 5)[1:])

def arn_config(service, resource, force_region=None, force_account=None):
    """Determine whether the ARN for the given service and resource requires
    a region and/or an account specified."""
    arn_has_region = True
    arn_has_account = True
    
    for service_config in CONFIG['services']:
        if service_config['service'] == service:
            if 'resource' in service_config and not re.search(service_config['resource'], resource):
                continue
            arn_has_region = service_config.get('region', True)
            arn_has_account = service_config.get('account', True)
            
            break
    
    if force_region:
        arn_has_region = force_region
    
    if force_account:
        arn_has_account = force_account
    
    return arn_has_region, arn_has_account

def arn(service, resource, region=None, account=None, profile=None, partition=None, force_region=None, force_account=None, on_error=None):
    """Construct an ARN for the given service and resource.
    The ARN format is arn:{partition}:{service}:{region}:{account-id}:{resource-id}
    Some services, and some resources within services, exclude either or both of
    region and account. Given a service, a resource, and the appropriate other data
    this function will format the ARN appropriately, ignoring the region or account
    as necessary.
    Note that the service is given as the service namespace, which is most often
    the service name in all lowercase, but consult the AWS docs if you are unsure.
    This is also the service name used in the SDK.
    Given a profile name, it will use boto3 to determine the region and account
    associated with that profile, if they are required and not already specified.
    """
    
    partition = partition or 'aws'
    
    arn_has_region, arn_has_account = arn_config(service, resource, force_region=force_region, force_account=force_account)
    
    missing = []
    
    session = None
    
    def err(msg):
        if on_error:
            return on_error(msg)
        else:
            raise RuntimeError(msg)
    
    if not arn_has_region:
        region = ''
    elif not region:
        if profile:
            import boto3
            session = session or boto3.Session(profile_name=profile)
            region = session.region_name
        else:
            missing.append('region')
        
    if not arn_has_account:
        account = ''
    elif not account:
        if profile:
            try:
                import boto3
            except:
                err("Error: boto3 is not installed")
            session = session or boto3.Session(profile_name=profile)
            try:
                account = session.client('sts').get_caller_identity()['Account']
            except Exception as e:
                err("Error using profile to get account: {}".format(e))
        else:
            missing.append('account')
    elif account != '*':
        account = '{:0>12}'.format(account)
    else:
        account = ''
        
    if missing:
        err("Error: {} required".format(' and '.join(missing)))
    
    return 'arn:{partition}:{service}:{region}:{account}:{resource}'.format(**{
        'partition': partition,
        'service': service,
        'region': region,
        'account': account,
        'resource': resource,
    })

def cloudformation(service, resource, force_region=None, force_account=None):
    """Output an object to build the ARN, suitable for use in a CloudFormation template.
    Unlike the other functions in this module, the resource can be specified as a list
    of parts, which will be joined without a separator. For example:
    aws_arn.cloudformation('dynamodb', ['table/', {'Ref': 'MyTable'}])
    """
    
    if isinstance(resource, six.string_types):
        resource = [resource]
    
    if isinstance(resource[0], six.string_types):
        resource_for_config = resource[0]
    else:
        resource_for_config = ''
    
    arn_has_region, arn_has_account = arn_config(service, resource_for_config,
                    force_region=force_region, force_account=force_account)
    
    region = {'Ref': 'AWS::Region'} if arn_has_region else ''
    
    parts = [
        'arn:',
        {'Ref': 'AWS::Partition'},
    ]
    
    if arn_has_region and arn_has_account:
        parts.extend([
            ':{}:'.format(service),
            {'Ref': 'AWS::Region'},
            ':',
            {'Ref': 'AWS::AccountId'},
            ':',
        ])
    elif arn_has_region:
        parts.extend([
            ':{}:'.format(service),
            {'Ref': 'AWS::Region'},
            '::',
        ])
    elif arn_has_account:
        parts.extend([
            ':{}::'.format(service),
            {'Ref': 'AWS::AccountId'},
            ':',
        ])
    else:
        parts.append(':{}:::'.format(service))
    
    parts.extend(resource)
    
    return {
        'Fn::Join': [
            '',
            parts
        ]
    }
    

def main():
    parser = argparse.ArgumentParser(description="""Construct an ARN for the given service and resource.
    The ARN format is arn:{partition}:{service}:{region}:{account-id}:{resource-id}
    Some services, and some resources within services, exclude either or both of
    region and account. Given a service, a resource, and the appropriate other data
    this function will format the ARN appropriately, ignoring the region or account
    as necessary.
    Note that the service is given as the service namespace, which is most often
    the service name in all lowercase, but consult the AWS docs if you are unsure.
    This is also the service name used in the SDK.
    Given a profile name, it will use boto3 to determine the region and account
    associated with that profile, if they are required and not already specified.""")
    
    parser.add_argument('service', help='The service namespace')
    parser.add_argument('resource', help='The resource-specific part of the ARN')
    
    region_group = parser.add_argument_group()
    region_group.add_argument('--region', '-r')
    region_group.add_argument('--force-region', choices=['on', 'off'], help="Override the built-in config")
    
    account_group = parser.add_argument_group()
    account_mutex_group = account_group.add_mutually_exclusive_group()
    account_mutex_group.add_argument('--account', '-a')
    account_mutex_group.add_argument('--fake-account', action='store_const', const='123456789012', dest='account', help="Use a fake account number")
    account_group.add_argument('--force-account', choices=['on', 'off'], help="Override the built-in config")
    
    profile_group = parser.add_mutually_exclusive_group()
    profile_group.add_argument('--profile', help="Retrieve region and/or account from AWS profile, if needed")
    profile_group.add_argument('--default-profile', action='store_const', const='default', dest='profile')
    
    parser.add_argument('--partition', default='aws')
    
    args = parser.parse_args()
    
    if args.force_region == 'on':
        force_region = True
    elif args.force_region == 'off':
        force_region = False
    else:
        force_region = None
    
    if args.force_account == 'on':
        force_account = True
    elif args.force_account == 'off':
        force_account = False
    else:
        force_account = None
    
    arn_string = arn(args.service, args.resource,
                     region=args.region, account=args.account,
                     profile=args.profile,
                     partition=args.partition,
                     force_region=force_region, force_account=force_account,
                     on_error=sys.exit)
    
    six.print_(arn_string)

if __name__ == '__main__':
    main()