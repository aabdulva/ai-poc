# AI Test Failure Analysis Agent - POC

## Objective

This POC demonstrates an AI-assisted approach for analysing software test failures and finding potentially related historical engineering issues across Jira, Confluence and a Known Issues database.

The POC uses synthetic data only.

## Architecture

```text
                         TEST LOG
                            |
                            v
                  +-------------------+
                  | LLM Log Analyzer  |
                  |      Llama 3.2    |
                  +---------+---------+
                            |
                            v
                  Structured Failure
                  - Component
                  - Error Codes
                  - Symptoms
                  - Operating Condition
                  - Software Version
                            |
                            v
                  +-------------------+
                  |   Query Builder   |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |   Hybrid Search   |
                  | Semantic similarity|
                  | Component matching |
                  | Error-code matching|
                  | Symptom matching   |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  |     ChromaDB      |
                  | Jira              |
                  | Confluence        |
                  | Known Issues      |
                  +---------+---------+
                            |
                            v
                  Historical Evidence
                            |
                            v
                  +-------------------+
                  | Llama 3.2 Reasoner|
                  | Evidence-grounded |
                  | analysis           |
                  +---------+---------+
                            |
                            v
                  Engineering Analysis
                  - Previous issue
                  - Root cause
                  - Affected version
                  - Fix version
                  - Solution
                  - Evidence/source
                  - Confidence
```

## Processing Flow

1. Test log is supplied to the agent.
2. Llama 3.2 extracts important failure characteristics.
3. A search query is constructed.
4. Historical records are embedded with `all-MiniLM-L6-v2`.
5. ChromaDB performs semantic retrieval.
6. Hybrid scoring adds component, error-code and symptom signals.
7. Retrieved records are provided to Llama 3.2 as evidence.
8. The LLM generates an engineering analysis.
9. Deterministic checks verify selected facts such as exact error-code presence.
10. The result includes source IDs and software-version distinctions.

## Knowledge Normalization

Different source systems expose information differently. The POC normalizes records into a common model:

- `source`
- `id`
- `title`
- `component`
- `description`
- `root_cause`
- `solution`
- `affected_software_version`
- `fix_software_version`

This prevents the LLM from having to infer the difference between the software version affected by an issue and the version containing its fix.

## Technology Stack

- Python
- Ollama
- Llama 3.2
- ChromaDB
- Sentence Transformers
- `all-MiniLM-L6-v2`

## Running the POC

Create and activate the environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Verify Ollama:

```powershell
ollama list
```

Build the vector database:

```powershell
python -m src.retrieval.vector_store
```

Run hybrid search:

```powershell
python -m src.retrieval.test_hybrid_search
```

Run the complete agent:

```powershell
python -m src.agent.analyze_failure
```

## Current POC Scope

Included:

- LLM-based test-log understanding
- Embedding generation
- Vector search
- Hybrid retrieval
- Synthetic Jira, Confluence and Known Issues data
- Knowledge normalization
- Evidence-grounded LLM response
- Source and record traceability
- Basic deterministic evidence verification

Not included:

- Live Jira integration
- Live Confluence integration
- Live Known Issues integration
- Volvo authentication and authorization
- Production deployment
- Enterprise vector database hosting
- Production monitoring
- Production UI
- Large-scale evaluation
- Production-grade security controls

## Production Considerations

The next phase should address:

1. Access and permission model for Jira, Confluence and Known Issues.
2. Secure ingestion and indexing.
3. Incremental synchronization and document versioning.
4. Access-control filtering before retrieval.
5. Approved enterprise LLM/model hosting.
6. Auditability and source traceability.
7. Evaluation with representative historical failures.
8. False-positive and false-negative measurement.
9. Data retention and security requirements.
10. Monitoring of retrieval and answer quality.

## Conclusion

The POC demonstrates that an AI agent can transform an unstructured test failure into a structured representation, retrieve semantically and structurally related historical engineering knowledge, and generate an evidence-grounded engineering analysis.

The data is synthetic. Real source-system integration, enterprise permissions and production security should be addressed in the next phase.
