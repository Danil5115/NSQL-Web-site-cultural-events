# Seminar Website

## Overview

Welcome to the Seminar Website, a platform designed to explore and discover cultural events in the city. This project leverages a microservices architecture encapsulated in Docker containers, incorporating MongoDB for event storage, Redis for caching, and Neo4j for event recommendations. Let's dive into the features and technologies that make this project stand out.

## Features

### 1. Cultural Event Exploration

Explore a diverse range of cultural events, including theatrical performances, musical concerts, festivals, educational events, and art exhibitions.

### 2. Search and Redis Cache

Efficiently search for events using our intelligent search engine. The system utilizes Redis caching to optimize search results, ensuring a responsive and seamless user experience.

### 3. Recommendations with Neo4j

Enhance your event discovery with personalized recommendations powered by Neo4j. The graph database analyzes event types and suggests similar events, creating a tailored experience for users.

### 4. MongoDB Integration

Persistently store and retrieve event data using MongoDB, a NoSQL database. Seamlessly add new events and retrieve existing ones with the flexibility of a document-oriented database.

### 5. User-Friendly Web Interface

The web interface is built using Flask, a lightweight and extensible web framework in Python. Bootstrap 5 ensures a visually appealing and responsive design for users on various devices.

### 6. Dockerized Microservices

Embrace the power of containerization with Docker, simplifying deployment and ensuring consistent behavior across different environments. Each service operates independently, promoting scalability and maintainability.

## Technologies Used

- **Flask:** A Python web framework for building robust and scalable web applications.

- **MongoDB:** A NoSQL database for flexible and efficient data storage.

- **Redis:** In-memory data structure store for caching search results and optimizing performance.

- **Neo4j:** A graph database for handling complex relationships and providing personalized recommendations.

- **Docker:** Containerization for easy deployment, scalability, and environment consistency.

- **Bootstrap 5:** Front-end framework for creating visually appealing and responsive user interfaces.

## Examples

### Home Page

![Home Page](https://github.com/Danil5115/NSQL-Web-site-cultural-events/blob/main/code/home.png)

The home page welcomes users, providing a search engine to find events and displaying recommendations based on their preferences.

### Events Page

![Events Page](https://github.com/Danil5115/NSQL-Web-site-cultural-events/blob/main/code/events.png)

The events page showcases upcoming cultural events, providing detailed information about each event.

### Add Event Page

![Add Event Page](https://github.com/Danil5115/NSQL-Web-site-cultural-events/blob/main/code/add_event.png)

Users can contribute to the platform by adding new events, specifying details such as event name, location, date, description, and type.

### Recommendations from neo4j and their links
![Recommendations](https://github.com/Danil5115/NSQL-Web-site-cultural-events/blob/main/code/recomendation.png)

### Docker
![Docker](https://github.com/Danil5115/NSQL-Web-site-cultural-events/blob/main/code/Docker.png)

