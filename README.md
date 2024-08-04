# Craft Application

The Craft application is a comprehensive platform that integrates multiple functionalities, including a social app, e-commerce app, courses app, and chat app. This extensive project features over 150 endpoints, ensuring seamless interaction and data flow between its various components. The application includes three distinct interfaces: Customer, Crafter, and Delivery, each tailored to meet the specific needs and workflows of its users.

## Table of Contents
- [Features](#features)
- [Endpoints](#endpoints)
- [Interfaces](#interfaces)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contact](#contact)

## Features
- **Social App**: Connect with other users, share updates, and follow each other's activities.
- **E-commerce App**: Browse and purchase products, manage orders, and handle payments.
- **Courses App**: Access and enroll in various courses, track progress, and receive certifications.
- **Chat App**: Communicate with other users through real-time messaging.

## Endpoints
This project features over 150 endpoints, ensuring seamless interaction and data flow between its various components. These endpoints are designed to handle a wide range of functionalities, from user authentication and profile management to order processing and real-time communication.

## Interfaces
The application includes three distinct interfaces, each tailored to meet the specific needs and workflows of its users:
- **Customer**: A user-friendly interface for customers to browse products, enroll in courses, and interact with other users.
- **Crafter**: A specialized interface for crafters to publish Courses, manage their products, track orders, and engage with customers.
- **Delivery**: A streamlined interface for delivery personnel to manage deliveries and update order statuses.

## Installation
To install and run the Craft application locally, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/Waleeddarwesh/Craft.git
    ```

2. Navigate to the project directory:
    ```sh
    cd Craft
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Apply the migrations:
    ```sh
    python manage.py migrate
    ```

5. Create a superuser:
    ```sh
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```sh
    python manage.py runserver
    ```

## Usage
Access the Swagger documentation to view all endpoints and their details:
- **Documentation**: [http://localhost:8000/docs/](http://localhost:8000/docs/)

## Contributing
We welcome contributions to the Craft application! If you would like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
    ```sh
    git checkout -b your-feature-branch
    ```

3. Make your changes and commit them:
    ```sh
    git commit -m "Description of your changes"
    ```

4. Push your changes to your fork:
    ```sh
    git push origin your-feature-branch
    ```

5. Create a pull request with a detailed description of your changes.

## Contact
For any questions or inquiries, please contact:
- Name: [Waleed Darwesh]
- Email: [Waleeddarwesh2002@gmail.com]
