# thesis
This project evaluates and compares search performance across MongoDB and Elasticsearch when applied to healthcare data workflows, specifically focusing on eligibility assessment, financial documentation, and patient status tracking within large-scale, distributed systems.

This repository includes:

-Simulated patient documents mimicking real-world healthcare data flows.

-Test scenarios assessing query performance under both indexed and non-indexed fields.

-Sample queries executed on both MongoDB and Elasticsearch.

-A JSON schema of the healthcare documents indexed in Elasticsearch.

-Logstash synchronization configuration

-The ElasticStack configuration set up (Elasticsearch, Logstash, Kibana)

JSON Document Mapping used:
{
  "health_insurance_data": {
    "mappings": {
      "properties": {
        "advice": { "type": "text" },
        "ages": { "type": "long" },
        "citizenship_status": { "type": "text" },
        "disability": { "type": "long" },
        "eligibility": {
          "properties": {
            "CHIP": { "type": "text" },
            "Marketplace": { "type": "text" },
            "Medicaid": { "type": "text" },
            "Medicare": { "type": "text" }
          }
        },
        "eligibility_summary": {
          "properties": {
            "CHIP": { "type": "text" },
            "Marketplace": { "type": "text" },
            "Medicaid": { "type": "text" },
            "Medicare": { "type": "text" }
          }
        },
        "expenses": {
          "properties": {
            "active": { "type": "float" },
            "passive": { "type": "float" }
          }
        },
        "family_size": { "type": "long" },
        "income": { "type": "float" },
        "medical_necessity": { "type": "boolean" },
        "residency_status": { "type": "text" },
        "state": { "type": "text" },
        "timestamp": { "type": "date" },
        "visit_data": { "type": "text" },
        "remaining_income": { "type": "float" },
        "claims_status": {
          "type": "nested",
          "properties": {
            "patient_id": { "type": "long" },
            "status": { "type": "text" },
            "claim_type": { "type": "text" },
            "coverage": { "type": "text" }
          }
        },
        "provider_incentives": {
          "type": "nested",
          "properties": {
            "provider_id": { "type": "long" },
            "location": { "type": "text" },
            "specialty": { "type": "text" },
            "incentive": { "type": "text" }
          }
        },
        "input_parameters": {
          "properties": {
            "ages": { "type": "long" },
            "citizenship_status": { "type": "text" },
            "disability": { "type": "boolean" },
            "expenses": {
              "properties": {
                "active": { "type": "long" },
                "passive": { "type": "long" }
              }
            },
            "family_size": { "type": "long" },
            "income": { "type": "long" },
            "location": { "type": "text" },
            "medical_necessity": { "type": "boolean" },
            "residency_status": { "type": "text" },
            "state": { "type": "text" },
            "timestamp": { "type": "date" }
          }
        }
      }
    }
  }
}

The Test scenarios-query used for performance comparison of the both relational vs non-relational database:

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

3.1.7.2 Test Scenario 2: Searching for the Number of Documents Based on a Non-Indexed Value
The query used - Find all patient documents that citizens in their states, it should look for the word citizen with case insensitivity properties:
# === MongoDB: COUNT ===
mongo_count = mongo_collection.count_documents({
    "input_parameters.citizenship_status": {
        "$regex": "citizen",
        "$options": "i"
    }
})
# === MongoDB: SEARCH ===
mongo_documents_cursor = mongo_collection.find({
    "input_parameters.citizenship_status": {
        "$regex": "citizen",
        "$options": "i"
    }
})
# === Elasticsearch: COUNT ===
es_query = {
    "query": {
        "wildcard": {
            "input_parameters.citizenship_status": {
                "value": "*citizen",
                "case_insensitive": True
            }
        }
    }
}
es_result_count = es.count(index=es_index, body=es_query)

# === Elasticsearch: SEARCH ===

es_result_search = es.search(index=es_index, body=es_query)

3.1.7.3 Test Scenario 3: Searching Documents Based on a Specific Value with Tokenization and Partial Search
Query used:
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


