# dynamodb-add-ttl-lambda
Lambda function to add a ttl attribute to an existing table based on an existing attribute

[![Build Status](https://travis-ci.org/Signiant/dynamodb-add-ttl-lambda.svg?branch=master)](https://travis-ci.org/Signiant/dynamodb-add-ttl-lambda)

# Purpose
This lambda function is designed to be used as a DynamoDB trigger in order to add a ttl attribute to an existing table for new rows.  It will base the new ttl attribute on an existing timestamp attibute by reading the existing attribute and adding a number of days to it.  The existing attribute, number of days and new ttl attribute name are all configurable

# Installing
The easiest deployment of this solution is using AWS SAM
* export your AWS credentials (or use --profile option with sam commands)
* update the samconfig.toml file
  * stack_name - name for the CFN stack
  * s3_bucket - deploy bucket
  * s3_prefix - path in deploy bucket used to store package during deploy
  * region - if other than us-east-1
  * parameter overrides
    * ttlReferenceAttribute - existing attribute used to calculate TTL
    * timeToLive - duration of TTL (in days)
    * ttlAttributeName - what to name the TTL (e.g. ttl)
    * tableName - the DynamoDB table to watch
    * streamARN - the ARN of the DynamoDB stream for the table above
* deploy the lambda using SAM: `./utils/deploy.sh default`

This should deploy the lambda and set up the associated dynamodb trigger for the appropriate table.

NOTE: As per the StartingPosition property on the DynamoDB event trigger - this lambda will only process NEW records.
You may need a separate process to backfill existing records.

You can then monitor the stats for the function and the cloudwatch log to ensure TTLs are being added correctly for new rows.
