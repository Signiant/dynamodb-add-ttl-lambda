import os
import json
import time
import dateutil.parser
import datetime
import calendar
import boto3


# Return the base value in seconds
# Handles 8601 string, milliseconds or seconds
def get_base_value_epoch_seconds(base_value):
    epoch_seconds = None
    base_value_float = None

    # test for ISO string first
    try:
        parsed = dateutil.parser.parse(base_value)
        print(base_value + " looks to be a time string")
        epoch_seconds = long(parsed.strftime('%s'))
    except Exception as e:
        print(base_value + " is not an ISO8601 string")

    if not epoch_seconds:
        # Could be seconds or milliseconds
        try:
            base_value_float = float(base_value)
        except Exception as e:
            print("ERROR: Unable to convert base_value to a float: " + str(e))

        if base_value_float:
            # https://stackoverflow.com/questions/23929145/how-to-test-if-a-given-time-stamp-is-in-seconds-or-milliseconds
            now = time.mktime(time.gmtime())
            if base_value_float > now:
                print(base_value + " looks to be in milliseconds - converting to seconds")
                epoch_seconds = long(base_value_float / 1000.0)
            else:
                # Could be seconds - see if we can parse it
                try:
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(base_value_float))
                    print(base_value + " looks to be in seconds already")
                    epoch_seconds = long(base_value)
                except Exception as e:
                    print(base_value + " does not look to be seconds " + str(e))

    return epoch_seconds


def get_expiry(base_value, ttl_duration):
    expiry_ttl = None

    future = datetime.datetime.fromtimestamp(float(base_value)) + datetime.timedelta(days=long(ttl_duration))
    expiry_ttl = calendar.timegm(future.timetuple())

    return expiry_ttl


def update_item(table_name, key, ttl_attrib_name, ttl_attrib_value, client):
    status = False
    key_str = json.dumps(key)

    print ("updating item " + key_str + " in table " + table_name)

    response = client.update_item(
        TableName=table_name,
        Key=key,
        ExpressionAttributeNames={
            '#ED': ttl_attrib_name
        },
        ExpressionAttributeValues={
            ':ed': {
                'N': str(ttl_attrib_value),
            }
        },
        ReturnValues='ALL_NEW',
        UpdateExpression='SET #ED = :ed'
    )

    if 'ResponseMetadata' in response:
        if 'HTTPStatusCode' in response['ResponseMetadata']:
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                print "ERROR: error updating key " + key_str
                status = False
            else:
                print "+ Successfully updated " + key_str
                status = True
        else:
            print "ERROR: No http status code in response when trying to update " + key_str
            status = False
    else:
        print "ERROR: No response metadata when trying to update " + key_str
        status = False

    return status


def lambda_handler(event, context):
    status = True
    do_update = False
    table_name = None
    master_attribute_value = None

    # print("Received event: " + json.dumps(event, indent=2))

    if 'master_attribute' in os.environ:
        master_attribute = os.environ['master_attribute']
    else:
        print("FATAL: No master attribute set in the master_attribute environment variable")
        status = False

    if 'time_to_live_days' in os.environ:
        time_to_live_days = os.environ['time_to_live_days']
    else:
        print("FATAL: No TTL duration in days set in the time_to_live_days environment variable")
        status = False

    if 'ttl_attribute_name' in os.environ:
        ttl_attribute_name = os.environ['ttl_attribute_name']
    else:
        print("FATAL: No TTL attribute name in days set in the ttl_attribute_name environment variable")
        status = False

    if status:
        # Batch size MUST be set to 1 in the dynamoDB trigger
        # Makes sense as we are doing an update and there is no batchUpdate operation
        record = event['Records'][0]

        if record['eventName'] == "INSERT":
            table_name = record["eventSourceARN"].split("/")[1]

            print "New INSERT into table " + table_name + " detected - adding TTL if not already present"

            # Do we already have a TTL (very unlikely)?
            if ttl_attribute_name not in record["dynamodb"]["NewImage"]:
                print("no TTL attribute name " + ttl_attribute_name + " found - computing and adding")

                # Does our master TTL attribute exist?
                if master_attribute not in record["dynamodb"]["NewImage"]:
                    print("ERROR: The master attribute " + master_attribute + " to base the TTL on does not exist")
                else:
                    print("Computing a new TTL based on the value in " + master_attribute + " that is " + str(time_to_live_days) + " days in the future")

                    # is attribute a string or a number?
                    if 'S' in record["dynamodb"]["NewImage"][master_attribute]:
                        master_attribute_value = record["dynamodb"]["NewImage"][master_attribute]['S']
                    elif 'N' in record["dynamodb"]["NewImage"][master_attribute]:
                        master_attribute_value = record["dynamodb"]["NewImage"][master_attribute]['N']
                    else:
                        print("ERROR: Unknown attribute type for the master attribute. Unable to continue")
                        status = False

                    if master_attribute_value:
                        print("Found a " + master_attribute + " value of " + master_attribute_value)
                        master_epoch_seconds = get_base_value_epoch_seconds(master_attribute_value)

                        if master_epoch_seconds:
                            ttl_value = get_expiry(master_epoch_seconds, time_to_live_days)
                            print("The TTL value is " + str(ttl_value))

                            table_key = record['dynamodb']['Keys']
                            do_update = True
                        else:
                            print("ERROR: Unable to obtain the original timestamp attribute value to compute a TTL")
                            status = False
            else:
                print "TTL already present - no update required"

    if do_update:
        session = boto3.session.Session(region_name=record['awsRegion'])
        dynamodb_client = session.client('dynamodb')

        if update_item(table_name, table_key, ttl_attribute_name, ttl_value, dynamodb_client):
            status = True
        else:
            status = False

    return status
