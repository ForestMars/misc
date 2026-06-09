# PEDAL (Product Engineering Delivery Automation Lifecycle)

PEDAL is a product development automation platform designed
to streamline and automate the end-to-end delivery pipeline. Built with
the power of Apache Airflow 3.x, PEDAL transforms a Product Requirements
Document (PRD) into a fully functional artifact delivery pipeline.
automating away the heavy lifting so your team can focus on what really matters.

## Table of Contents

- <a href="#Overview" class="wikilink" title="Overview">Overview</a>
- <a href="#Architecture" class="wikilink"
  title="Architecture">Architecture</a>
- <a href="#Pipeline_Workflow" class="wikilink"
  title="Pipeline Workflow">Pipeline Workflow</a>
- <a href="#Features" class="wikilink" title="Features">Features</a>
- <a href="#Getting_Started" class="wikilink"
  title="Getting Started">Getting Started</a>
  - <a href="#Prerequisites" class="wikilink"
    title="Prerequisites">Prerequisites</a>
  - <a href="#Installation" class="wikilink"
    title="Installation">Installation</a>
  - <a href="#Configuration" class="wikilink"
    title="Configuration">Configuration</a>
- <a href="#Usage" class="wikilink" title="Usage">Usage</a>
- <a href="#Testing" class="wikilink" title="Testing">Testing</a>
- <a href="#Contribution_Guidelines" class="wikilink"
  title="Contribution Guidelines">Contribution Guidelines</a>
- <a href="#License" class="wikilink" title="License">License</a>
- <a href="#Contact" class="wikilink" title="Contact">Contact</a>

## Overview

PEDAL automates the transformation of a high-level product requirements
document (PRD) into a suite of artifacts ready for development and
deployment. By leveraging Apache Airflow 3.x, PEDAL orchestrates the
following key steps:

1.  **Data Model Distillation:** Parses the PRD to extract the core data
    model.
2.  **Domain Model Generation:** Analyzes domain objects and
    hypergranularized business logic (product functions) to form a
    detailed domain model.
3.  **OpenAPI Specification (OAS) Creation:** Automatically generates an
    OpenAPI OAS file that encapsulates the API contract based on the
    domain model.
4.  **Zod Schema and Supabase Migration:** From the OpenAPI file, the
    pipeline creates a Zod schema for runtime validation and generates
    Supabase migration files to align the database schema.
5.  **Testing:** Requisite tests are created at each stage to ensure
    integrity, accuracy, and robustness of the transformation process.

## Architecture

PEDAL’s architecture is built around a modular, extendable design where
each component of the transformation pipeline is handled by dedicated
modules. The core components include:

- **Apache Airflow 3.x:** Manages and schedules the end-to-end pipeline
  as Directed Acyclic Graphs (DAGs), ensuring reliable task
  orchestration.
- **PRD Parser:** Reads and interprets the Product Requirements Document
  to extract relevant information.
- **Data & Domain Model Generator:** Processes extracted information to
  distill data models and domain objects.
- **OpenAPI OAS Generator:** Constructs the API specification based on
  the derived models.
- **Artifact Generators:** Convert the OpenAPI specification into:
  - **Zod Schema:** For robust runtime type-checking and validation.
  - **Supabase Migrations:** A migration script to update the database
    schema in sync with the API changes.
- **Testing Suite:** Automated tests validate each transformation step,
  ensuring fidelity and reliability.

## Pipeline Workflow

The PEDAL pipeline consists of the following stages:

1.  **PRD Ingestion:**
    1.  **Input:** A detailed Product Requirements Document.
    2.  **Process:** The PRD Parser extracts entities, relationships,
        and business logic.
2.  **Data Model Distillation:**
    1.  **Outcome:** A clear, structured data model that serves as the
        foundation for further processing.
3.  **Domain Model Construction:**
    1.  **Outcome:** A rich domain model representing objects and
        hypergranular business methods.
4.  **OpenAPI Specification Generation:**
    1.  **Outcome:** A fully-featured OpenAPI (OAS) file that defines
        all endpoints, schemas, and operations.
5.  **Artifact Creation:**
    1.  **Zod Schema:** Automatically generated schema for validating
        API inputs and outputs.
    2.  **Supabase Migration:** A migration script to update the
        database schema.
6.  **Automated Testing:**
    1.  Tests verify that transformations maintain the integrity of the
        product's requirements and logic.

## Features

- **End-to-End Automation:** From requirements to deployment artifacts.
- **Modular Architecture:** Easy to extend, modify, or replace
  components as needed.
- **Robust Orchestration:** Powered by Apache Airflow 3.x for reliable
  pipeline execution.
- **Integrated Testing:** Ensures each transformation step meets quality
  and reliability standards.
- **Schema Generation:** Automatically produces OpenAPI, Zod, and
  Supabase artifacts, reducing manual coding effort.

## Getting Started

### Prerequisites

- **Apache Airflow 3.x:** Ensure you have the compatible version
  installed.
- **Node.js & NPM:** For Zod schema generation and related scripts.
- **Supabase CLI/Access:** For applying and testing migration scripts.
- **Python 3.x:** To run the main pipeline and manage dependencies.

### Installation

1.  **Clone the Repository:**

``` bash
git clone https://github.com/your-org/pedal.git
cd pedal
```

1.  **Install Python Dependencies:**

``` bash
pip install -r requirements.txt
```

1.  **Install Node Dependencies:**

``` bash
cd frontend-scripts
npm install
```

1.  **Set Up Apache Airflow:**

Follow the \[Airflow installation
guide\](https://airflow.apache.org/docs/apache-airflow/stable/start.html)
to set up your Airflow environment.

### Configuration

- **Environment Variables:** Configure your \`.env\` file with required
  settings such as database credentials, Supabase keys, and Airflow
  configurations.
- **Airflow DAGs:** Ensure the DAG files are placed in the Airflow DAGs
  folder and properly configured.

## Usage

1.  **Start Airflow Scheduler & Webserver:**

``` bash
airflow scheduler
airflow webserver
```

1.  **Trigger the PEDAL Pipeline:**

- Manually trigger the DAG from the Airflow UI or schedule it as per
  your requirements.
- Monitor logs and output through the Airflow interface.

1.  **Review Artifacts:**

- Inspect the generated OpenAPI OAS file.
- Validate the Zod schema in your Node.js environment.
- Apply and test the Supabase migration.

## Testing

PEDAL includes a comprehensive testing suite to validate each stage of
the pipeline. To run tests:

``` bash
# For Python-based tests
pytest

# For Node.js based tests (if applicable)
npm test
```

Tests cover:

- PRD parsing accuracy.
- Correctness of the data and domain model generation.
- Validity of the OpenAPI specification.
- Integrity of the generated Zod schemas and Supabase migrations.

## License

⚖️ This project is copyright 2025 Continuum Software. Dependency licenses as stated. 

## Contact

For any queries or further information, please reach out to:

- **Email:** info@mlops.nyc
- **GitHub Issues:** \[GitHub Issue
  Tracker\](https://github.com/forestmars/pedal/issues)

PEDAL is the all-in-one solution to automate product engineering
delivery with efficiency, reliability, and scalability. 