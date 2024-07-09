# Project Name

This project is a collection of Python scripts for handling different functionalities such as creating a database, sending emails, and communicating via MQTT.

## Files

### `create_database.py`

This script creates an SQLite database and defines two tables: `projects` and `tasks`.

- **Functions:**
  - `create_connection(db_file)`: Establishes a connection to the SQLite database.
  - `create_table(conn, create_table_sql)`: Creates a table using the provided SQL statement.
  - `main()`: Main function to create the database and tables.

### `email_handler.py`

This script sends an email using SMTP.

- **Functions:**
  - `send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, login, password)`: Sends an email using the provided SMTP server details.
  - `main()`: Main function to send a test email.

### `mqtt_comunication.py`

This script handles MQTT communication.

- **Functions:**
  - `on_connect(client, userdata, flags, rc)`: Callback function for when the client connects to the broker.
  - `on_message(client, userdata, msg)`: Callback function for when a message is received from the broker.
  - `main()`: Main function to set up MQTT client and start the loop.

## Usage

1. **Create Database:**
   Run `create_database.py` to create the SQLite database and tables.
   ```sh
   python create_database.py
