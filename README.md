# Flask Email Analytics API

This project is a Flask-based API for sending emails via Postmark and tracking their engagement (sends, opens, clicks). It includes Swagger documentation for easy exploration and testing of the API.

## Setup

To get started, you'll need to set up your environment variables and initialize the Flask application.

### Environment Variables

Before running the project, ensure the following environment variables are set:

- `FLASK_APP`: Points to your `app.py` file.
- `FLASK_DEBUG=1`: Enables Flask's debug mode.
- `FLASK_ENV=development`: Sets the environment to development.
- `POSTMARK_API_TOKEN`: Your Postmark API token.

**Note:** Since the Postmark account is in sandbox mode, you may need to change the "sender" address in `services.py`. Normally, this address would be stored in a config file or as an environment variable rather than being hardcoded.

### Initial Setup

1. Initialize the database:
   ```bash
   flask db init
   ```
2. Create the initial migration:
    ``` bash
   flask db migrate -m "Initial migration"
   ```
3. Apply the migration:
    ```bash
   flask db upgrade
   ```
4. Run the flask application:
    ```bash
   flask run
   ```
   
### Accessing Swagger Documentation
You can access the Swagger documentation to explore and test the API at: http://127.0.0.1:5000/swagger-ui.

### Future Improvements
1. **GraphQL for Dynamic Queries**: If this application were to grow larger, we might consider using GraphQL to handle dynamic and complex queries more efficiently. For now, this would add unnecessary complexity given the current size of the project.
2. **Refactoring Business Logic**: The routes.py file is becoming somewhat large. Ideally, more of the business logic would be moved into dedicated services to keep the route handlers clean and focused.
3. **Database Improvement**: Currently, SQLAlchemy is configured to create a local SQLite database. For production, we should consider replacing it with a hosted database solution like PostgreSQL, MongoDB, or another similar service.
   