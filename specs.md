Components:
On-premise Server:
The server running the application generating logs and metrics.
Fluentd Agent:
Installed on each on-premise server.
Responsible for collecting logs from the local application and forwarding them to Apache Kafka.
Apache Kafka:
Open-source distributed event streaming platform.
Acts as a scalable and durable ingestion layer for log data.
Logstash:
Open-source data processing pipeline.
Performs parsing, filtering, and enrichment of log data from Apache Kafka.
Elasticsearch:
Open-source distributed search and analytics engine.
Stores processed log data from Logstash for indexing and searching.
Kibana:
Open-source data visualization dashboard.
Provides tools for analyzing and visualizing log data stored in Elasticsearch.
Prometheus:
Open-source monitoring and alerting toolkit.
Collects and stores metrics from on-premise servers and applications for monitoring and alerting.
Workflow:
Log Generation:
Applications running on on-premise servers generate logs and expose metrics.
Fluentd Agents:
Fluentd agents collect logs from local applications and forward them to Apache Kafka.
Apache Kafka:
Ingests and stores log data from Fluentd agents.
Logstash:
Processes log data from Apache Kafka, performing parsing, filtering, and enrichment as needed.
Elasticsearch:
Stores processed log data from Logstash for indexing and searching.
Kibana:
Provides monitoring, analysis, and visualization tools for log data stored in Elasticsearch.
Prometheus:
Scrapes metrics exposed by on-premise servers and applications.
Stores metrics data for monitoring and alerting purposes.
