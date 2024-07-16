# Introduction to GenAI with Apache Airflow®

Welcome! :rocket:

This repository contains the code to be used in the Introduction to GenAI with [Apache Airflow®](https://airflow.apache.org/) [Astronomer Academy module](https://academy.astronomer.io/introduction-to-genai-with-apache-airflow).

## Academy Module Contents

In the Introduction to GenAI with Airflow module, you will learn everything you need to create your first retrieval augmented generation (RAG) application with Airflow. 

We will begin by introducing Generative AI (GenAI): what it is and how Airflow helps power GenAI applications. Next, we will cover the module project, a content generation application using a [Streamlit](https://streamlit.io/) frontend that creates custom text based on local data. The application's data will be made available using an Airflow pipeline consisting of one DAG that ingests local files, chunks the text using [LangChain](https://www.langchain.com/), embeds it using [OpenAI](https://openai.com/), and stores it into a [Weaviate](https://weaviate.io/) vector database.

After covering the basics and explaining the Airflow DAG powering the RAG application, you will clone a GitHub repository with a pre-built Airflow environment in which we will build the DAG step-by-step. While building the DAG you will learn about key Airflow features such as the TaskFlow API, advanced DAG parameters, Airflow branching and dynamic task mapping.

Finally, we conclude by adapting the application for your personal use case and explore a real-world application similar RAG DAGs: [AskAstro](https://ask.astronomer.io/); a chat-bot with advanced knowledge about Airflow and Astronomer.

> [!NOTE]
> The fully finished DAG can be found in the `solutions` folder, if you are in a hurry!

## How to use this repository

1. :star: the repository and clone it to your local machine.
2. Create a new file at the root of the project called `.env` and copy the contents from `.env_example` into it.
3. Provide your own OpenAI API key in the `.env` file in the two places with the `<YOUR-OPENAI-API-KEY>` placeholders.
4. Make sure you have the open-source and free [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli) installed on your local machine.
5. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 6 Docker containers on your machine, 4 for different Airflow components and one each for Weaviate and Streamlit:

- Postgres: Airflow's Metadata Database (port: 5432)
- Webserver: The Airflow component responsible for rendering the Airflow UI (port: 8080)
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks
- Weaviate: A local Weaviate instance (port: 8081 and 50051)
- Streamlit: A local Streamlit application (port: 8501)

6. Verify that all 6 Docker containers were created by running 'docker ps'. The streamlit container can take a few minutes to fully start.

> [!NOTE] 
> Running 'astro dev start' will start your project occupying the ports 8080, 8081, 5432, 50051 and 8501. If you already have any of those ports allocated, you can either stop your existing Docker containers or change the port. See the [Astronomer documentation for how to change the Astro project related ports](https://docs.astronomer.io/astro/test-and-troubleshoot-locally#ports-are-not-available) and override the ports for Streamlit and or Weaviate in the `docker-compose.override.yml` file.

7. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.
8. Follow the Academy module to build your RAG DAG.

## Resources

### Airflow and AI/ML resources
- Academy: 
  - [Taskflow API Module](https://academy.astronomer.io/astro-runtime-taskflow)
  - [Airflow: Branching Module](https://academy.astronomer.io/astro-runtime-branching)
  - [Airflow: Dynamic Task Mapping Module](https://academy.astronomer.io/astro-runtime-dynamic-task-mapping)
- Learn Guides & Tutorials:
  - [Best practices for orchestrating MLOps pipelines with Airflow](https://www.astronomer.io/docs/learn/airflow-mlops)
  - [DAG-level parameters](https://www.astronomer.io/docs/learn/airflow-dag-parameters)
  - [Introduction to the TaskFlow API and Airflow decorators](https://www.astronomer.io/docs/learn/airflow-decorators)
  - [Branching in Airflow](https://www.astronomer.io/docs/learn/airflow-branch-operator)
  - [Create dynamic Airflow tasks](https://www.astronomer.io/docs/learn/dynamic-tasks)
  - [Orchestrate Weaviate operations with Apache Airflow](https://www.astronomer.io/docs/learn/airflow-weaviate)
- [Gen AI Cookbook](https://www.astronomer.io/ebooks/gen-ai-airflow-cookbook/)(Reference Architecture Diagrams)
- [Ask Astro](https://github.com/astronomer/ask-astro)
- [Advanced Content Generation Pipeline Repo](https://github.com/astronomer/gen-ai-fine-tune-rag-use-case)

### Documentation for the tools used:

- [Astronomer Airflow Learn Docs](https://www.astronomer.io/docs/learn)
- [Apache Airflow Official Documentation](https://airflow.apache.org/docs/apache-airflow/stable/index.html)
- [Astro CLI to run Airflow locally in Docker](https://www.astronomer.io/docs/astro/cli/overview)
- [Weaviate](https://weaviate.io/developers/weaviate)
- [Airflow Weaviate Provider](https://airflow.apache.org/docs/apache-airflow-providers-weaviate/stable/index.html)
- [Streamlit](https://docs.streamlit.io/)
- [LangChain](https://python.langchain.com/v0.2/docs/introduction/)
- [pandas](https://pandas.pydata.org/docs/)
- [OpenAI](https://platform.openai.com/docs/introduction)
