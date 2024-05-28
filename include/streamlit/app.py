import streamlit as st
import weaviate
import json
from openai import OpenAI
import os

WEAVIATE_CLASS_NAME = "MYDATA"


def get_embedding(text):
    model = "text-embedding-ada-002"
    client = OpenAI()
    embeddings = client.embeddings.create(input=[text], model=model).data

    return [x.embedding for x in embeddings]


def get_relevant_articles(reworded_prompt, limit=5, certainty=0.75):
    import weaviate.classes as wvc

    client = weaviate.connect_to_local(
        host="weaviate",
        port=8081,
        auth_credentials=weaviate.auth.AuthApiKey("adminkey"),
        headers={"X-OpenAI-Api-key": os.getenv("OPENAI_API_KEY")},
        skip_init_checks=True,
    )

    input_text = reworded_prompt

    try:
        publications = client.collections.get(WEAVIATE_CLASS_NAME)

        response = publications.query.near_text(
            query=input_text,
            distance=certainty,
            return_metadata=wvc.query.MetadataQuery(distance=True),
            limit=limit,
        )

    finally:
        client.close()

    return response.objects


def get_response(articles, query):
    prompt = """You are the helpful social post generator Astra! You will create an interesting factoid post 
    about Apache Airflow and the topic requested by the user:"""

    for article in articles:
        article = article.properties
        article_title = article["folder_path"] if article["folder_path"] else "unknown"

        article_full_text = article["full_text"] if article["full_text"] else "no text"

        article_info = article_title + " Full text: " + article_full_text
        prompt += " " + article_info + " "

    prompt += "Your user asks:"

    prompt += " " + query

    prompt += """ 
    Remember to keep the post short and sweet! At the end of the post add another sentence that is a space fact!"""

    client = OpenAI()

    champion_model_id = "gpt-3.5-turbo"

    chat_completion = client.chat.completions.create(
        model=champion_model_id, messages=[{"role": "user", "content": prompt}]
    )

    return chat_completion


# Streamlit app code
st.title("Create social media posts with Astra!")

st.header("Search")

user_input = st.text_input(
    "Your post idea:",
    "Create a LinkedIn post for me about dynamic task mapping!",
)
limit = st.slider("Retrieve X most relevant chunks:", 1, 20, 5)
certainty = st.slider("Certainty threshold for relevancy", 0.0, 1.0, 0.75)

if "response_text" not in st.session_state:
    st.session_state["response_text"] = ""

if "picture" not in st.session_state:
    st.session_state["picture"] = ""

if "articles" not in st.session_state:
    st.session_state["articles"] = []

if st.button("Generate post!"):
    st.header("Answer")
    with st.spinner(text="Thinking... :thinking_face:"):
        articles = get_relevant_articles(user_input, limit=limit, certainty=certainty)
        response = get_response(articles=articles, query=user_input)

        st.success("Done! :smile:")

        st.write(response.choices[0].message.content)

        st.header("Sources")

        for article in articles:
            st.write(f"URI: {article.properties['uri']}")
            st.write(f"Chunk number: {int(article.properties['chunk_index'])}")
            st.write("---")
