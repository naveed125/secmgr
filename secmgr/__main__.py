#!/usr/bin/env python3

import argparse
import boto3
from botocore.exceptions import ClientError
import re
import json
import sys

#
# Constants
#
SEARCH_PATTERN = r'{{\s*(.*)\s*}}'


#
# Function to get a single key data from secrets manager
#
def get_secret(secret_key):

    data = None
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_key
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"The requested secret {secret_key} was not found", file=sys.stderr)
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print(f"The request was invalid due to:", e, file=sys.stderr)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print(f"The request had invalid params:", e, file=sys.stderr)
    else:
        if 'SecretString' in get_secret_value_response:
            data = get_secret_value_response['SecretString']

    return data


# Init boto3 client
try:
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )
except Exception as ex:
    print("Error during boto3 initialization:", ex)
    exit(1)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-k', '--key', help='fetch a secrets key')
parser.add_argument('-f', '--file', help='parse a template file')
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

# Process arguments
value = None
if args.key:

    key = args.key
    sub_key = None

    if args.key.find(":") > 0:
        (key, sub_key) = args.key.split(":")

    value = get_secret(key)

    if sub_key:
        parsed = json.loads(value)
        if sub_key in parsed:
            value = parsed[sub_key]

    if value:
        print(value)

elif args.file:

    # read the whole file into an array
    line = None
    with open(args.file) as fp:
        lines = fp.readlines()

    # group by keys to minimize fetches
    keys_to_fetch = {}
    for line in lines:
        result = re.search(SEARCH_PATTERN, line)
        if result:
            (key, sub_key) = result.group(1).split(":")
            if key in keys_to_fetch:
                keys_to_fetch[key].append(sub_key)
            else:
                keys_to_fetch[key] = [sub_key]

    # fetch top level key data
    key_data = {}
    for key in keys_to_fetch:
        secrets = json.loads(get_secret(key))
        for secret in secrets:
            key_data[f"{key}:{secret}"] = secrets[secret]

    # finally, fill in the data
    for line in lines:
        result = re.search(SEARCH_PATTERN, line)
        if result:
            line = re.sub(SEARCH_PATTERN, key_data[result.group(1)], line)
        print(line, end="")
