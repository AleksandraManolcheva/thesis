import time
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from datetime import datetime

# === MongoDB setup ===
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["health_insurance_db"]
mongo_collection = mongo_db["eligibility_data_"]

# === Elasticsearch setup ===
es = Elasticsearch("http://localhost:9200")
es_index = "health_insurance_data"

# Get today's date for range query
today = datetime.today().strftime("%Y-%m-%dT00:00:00")

# === Elasticsearch Query ===
es_query = {
  "query": {
    "bool": {
      "must": [
        {
          "fuzzy": {
            "input_parameters.state": {
              "value": "Minnesota",
              "fuzziness": "AUTO"
            }
          }
        }
      ],
      "filter": [
        {
          "range": {
            "timestamp": {
              "gte": today,  # Today's start timestamp
              "lt": f"{today[:10]}T23:59:59"  # End of today's timestamp
            }
          }
        }
      ]
    }
  }
}

# === MongoDB Query ===
mongo_query = {
    "input_parameters.state": {
        "$regex": "minnesota",  # Basic search for documents where state contains 'minnesota'
        "$options": "i"         # Case-insensitive
    },
    "timestamp": {
        "$gte": datetime.strptime(today, "%Y-%m-%dT%H:%M:%S"),  # Start of today
        "$lt": datetime.strptime(f"{today[:10]}T23:59:59", "%Y-%m-%dT%H:%M:%S")  # End of today
    }
}

# === Elasticsearch: SEARCH (instead of COUNT) ===
start_time_es_search = time.time()
es_result_search = es.search(index=es_index, body=es_query)  # Execute Elasticsearch query
end_time_es_search = time.time()
es_duration_search = end_time_es_search - start_time_es_search

# === MongoDB: COUNT ===
start_time_mongo_count = time.time()
mongo_count = mongo_collection.count_documents(mongo_query)  # Count matching documents in MongoDB
end_time_mongo_count = time.time()
mongo_duration_count = end_time_mongo_count - start_time_mongo_count

# === MongoDB: SEARCH ===
start_time_mongo_search = time.time()
mongo_documents_cursor = mongo_collection.find(mongo_query)  # Search for matching documents
mongo_documents_all = list(mongo_documents_cursor)
end_time_mongo_search = time.time()
mongo_duration_search = end_time_mongo_search - start_time_mongo_search

# === Return Results (without printing) ===
results = {
    "mongodb_count": mongo_count,
    "mongodb_duration_count": mongo_duration_count,
    "mongodb_documents_all": mongo_documents_all[:1],  # Return just one document for example
    "mongodb_duration_search": mongo_duration_search,
    "elasticsearch_documents_all": es_result_search['hits']['hits'][:1],  # Sample document from Elasticsearch
    "elasticsearch_duration_search": es_duration_search
}

# === Printing the Results ===
print("=== Time and Count Comparison ===")

# MongoDB results
print(f"\nMongoDB:")
print(f"  - Count: {results['mongodb_count']}")
print(f"  - Duration for Count Query: {results['mongodb_duration_count']:.6f} seconds")
print(f"  - Duration for Search Query: {results['mongodb_duration_search']:.6f} seconds")
print(f"  - Sample Document (MongoDB): {results['mongodb_documents_all']}")

# Elasticsearch results
print(f"\nElasticsearch:")
print(f"  - Duration for Search Query: {results['elasticsearch_duration_search']:.6f} seconds")
print(f"  - Sample Documents (Elasticsearch): {results['elasticsearch_documents_all']}")
