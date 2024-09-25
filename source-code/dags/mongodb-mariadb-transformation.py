# To illustrate how we can trigger a job/transformation in the PDI container via Carte APIs
# Reference: https://help.pentaho.com/Documentation/9.1/Developer_center/REST_API_Reference/Carte

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator

from datahub_airflow_plugin.entities import Dataset, Urn

args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "wait_for_downstream": False,
    "catchup": False,
}


with DAG(
    dag_id="mongodb-to-mariadb",
    default_args=args,
    schedule_interval=None,
    catchup=False,
    description=f"Data transformation from mongodb to mariadb tables.",
) as dag:

    start = DummyOperator(
        task_id='Start',
    )

    t1 = BashOperator(
        task_id='Trigger_Transformation',
        bash_command='curl "${PDI_CONN_STR}/kettle/executeTrans/?rep=test-repo&trans=/metadata-injection-example/transformations/mongodb_to_mariadb"',
        inlets = [
            Dataset(platform="mongodb", name="cinfodata.city"),
            Urn(
                "urn:li:dataset:(urn:li:dataPlatform:mongodb,cinfodata.city,PROD)"
            ),
            Urn("urn:li:dataJob:(urn:li:dataFlow:(airflow,mongo-to-mariadb,prod),t1)"),
        ],
        outlets = [Dataset("mariadb", "nation.public.modified_cities")],
    )

    stop = DummyOperator(
        task_id='Stop',
    )

    start >> [t1] >> stop