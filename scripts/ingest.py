#!/usr/bin/python3

import getopt
import os
import sys

import requests

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
    year = None
    month = None
    report_name = None
    try:
        opts, _ = getopt.getopt(argv, "ha:s:y:m:r:", ["account=", "source=", "year=", "month=", "report"])
    except getopt.GetoptError:
        print(f"{SCRIPT_NAME} -a < account_id > -s < source_uuid > -y < year > -m < month > -r < report >")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(f"{SCRIPT_NAME} -a <account_id> -s <source_uuid> -y < year > -m < month > -r < report >")
            sys.exit()
        elif opt in ("-a", "--account"):
            account = arg
        elif opt in ("-s", "--source"):
            source_uuid = arg
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-m", "--month"):
            month = arg
        elif opt in ("-r", "--report"):
            report_name = arg

    if not account or not source_uuid or not year or not month or not report_name:
        print("All arguments were not provided. See -h for more help.")
        exit(1)

    datasource_name = f"aws_data_{account}_{source_uuid.replace('-', '_')}"
    payload = {
        "type": "index_parallel",
        "spec": {
            "ioConfig": {
                "type": "index_parallel",
                "inputSource": {
                    "type": "s3",
                    "uris": [
                        f"s3://{bucket}/data/csv/{account}/{source_uuid}/{year}/{month}/{report_name}"
                    ]
                },
                "inputFormat": {
                    "type": "csv",
                    "findColumnsFromHeader": True
                },
                "appendToExisting": False
            },
            "tuningConfig": {
                "type": "index_parallel",
                "partitionsSpec": {
                    "type": "dynamic"
                }
            },
            "dataSchema": {
                "dataSource": datasource_name,
                "granularitySpec": {
                    "type": "uniform",
                    "queryGranularity": "HOUR",
                    "rollup": True,
                    "segmentGranularity": "HOUR"
                },
                "timestampSpec": {
                    "column": "bill/BillingPeriodEndDate",
                    "format": "iso"
                },
                "dimensionsSpec": {
                    "dimensions": [
                        "bill/BillingEntity",
                        "bill/BillingPeriodStartDate",
                        "bill/BillType",
                        "identity/LineItemId",
                        "identity/TimeInterval",
                        "lineItem/AvailabilityZone",
                        "lineItem/CurrencyCode",
                        "lineItem/LineItemDescription",
                        "lineItem/LineItemType",
                        "lineItem/Operation",
                        "lineItem/ProductCode",
                        "lineItem/ResourceId",
                        "lineItem/UsageEndDate",
                        "lineItem/UsageStartDate",
                        "lineItem/UsageType",
                        "pricing/term",
                        "pricing/unit",
                        "product/clockSpeed",
                        "product/currentGeneration",
                        "product/enhancedNetworkingSupported",
                        "product/instanceFamily",
                        "product/instanceType",
                        "product/licenseModel",
                        "product/location",
                        "product/locationType",
                        "product/memory",
                        "product/networkPerformance",
                        "product/operatingSystem",
                        "product/operation",
                        "product/physicalProcessor",
                        "product/preInstalledSw",
                        "product/processorArchitecture",
                        "product/processorFeatures",
                        "product/productFamily",
                        "product/ProductName",
                        "product/region",
                        "product/servicecode",
                        "product/sku",
                        "product/storage",
                        "product/tenancy",
                        "product/usagetype",
                        "resourceTags/user:version"
                    ]
                },
                "metricsSpec": [
                    {
                        "name": "count",
                        "type": "count"
                    },
                    {
                        "name": "sum_bill/PayerAccountId",
                        "type": "longSum",
                        "fieldName": "bill/PayerAccountId"
                    },
                    {
                        "name": "sum_lineItem/UsageAccountId",
                        "type": "longSum",
                        "fieldName": "lineItem/UsageAccountId"
                    },
                    {
                        "name": "sum_lineItem/UsageAmount",
                        "type": "longSum",
                        "fieldName": "lineItem/UsageAmount"
                    },
                    {
                        "name": "sum_product/ecu",
                        "type": "longSum",
                        "fieldName": "product/ecu"
                    },
                    {
                        "name": "sum_product/vcpu",
                        "type": "longSum",
                        "fieldName": "product/vcpu"
                    }
                ]
            }
        }
    }

    r = requests.post(f"{DRUID_URL}/druid/indexer/v1/task", json=payload)
    print(r.status_code)
    print(r.text)

