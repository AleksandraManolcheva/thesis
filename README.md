# thesis
3.1.7.1 Test Scenario 1: Searching for the Number of Documents Based on a Specific Indexed Value (Value that is stored in cache memory)

Find all patient documents that are located in the state of Minnesota or Michigan:

# === MongoDB: COUNT ===
mongo_count = mongo_collection.count_documents({
    "input_parameters.state": {
        "$in": ["Minnesota", "Michigan"]
    }
})
# === MongoDB: SEARCH ===
mongo_documents_cursor = mongo_collection.find({
    "input_parameters.state": {
        "$in": ["Minnesota", "Michigan"]
    }
})
# === Elasticsearch: COUNT ===
es_query = {
    "query": {
        "terms": {
            "input_parameters.state.keyword": ["Minnesota", "Michigan"]
        }
    }
}
es_result_count = es.count(index=es_index, body=es_query)
# === Elasticsearch: SEARCH ===
es_result_search = es.search(index=es_index, body=es_query)
