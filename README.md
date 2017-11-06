# dynamodb-add-ttl-lambda
Lambda function to add a ttl attribute to an existing table based on an existing attribute

[![Build Status](https://travis-ci.org/Signiant/dynamodb-add-ttl-lambda.svg?branch=master)](https://travis-ci.org/Signiant/dynamodb-add-ttl-lambda)

# Purpose
This lambda function is designed to be used as a DynamoDB trigger in order to add a ttl attribute to an existing table for new rows.  It will base the new ttl attribute on an existing timestamp attibute by reading the existing attribute and adding a number of days to it.  The existing attribute, number of days and new ttl attribute name are all configurable

# Installing
* Grab the zip file from the [releases](https://github.com/Signiant/dynamodb-add-ttl-lambda/releases) section of the repo and upload to an S3 location of your choosing
* Create a new cloudformation stack using the CFN template in the repo
* Provide the S3 location of the function code and the parameters for the function (existing attribute, new ttl in days, etc.)

Once the function and associated IAM policy are created, you can then add it as a trigger to the DynamoDB table you wish to add TTLs to:
* Under the Triggers tab for the DynamoDB table, add a new trigger
* Choose the new function
* Ensure you set a batch size of 1 (IMPORTANT)

You can then monitor the stats for the function and the cloudwatch log to ensure TTLs are being added correctly for new rows.
