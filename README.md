# Mini CricHeroes

A backend cricket match management and scoring system built with Python, Django REST Framework, and SQLite/PostgreSQL.

The project started as a Python-based cricket scoring application and was evolved into a REST API backend with authentication, match lifecycle management, innings scoring, scorecards, automated match completion, API documentation, validation, logging, and automated tests.

## Features

- Player and team management
- Match creation and management
- Toss management
- Batting and bowling team selection
- Innings creation
- Opening batsman selection
- Bowler selection
- Ball-by-ball scoring
- Runs, extras, wides and no-balls
- Wicket recording
- Batsman replacement
- Strike rotation
- Automatic innings completion
- Automatic match completion
- Match result calculation
- Batting scorecards
- Bowling scorecards
- JWT authentication
- Endpoint-level authorization
- Request validation
- Global API exception handling
- Structured application logging
- Swagger/OpenAPI documentation
- SQLite development database
- PostgreSQL-ready configuration
- Automated test suite

## Tech Stack

- Python 3
- Django
- Django REST Framework
- PostgreSQL / SQLite
- Simple JWT
- drf-spectacular
- Pytest
- Django Test Framework
- Git / GitHub

## Architecture

The project follows a layered backend architecture:

```text
Client
   |
   v
URL Routing
   |
   v
API Views
   |
   +---- Serializers / Validation
   |
   v
Service Layer
   |
   v
Django ORM
   |
   v
Database