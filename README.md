# End-to-End Sensor Data Processing Pipeline on AWS

This project implements a scalable, event-driven pipeline for ingesting, processing, and exposing sensor data. The entire infrastructure is deployed on AWS using Terraform, and the application is containerized with Docker and orchestrated by Kubernetes (EKS).

## Architecture

The architecture is designed around a microservices pattern, with services communicating asynchronously via an Apache Kafka message queue.

```
                               +---------------------+
                               |      Clients        |
                               +---------------------+
                                         |
                                         v
                               +---------------------+
                               |   AWS Load Balancer |
                               +---------------------+
                                         |
                                         v
+-------------------+      +-------------------------+      +-----------------------+
|   Producer Service|      |     Consumer Service    |      |      API Service      |
| (Kubernetes Pod)  | ---> |   (Kubernetes Pod)      | ---> |   (Kubernetes Pod)    |
+-------------------+      +-------------------------+      +-----------------------+
          |                            |                            |
          v                            v                            v
+-------------------+      +-------------------------+      +-----------------------+
|   Kafka (AWS MSK) |      |  PostgreSQL (AWS RDS)   |      |  PostgreSQL (AWS RDS) |
+-------------------+      +-------------------------+      +-----------------------+

```

1.  **Data Ingestion**: A `producer` service (running in a Kubernetes pod) generates simulated sensor data and sends it to an AWS MSK (Managed Streaming for Kafka) topic.
2.  **Data Processing & Storage**: A `consumer` service subscribes to the Kafka topic, receives the sensor data, and persists it into an AWS RDS PostgreSQL database.
3.  **Data Access**: An `api` service provides a RESTful API for external clients to query the sensor data stored in the database. This service is exposed to the internet via an AWS Load Balancer.
4.  **Infrastructure**: All the underlying AWS resources (VPC, EKS cluster, MSK cluster, RDS instance, IAM roles, and security groups) are defined and managed using Terraform.
5.  **Containerization**: The `producer`, `consumer`, and `api` services are all containerized using Docker.
6.  **Orchestration**: The containerized services are deployed and managed on a Kubernetes cluster (AWS EKS).

## Technology Stack

*   **Cloud Provider**: AWS
*   **Infrastructure as Code**: Terraform
*   **Containerization**: Docker
*   **Orchestration**: Kubernetes (AWS EKS)
*   **Messaging**: Apache Kafka (AWS MSK)
*   **Database**: PostgreSQL (AWS RDS)
*   **Application Backend**: Python
*   **Frameworks/Libraries**:
    *   Flask (for the REST API)
    *   `kafka-python` (for Kafka integration)
    *   `psycopg2-binary` (for PostgreSQL integration)

## Project Structure

```
.
├── k8s/                    # Kubernetes manifests
│   ├── api.yaml
│   ├── configmap.yaml
│   ├── consumer-deployment.yaml
│   ├── producer-deployment.yaml
│   └── secret.yaml
├── .terraform/             # Terraform state
├── api.py                  # Flask API application
├── consumer.py             # Kafka consumer application
├── producer.py             # Kafka producer application
├── *.tf                    # Terraform files for AWS infrastructure
├── docker-compose.yml      # For local development environment
├── *.Dockerfile            # Dockerfiles for each service
└── requirements.txt        # Python dependencies
```

## Prerequisites

*   [AWS CLI](https://aws.amazon.com/cli/) configured with your credentials.
*   [Terraform](https://www.terraform.io/downloads.html)
*   [Docker](https://docs.docker.com/get-docker/)
*   [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
*   An account on [Docker Hub](https://hub.docker.com/)

## Deployment Steps

### 1. Build and Push Docker Images

You will need to build the Docker images for the three services and push them to your own Docker Hub repository.

```bash
# Replace 'your-dockerhub-username' with your actual Docker Hub username
export DOCKER_USERNAME=your-dockerhub-username

docker build -t $DOCKER_USERNAME/producer:v1 -f producer.Dockerfile .
docker build -t $DOCKER_USERNAME/consumer:v2 -f consumer.Dockerfile .
docker build -t $DOCKER_USERNAME/api:v1 -f api.Dockerfile .

docker push $DOCKER_USERNAME/producer:v1
docker push $DOCKER_USERNAME/consumer:v2
docker push $DOCKER_USERNAME/api:v1
```

After pushing the images, update the image names in the Kubernetes deployment files (`k8s/*.yaml`) to point to your Docker Hub repository.

### 2. Deploy AWS Infrastructure

Use Terraform to provision the necessary AWS resources.

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the changes
terraform apply
```

This will create the VPC, EKS cluster, MSK cluster, and RDS database. The process will take several minutes.

### 3. Configure kubectl

Once the EKS cluster is created, configure `kubectl` to connect to it.

```bash
aws eks --region $(terraform output -raw aws_region) update-kubeconfig --name $(terraform output -raw cluster_name)
```

### 4. Deploy the Application to Kubernetes

Apply the Kubernetes manifests to deploy the services.

```bash
# Apply the ConfigMap and Secret
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy the services
kubectl apply -f k8s/producer-deployment.yaml
kubectl apply -f k8s/consumer-deployment.yaml
kubectl apply -f k8s/api.yaml
```

### 5. Access the API

Find the external IP address of the API service's Load Balancer.

```bash
kubectl get svc sensor-api-service
```

You can then use this IP address to access the API endpoints.

## API Endpoints

*   `GET /`: Health check.
*   `GET /data/latest`: Get the latest 100 sensor readings.
*   `GET /data/stats`: Get aggregated statistics for the last 24 hours.
*   `GET /data/by-sensor/<sensor_id>`: Get the last 50 readings for a specific sensor.

## Local Development

A `docker-compose.yml` file is provided to spin up a local development environment with Kafka and PostgreSQL.

```bash
docker-compose up -d
```

You can then run the Python applications (`producer.py`, `consumer.py`, `api.py`) locally. Make sure to set the required environment variables (e.g., `DB_HOST`, `KAFKA_BOOTSTRAP_SERVERS`) to point to `localhost`.

## Cleanup

To tear down all the AWS resources created by Terraform, run:

```bash
terraform destroy
```
