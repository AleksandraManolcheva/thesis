from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pymongo import MongoClient
import json
from bson import ObjectId
import datetime

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["health_insurance_db"]
collection = db["eligibility_data_"]

# Elasticsearch connection
es = Elasticsearch([{"scheme": "http", "host": "localhost", "port": 9200}])

# Ensure index exists with proper mappings (create if necessary)
index_exists = es.indices.exists(index="health_insurance_data")
if not index_exists:
    es.indices.create(index="health_insurance_data", body={
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "input_parameters": {
                    "properties": {
                        "timestamp": {"type": "date"}
                    }
                },
                # You can add more fields here if needed
            }
        }
    })

# Custom function to serialize MongoDB data (handling ObjectId and datetime)
def serialize_document(doc):
    """Converts ObjectId and datetime to serializable format"""
    doc_id = str(doc['_id'])  # Save for later
    del doc['_id']            # Do not store _id in _source

    # Convert root-level timestamp
    if 'timestamp' in doc and isinstance(doc['timestamp'], datetime.datetime):
        doc['timestamp'] = doc['timestamp'].isoformat()

    # Convert nested timestamp if present
    if 'input_parameters' in doc and 'timestamp' in doc['input_parameters']:
        ts = doc['input_parameters']['timestamp']
        if isinstance(ts, datetime.datetime):
            doc['input_parameters']['timestamp'] = ts.isoformat()

    return doc_id, doc

# Function to prepare data for Elasticsearch
def generate_es_action(doc):
    """Converts document to Elasticsearch action"""
    doc_id, serialized_doc = serialize_document(doc)
    return {
        "_op_type": "index",
        "_index": "health_insurance_data",
        "_id": doc_id,
        "_source": serialized_doc
    }

# Log function moved here to avoid NameError
def log_failed_indexing(errors):
    """Log details for failed indexing documents"""
    for error in errors:
        try:
            print(f"Failed to index document: {json.dumps(error, indent=2)}")
        except Exception as e:
            print(f"Failed to log an error: {e}")

# Fetch data from MongoDB
cursor = collection.find()
actions = [generate_es_action(doc) for doc in cursor]

# Perform bulk index
try:
    success, failed = bulk(es, actions, chunk_size=100, raise_on_error=False, stats_only=False)
    print(f"Successfully indexed {success} documents.")

    # 'failed' is a list of errors, not a count, if raise_on_error=False
    if failed:
        print(f"{len(failed)} document(s) failed to index.")
        log_failed_indexing(failed)

except Exception as e:
    print(f"Error during bulk indexing: {e}")
