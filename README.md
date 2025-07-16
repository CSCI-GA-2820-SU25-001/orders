# Order Service
[![Build Status](https://github.com/CSCI-GA-2820-SU25-001/orders/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU25-001/orders/actions)
[![codecov](https://codecov.io/github/CSCI-GA-2820-SU25-001/orders/graph/badge.svg?token=T6I3PGTLDV)](https://codecov.io/github/CSCI-GA-2820-SU25-001/orders)
## Overview

This is a RESTful microservice for managing orders in an online store. The service is built using Flask and PostgreSQL, and supports full CRUD operations along with query filtering.

The `/service` folder contains the business logic and service endpoints. The `/tests` folder contains model and route-level unit tests.

## Running the service

Run the following commands

### Setup
```
git clone https://github.com/CSCI-GA-2820-SU25-001/orders.git
cd orders
make lint
make test
```
### Running
You can then run your project:
```
make run
```

The service will be available at ``http://localhost:8080`` in your browser.

## curl request

### Order

#### CREATE Order
```
curl -i -X POST http://localhost:8080/orders \
     -H "Content-Type: application/json" \
     -d '{
           "name": "My First Order",
           "customer_id": 42
         }'
```

#### GET order collection
```
curl -i http://localhost:8080/orders
```
#### GET specific order
```
curl -i http://localhost:8080/orders/<ORDER_ID>
```
#### DELETE specific order
```
curl -i -X PUT http://localhost:8080/orders/<ORDER_ID> \
     -H "Content-Type: application/json" \
     -d '{
           "name": "Updated Order Name",
           "customer_id": 99
         }'
```


### Order Item

Make sure there is a corresponding Order created before


#### GET Order Item collection
```
curl -i http://localhost:8080/orders/<ORDER_ID>/items/<ITEM_ID>
```

#### GET Order Item collection

```curl -i http://localhost:8080/orders/<ORDER_ID>/items/<ITEM_ID>```

#### LIST Order Item
```
curl -i http://localhost:8080/orders/<ORDER_ID>/items
```


#### Update specific order
```
curl -i -X PUT http://localhost:8080/orders/<ORDER_ID>/items/<ITEM_ID> \
     -H "Content-Type: application/json" \
     -d '{
           "name": "MacBook Pro 14\" (M3)",
           "product_id": 1234,
           "quantity": 3
         }'
```


#### Delete

```curl -i -X DELETE http://localhost:5000/orders/<ORDER_ID>/items/<ITEM_ID>```


## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```
 

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
