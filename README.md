# druid-on-ocp4
Setup for running Apache Druid on OpenShift 4 working with data residing on Amazon S3. Additionally, there is are Docker Compose instructions for alternate development environments.

## Assumptions
This project utilizes Red Hat software and assumes you have access to registry.redhat.io for both the OpenShift 4 and Docker Compose setup.

Deploying Apache Druid on OpenShift 4 assumes you have a working OpenShift 4 cluster.

Both the OpenShift 4 deployment and Docker Compose setup assumes you have access to the S3 object store (AWS).

0. Clone the repos
```
git clone https://github.com/chambridge/druid-on-ocp4.git
git clone https://github.com/apache/druid.git
```

# Docker Compose Deployment

1. Copy the example.env file to .env and update your AWS settings
```
cp example.env .env
```

2. Setup python environment
```
pipenv install
```

3. Start Docker Compose
```
make docker-up
```

4. View the Docker logs
```
make docker-logs
```

5. Ingest data from S3 bucket for data stored as s3://{bucket}/data/csv/{account}/{source_uuid}/{year}/{month}/{report_name}
```
python scripts/ingest.py  -a < account_id > -s < source_uuid > -y < year > -m < month > -r < report >
```

6. Query data from Druid datasource
```
python scripts/query.py  -a < account_id > -s < source_uuid >
```


# OpenShift 4 Deployment

1. Setup pull secret in your project
```
oc project <project>
make setup-pull-secret
```