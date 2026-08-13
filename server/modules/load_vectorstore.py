import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from pinecone import Pinecone ,ServerlessSpec
from langchain_community.document_loaders import pypdfloader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from