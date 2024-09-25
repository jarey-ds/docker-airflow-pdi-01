# To illustrate how we can trigger a job/transformation in the PDI container via Carte APIs
# Reference: https://help.pentaho.com/Documentation/9.1/Developer_center/REST_API_Reference/Carte

import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator

from datahub_airflow_plugin.entities import Dataset, Urn

now = datetime.datetime.now()

args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "wait_for_downstream": False,
    "catchup": False,
}


with DAG(
    dag_id="mariadb-to-files",
    default_args=args,
    schedule_interval=None,
    catchup=False,
    description=f"Data transformation from mariadb to two file formats example.",
) as dag:

    start = DummyOperator(
        task_id='Start',
    )

    t1 = BashOperator(
        task_id='Trigger_Transformation',
        bash_command='curl "${PDI_CONN_STR}/kettle/executeTrans/?rep=test-repo&trans=/metadata-injection-example/transformations/mariadb_to_file"',
        inlets = [
            Dataset(platform="mariadb", name="nation.public.region_areas"),
            Urn(
                "urn:li:dataset:(urn:li:dataPlatform:mariadb,nation.public.region_areas,PROD)"
            ),
            Urn("urn:li:dataJob:(urn:li:dataFlow:(airflow,mariadb-to-files,prod),t1)"),
        ],
        outlets = [Dataset("csv", f"mariadb_file.csv{now.year}{now.month}{now.day}.csv"),
                   Dataset("avro", "maria_db_table.avro")],
    )

    stop = DummyOperator(
        task_id='Stop',
    )

    start >> [t1] >> stop