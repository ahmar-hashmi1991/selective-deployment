Components:
On-premise Server:
The server running the application generating logs.
Fluentd Agent:
Installed on each on-premise server.
Responsible for collecting logs from the local application and forwarding them to Azure Event Hubs.
Azure Event Hubs:
Azure service for ingesting and storing event data.
Acts as a scalable and reliable entry point for log data.
Azure Stream Analytics:
Azure service for real-time stream processing.
Performs data transformation, filtering, and aggregation on log data streamed from Azure Event Hubs.
Azure Monitor Logs:
Azure service for centralized log storage.
Stores processed log data from Azure Stream Analytics.
Azure Monitor:
Azure service for monitoring and analysis.
Provides tools for analyzing and visualizing log data stored in Azure Monitor Logs.
Workflow:
Log Generation:
Applications running on on-premise servers generate logs.
Fluentd Agents:
Fluentd agents collect logs from local applications and forward them to Azure Event Hubs.
Azure Event Hubs:
Ingests and stores log data from Fluentd agents.
Azure Stream Analytics:
Processes log data in real-time, performing filtering, transformation, and aggregation as needed.
Azure Monitor Logs:
Stores processed log data for historical analysis and retention.
Azure Monitor:
Provides monitoring, analysis, and visualization tools for log data stored in Azure Monitor Logs.
