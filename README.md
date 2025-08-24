# Star Wars Team Builder API

A Django REST API for assembling a Star Wars team to fight the dark side! This application helps you build a team of up to 5 good characters while keeping evil ones at bay.

## 🚀 Features

### Core Functionality
- **Character Management**: Browse, filter, and search Star Wars characters
- **Evil Classification**: AI-powered system to identify evil characters based on:
  - Names containing 'Darth' or 'Sith'
  - Evil affiliations
  - Evil masters
- **Team Building**: Create and manage teams with up to 5 members
- **Smart Validation**: Prevents adding evil characters to your team

### Advanced Features
- **AI-Generated Biographies**: AI-powered character descriptions
- **Semantic Search**: Find characters by meaning, not just keywords
- **Authentication**: Register and login to manage your teams

## 🛠️ Technology Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL with pgvector for semantic search
- **AI/ML**: OpenAI newest GPT-5, LangChain, scikit-learn
- **Containerization**: Docker & Docker Compose
- **External Data**: Star Wars API integration

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API key (for AI features)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd starwars-team-builder
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file, generate a Django secret key, set your OpenAI API key and configure PostgreSQL settings
```

### 3. Run with Docker
```bash
# Build and start all services
docker-compose up --build

# The API will be available at http://localhost:8000
```

### 4. Migrate Database and Populate Characters for first time seup
```bash
# Running migrations
docker-compose exec api python manage.py migrate

# Populate initial character data (with a sample of 50 characters, and max 12 workers)
docker-compose exec api python manage.py populate_characters --limit 50 --max-workers 12 
```

## 🔗 API Endpoints

### Characters
- `GET /api/characters/` - List characters (with filtering & pagination)
- `GET /api/characters/{id}/` - Get character details
- `POST /api/characters/search?query=your+query+here&limit=5` - Semantic search

### Teams
- `GET /api/teams/` - List all teams
- `POST /api/teams/` - Create new team
- `GET /api/teams/{id}/` - Get team details
- `PUT /api/teams/{id}/` - Update team
- `DELETE /api/teams/{id}/` - Delete team
- `POST /api/teams/{id}/add-member/` - Add character to team
- `POST /api/teams/{id}/remove-member/` - Remove character from team

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - User login
