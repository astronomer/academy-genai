"""
## Delete a class in Weaviate

CAUTION: This DAG will delete a specified class in your Weaviate instance.
Meant to be used during development to reset Weaviate.
Please use it with caution.
"""

from airflow.providers.weaviate.hooks.weaviate import WeaviateHook
from airflow.decorators import dag, task
import os

# Provider your Weaviate conn_id here.
WEAVIATE_CONN_ID = os.getenv("WEAVIATE_CONN_ID", "weaviate_default")
# Provide the class name to delete the schema.
WEAVIATE_CLASS_TO_DELETE = "MY_SCHEMA_TO_DELETE"


@dag(
    dag_display_name="🧼 Delete a Schema in Weaviate",
    schedule=None,
    start_date=None,
    catchup=False,
    description="CAUTION! Will delete a class in Weaviate!",
    tags=["helper"]
)
def clear_weaviate():

    @task(
        task_display_name=f"Delete {WEAVIATE_CLASS_TO_DELETE} in Weaviate",
    )
    def delete_all_weaviate_schemas(class_to_delete=None):
        WeaviateHook(WEAVIATE_CONN_ID).get_conn().schema.delete_class(class_to_delete)

    delete_all_weaviate_schemas(class_to_delete=WEAVIATE_CLASS_TO_DELETE)


clear_weaviate()
