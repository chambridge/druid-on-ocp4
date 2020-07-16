#!/usr/bin/python3

import getopt
import os
import sys

from pydruid.db import connect

SCRIPT_NAME = os.path.basename(__file__)

def main(argv):
    DRUID_HOST = os.environ.get("DRUID_HOST", "localhost")
    try:
        DRUID_PORT = int(os.environ.get("DRUID_PORT", "8888"))
    except ValueError:
        DRUID_PORT = 8888
    DRUID_URL = f"http://{DRUID_HOST}:{DRUID_PORT}"

    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        print("You must define S3_BUCKET in your environoment.")
        exit(1)

    account = None
    source_uuid = None
    try:
        opts, _ = getopt.getopt(argv,"ha:s:",["account=","source="])
    except getopt.GetoptError:
        print(f"{SCRIPT_NAME} -a < account_id > -s < source_uuid >")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print (f"{SCRIPT_NAME} -a <account_id> -s <source_uuid>")
            sys.exit()
        elif opt in ("-a", "--account"):
            account = arg
        elif opt in ("-s", "--source"):
            source_uuid = arg

    if not account or not source_uuid:
        print("You must provide both an account and source_uuid. See -h for more help.")
        exit(1)

    datasource_name = f"aws_data_{account}_{source_uuid.replace('-', '_')}"

    conn = connect(host=DRUID_HOST, port=DRUID_PORT,
                path='/druid/v2/sql/', scheme='http')
    curs = conn.cursor()
    curs.execute("""
        SELECT "__time", "bill/BillType", "bill/BillingEntity", "bill/BillingPeriodStartDate", "count", "identity/LineItemId", "identity/TimeInterval", "lineItem/AvailabilityZone", "lineItem/CurrencyCode", "lineItem/LineItemDescription", "lineItem/LineItemType", "lineItem/Operation", "lineItem/ProductCode", "lineItem/ResourceId", "lineItem/UsageEndDate", "lineItem/UsageStartDate", "lineItem/UsageType", "pricing/term", "pricing/unit", "product/ProductName", "product/clockSpeed", "product/currentGeneration", "product/enhancedNetworkingSupported", "product/instanceFamily", "product/instanceType", "product/licenseModel", "product/location", "product/locationType", "product/memory", "product/networkPerformance", "product/operatingSystem", "product/operation", "product/physicalProcessor", "product/preInstalledSw", "product/processorArchitecture", "product/processorFeatures", "product/productFamily", "product/region", "product/servicecode", "product/sku", "product/storage", "product/tenancy", "product/usagetype", "resourceTags/user:version", "sum_bill/PayerAccountId", "sum_lineItem/UsageAccountId", "sum_lineItem/UsageAmount", "sum_product/ecu", "sum_product/vcpu"
        FROM "aws_data_10001_50e9fa68_6dba_43c6_9b91_26eb1ab2e860"
        WHERE "__time" >= CURRENT_TIMESTAMP - INTERVAL '1' DAY
        LIMIT 10
    """)
    for row in curs:
        print(row)


if __name__ == "__main__":
   main(sys.argv[1:])
