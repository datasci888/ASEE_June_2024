# -*- coding: utf-8 -*-
"""LLM integration with ClarifAI.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19eD5SyEMQWJs_yOXiajKe9UJBHVJlyQV
"""

# !pip install openai
# !pip install config
# !pip install pinecone-client[grpc]
# !pip install sentence-transformers PyMuPDF
# !pip install clarifai==9.10.4
# !pip install langchain

!pip install langchain torch pinecone-client pyPdfium2 tqdm

from openai import OpenAI
import pandas as pd
import openai
from config import Config
import json

openai.api_key = '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'

df = pd.read_csv("hrv_metrics.csv")

df_string = df.to_string(index=False)

client = OpenAI(api_key=openai.api_key)

assistant = client.beta.assistants.create(
    name="Psychologist Assistant",
    instructions="You are a psychological counselor. Analyze heart metrics and provide guidance.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-turbo-preview"
)

def show_json(obj):
    print(json.dumps(json.loads(obj.model_dump_json()), indent=4))
show_json(assistant)

thread = client.beta.threads.create()

def submit_message(assistant_id, thread_id, user_message):
    # Adding a new user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_message
    )
    # Initiating the Assistant on the thread
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

import time

def wait_on_run(run_id, thread_id):
    run_status = "queued"  # Initial status
    while run_status in ["queued", "in_progress"]:
        # Retrieve the current status of the run
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )
        run_status = run.status
        time.sleep(0.5)  # Sleep to avoid excessive polling
    return run

def get_response(thread_id):
    # Fetching messages from the thread in ascending order
    messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
    return messages

hrv_analysis_prompt = """
Given the user's heart rate variability (HRV) metrics showing signs of stress and potential sleep irregularities, provide a detailed analysis and suggest practices to improve their mental and physical health. Consider the following categories and practices:

- Mindfulness: Guided meditation, Breathwork exercises, pranayama
- Physical Activity: Regular exercise, Yoga, dance, hiking
- Sleep Hygiene: Consistent sleep schedule, Relaxing bedtime routine
- Relaxation Techniques: Progressive muscle relaxation, Deep breathing exercises
- Social Connection: Spending time with loved ones
- Time Management: Creating a schedule and setting realistic goals
- Healthy Diet: Limiting processed foods and sugary drinks

Incorporate breathing practices, yoga, and other relevant activities to offer a holistic approach to well-being.
"""

# Combine the HRV metrics DataFrame string with the analysis prompt
combined_message = f"{hrv_analysis_prompt}\n\nHRV Metrics:\n{df_string}"

# Submit the combined message to initiate the analysis
run = submit_message(assistant_id=assistant.id, thread_id=thread.id, user_message=combined_message)

# Wait for the Assistant to complete its analysis
completed_run = wait_on_run(run_id=run.id, thread_id=thread.id)

# Fetch the response messages from the thread
messages = get_response(thread_id=thread.id)

def display_messages_and_build_string(messages):
    combined_message = ""
    for message in messages.data:
        # Same logic as before for prefix and message text
        prefix = "User:" if message.role == 'user' else "Assistant:"
        message_text = message.content[0].text.value
        message_text = message_text.replace("**", "").replace("### ", "").replace("\n-", "\n• ")

        # Print the message
        print(f"{prefix}\n{message_text}\n\n---\n")

        # Append the formatted message to the combined string
        combined_message += f"{prefix}\n{message_text}\n\n---\n"

    return combined_message

combined_message = display_messages_and_build_string(messages)

text_content = combined_message.strip()

# Save the text content to a txt file
with open("LLM Recommendation Message.txt", "w") as f:
    f.write(combined_message)

print("Message successfully saved to message.txt")

def get_embedding(text, model="text-embedding-ada-002"):
    # Replace newlines with spaces to ensure smooth processing
    text = text.replace("\n", " ")
    # Fetch the embedding for the provided text
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    # Extract and return the embedding vector
    return response['data'][0]['embedding']

import os

folder_path = '/content/drive/My Drive/pdfs'
pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
print(pdf_files)

import fitz

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    return " ".join(texts)

pdf_path = os.path.join(folder_path, pdf_files[0])
pdf_text = extract_text_from_pdf(pdf_path)

import os
import fitz
from sentence_transformers import SentenceTransformer

# Read a PDF and return its text content
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
        text += "\n\n"
    return text

# Initialize SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.auto_cache = False

folder_path = '/content/drive/My Drive/pdfs'
pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

# Extract texts from PDFs
texts = [extract_text_from_pdf(os.path.join(folder_path, f)) for f in pdf_files]

# Generate embeddings for the extracted texts
embeddings = model.encode(texts)

import os
import fitz
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Function to read a PDF and return its text content
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
        text += "\n\n"
    return text

# Initialize SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.auto_cache = False

folder_path = '/content/drive/My Drive/pdfs'
pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

# Extract texts from PDFs
texts = [extract_text_from_pdf(os.path.join(folder_path, f)) for f in pdf_files]

# Generate embeddings for the extracted texts
embeddings = model.encode(texts)

# LangChain code to split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=20, length_function=len, is_separator_regex=False)

# Define a Document class for storing chunks with metadata
class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

# Function to split texts into chunks and create Document objects
def split_texts_into_documents(texts, metadata_list):
    documents = []
    for text, metadata in zip(texts, metadata_list):
        split_chunks = text_splitter.split_text(text)
        for chunk in split_chunks:
            documents.append(Document(page_content=chunk, metadata=metadata))
    return documents

# Create metadata for each PDF, for this example, it's the filename
metadata_list = [{'source': f} for f in pdf_files]

# Split the extracted texts into Document objects
documents = split_texts_into_documents(texts, metadata_list)

"""Print a sample of Document objects

"""

def print_documents_sample(documents, num_samples=5):
    print(f"Showing {num_samples} samples from the documents list:\n")
    for i, document in enumerate(documents[:num_samples]):
        print(f"Sample {i+1}:")
        print(f"Page Content:\n{document.page_content[:200]}...")  # Print the first 200 characters to keep it concise
        print(f"Metadata: {document.metadata}")
        print("-" * 100)
print_documents_sample(documents)

# Please login and get your API key from  https://clarifai.com/settings/security
from getpass import getpass

CLARIFAI_PAT = getpass()

# Import the required modules
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Clarifai

# Specify the correct user_id/app_id

USER_ID = 'sgopi'
APP_ID = 'llmRAG'

# Commented out IPython magic to ensure Python compatibility.
# Set Personal Access Token as environment variable
# %env CLARIFAI_PAT = CLARIFAI_PAT

import os
os.environ['CLARIFAI_PAT'] = CLARIFAI_PAT

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api.service_pb2_grpc import V2Stub
from clarifai_grpc.grpc.api.status.status_code_pb2 import StatusCode
from clarifai_grpc.grpc.api import service_pb2

channel = ClarifaiChannel.get_grpc_channel()
stub = V2Stub(channel)

# This is how you authenticate.
metadata = (('authorization', f'Key {CLARIFAI_PAT}'),)

"""Create app once"""

# Assuming `texts` is the list of texts extracted from PDFs
concatenated_texts = "\n\n".join(texts)  # Separating PDF texts with two newlines

# Specify the path for the new combined text file
combined_text_file_path = "combined_texts.txt"

# Save the concatenated texts to a file
with open(combined_text_file_path, "w") as text_file:
    text_file.write(concatenated_texts)

print(f"Saved combined texts to {combined_text_file_path}")

loader = TextLoader("combined_texts.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

from langchain_community.vectorstores import Clarifai

# Create a Clarifai vector store from the documents
clarifai_vector_db = Clarifai.from_documents(
    user_id=USER_ID,
    app_id=APP_ID,
    documents=docs,
    pat=CLARIFAI_PAT,
    number_of_docs=53,
)

# Run similarity search using Clarifai

docs10 = clarifai_vector_db.similarity_search("how to manage stress?")

print(docs10)

from langchain.llms import Clarifai
from langchain.chains import RetrievalQA

USER_ID = "openai"
APP_ID = "chat-completion"
MODEL_ID = "GPT-4"

# completion llm
clarifai_llm = Clarifai(
    pat=CLARIFAI_PAT, user_id=USER_ID, app_id=APP_ID, model_id=MODEL_ID)

qa = RetrievalQA.from_chain_type(
    llm=clarifai_llm,
    retriever=clarifai_vector_db.as_retriever(),
    chain_type="stuff"
)

qa.run("How to reduce daily stress?")