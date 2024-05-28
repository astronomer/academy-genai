"""
## Simple RAG DAG to ingest new knowledge data into a vector database

This DAG ingests text data from markdown files, chunks the text, and then ingests 
the chunks into a Weaviate vector database.
"""

from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator
from airflow.providers.weaviate.hooks.weaviate import WeaviateHook
from airflow.providers.weaviate.operators.weaviate import WeaviateIngestOperator
from pendulum import datetime, duration
import os
import logging
import json
import pandas as pd

t_log = logging.getLogger("airflow.task")

# Variables used in the DAG
_INGESTION_FOLDERS_LOCAL_PATHS = os.getenv("INGESTION_FOLDERS_LOCAL_PATHS")

_WEAVIATE_CONN_ID = os.getenv("WEAVIATE_CONN_ID")
_WEAVIATE_CLASS_NAME = os.getenv("WEAVIATE_CLASS_NAME")
_WEAVIATE_VECTORIZER = os.getenv("WEAVIATE_VECTORIZER")
_WEAVIATE_SCHEMA_PATH = os.getenv("WEAVIATE_SCHEMA_PATH")

_CREATE_CLASS_TASK_ID = "create_class"
_CLASS_ALREADY_EXISTS_TASK_ID = "class_already_exists"


@dag(
    dag_display_name="📚 Ingest Knowledge Base",
    start_date=datetime(2024, 5, 1),
    schedule="@daily",
    catchup=False,
    max_consecutive_failed_dag_runs=5,
    tags=["RAG"],
    default_args={
        # "retries": 3,
        "retry_delay": duration(minutes=5),
        "owner": "AI Task Force",
    },
    doc_md=__doc__,
    description="Ingest knowledge into the vector database for RAG.",
)
def my_first_rag_dag_solution():

    # ---------------------- #
    # Set up Weaviate schema #
    # ---------------------- #

    @task.branch
    def check_class(
        conn_id: str,
        class_name: str,
        create_class_task_id: str,
        class_already_exists_task_id: str,
    ) -> str:
        """
        Check if the target class exists in the Weaviate schema.
        Args:
            conn_id: The connection ID to use.
            class_name: The name of the class to check.
            create_class_task_id: The task ID to execute if the class does not exist.
            class_already_exists_task_id: The task ID to execute if the class already exists.
        Returns:
            str: Task ID of the next task to execute.
        """

        # connect to Weaviate using the Airflow connection `conn_id`
        hook = WeaviateHook(conn_id)
        client = hook.get_client()

        # retrieve the existing schema from the Weaviate instance
        schema = client.schema.get()
        existing_classes = {cls["class"]: cls for cls in schema.get("classes", [])}

        # if the target class does not exist yet, we will need to create it
        if class_name not in existing_classes:
            print(f"Class {class_name} does not exist yet.")
            return create_class_task_id
        # if the target class exists it does not need to be created
        else:
            return class_already_exists_task_id

    check_class_obj = check_class(
        conn_id=_WEAVIATE_CONN_ID,
        class_name=_WEAVIATE_CLASS_NAME,
        create_class_task_id=_CREATE_CLASS_TASK_ID,
        class_already_exists_task_id=_CLASS_ALREADY_EXISTS_TASK_ID,
    )

    @task
    def create_class(
        conn_id: str, class_name: str, vectorizer: str, schema_json_path: str
    ) -> None:
        """
        Create a class in the Weaviate schema.
        Args:
            conn_id: The connection ID to use.
            class_name: The name of the class to create.
            vectorizer: The vectorizer to use for the class.
            schema_json_path: The path to the schema JSON file.
        """
        import json

        weaviate_hook = WeaviateHook(conn_id)

        with open(schema_json_path) as f:
            schema = json.load(f)
            class_obj = next(
                (item for item in schema["classes"] if item["class"] == class_name),
                None,
            )
            class_obj["vectorizer"] = vectorizer

        weaviate_hook.create_class(class_obj)

    create_class_obj = create_class(
        conn_id=_WEAVIATE_CONN_ID,
        class_name=_WEAVIATE_CLASS_NAME,
        vectorizer=_WEAVIATE_VECTORIZER,
        schema_json_path=_WEAVIATE_SCHEMA_PATH,
    )

    schema_already_exists_obj = EmptyOperator(task_id="class_already_exists")  # rename!
    ingest_documents_obj = EmptyOperator(
        task_id="ingest_documents", trigger_rule="none_failed"
    )

    # ----------------------- #
    # Ingest domain knowledge #
    # ----------------------- #

    @task
    def fetch_ingestion_folders_local_paths(ingestion_folders_local_paths) -> list[str]:

        # get all the folders in the given location
        folders = os.listdir(ingestion_folders_local_paths)

        # return the full path of the folders
        return [
            os.path.join(ingestion_folders_local_paths, folder) for folder in folders
        ]

    fetch_ingestion_folders_local_paths_obj = fetch_ingestion_folders_local_paths(
        ingestion_folders_local_paths=_INGESTION_FOLDERS_LOCAL_PATHS
    )

    # dynamically mapped task
    @task(map_index_template="{{ my_custom_map_index }}")
    def extract_document_text(ingestion_folder_local_path: str) -> list[str]:
        """
        Extract information from markdown files in a folder.
        Args:
            folder_path (str): Path to the folder containing markdown files.
        Returns:
            list[dict]: A list of dictionaries containing the extracted information.
        """
        files = [
            f for f in os.listdir(ingestion_folder_local_path) if f.endswith(".md")
        ]

        uris = []
        titles = []
        texts = []

        for file in files:
            file_path = os.path.join(ingestion_folder_local_path, file)

            uris.append(file_path)
            titles.append(file.split(".")[0])
            timestamp = os.path.getmtime(file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                texts.append(f.read())


        document_df = pd.DataFrame(
            {
                "folder_path": ingestion_folder_local_path,
                "uri": uris,
                "title": titles,
                "timestamp": timestamp,
                "full_text": texts,
                "type": "text/markdown",
            }
        )

        document_df["timestamp"] = document_df["timestamp"].astype(str)

        t_log.info(f"Number of records: {document_df.shape[0]}")

        # get the current context and define the custom map index variable
        from airflow.operators.python import get_current_context

        context = get_current_context()
        context["my_custom_map_index"] = (
            f"Extracted files from: {ingestion_folder_local_path}."
        )

        return document_df

    extract_document_text_obj = extract_document_text.expand(
        ingestion_folder_local_path=fetch_ingestion_folders_local_paths_obj
    )

    # dynamically mapped task
    @task(
        map_index_template="{{ my_custom_map_index }}",
    )
    def chunk_text(df: pd.DataFrame) -> pd.DataFrame:
        """
        Chunk the text in the DataFrame.
        Args:
            df (pd.DataFrame): The DataFrame containing the text to chunk.
        Returns:
            pd.DataFrame: The DataFrame with the text chunked.
        """

        from langchain.schema import Document
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter()

        df["chunks"] = df["full_text"].apply(
            lambda x: splitter.split_documents([Document(page_content=x)])
        )

        df = df.explode("chunks", ignore_index=True)
        df.dropna(subset=["chunks"], inplace=True)
        df["full_text"] = df["chunks"].apply(lambda x: x.page_content)

        for document in df["uri"].unique():
            chunks_per_doc = 0
            for i, chunk in enumerate(df.loc[df["uri"] == document, "chunks"]):
                print(f"Document: {document}, Chunk: {i}")
                df.loc[df["chunks"] == chunk, "chunk_index"] = i
                chunks_per_doc += 1
            df["chunks_per_doc"] = chunks_per_doc

        df["chunk_index"] = df["chunk_index"].astype(int)
        df["chunks_per_doc"] = df["chunks_per_doc"].astype(int)
        df.drop(["chunks"], inplace=True, axis=1)
        df.reset_index(inplace=True, drop=True)

        # get the current context and define the custom map index variable
        from airflow.operators.python import get_current_context

        context = get_current_context()

        context["my_custom_map_index"] = (
            f"Chunked files from: {df['folder_path'][0]}."
        )

        return df

    chunk_text_obj = chunk_text.expand(df=extract_document_text_obj)

    # dynamically mapped task
    ingest_data = WeaviateIngestOperator.partial(
        task_id="ingest_data",
        conn_id="weaviate_default",
        class_name=_WEAVIATE_CLASS_NAME,
        map_index_template="Ingested files from: {{ task.input_data.to_dict()['folder_path'][0] }}.",
    ).expand(input_data=chunk_text_obj)

    # ---------------- #
    # Set dependencies #
    # ---------------- #

    chain(
        check_class_obj,
        [create_class_obj, schema_already_exists_obj],
        ingest_documents_obj,
        fetch_ingestion_folders_local_paths_obj,
    )

    chain(
        chunk_text_obj,
        ingest_data,
    )


my_first_rag_dag_solution()
