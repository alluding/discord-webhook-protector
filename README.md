## Flask Discord Webhook Protector

### Requirements
- Python 3.10+
- Flask
- requests

### Usage Guide

1. **Installation**
   
   Ensure you have Python installed. Clone or download this repository to your local environment.

2. **Setup**

   - Install the required packages:
     ```
     pip install flask requests
     ```

   - Define environment variables:
     Set the environment variable `hook` to the URL of your destination webhook.

3. **Configuration**

   Modify the `ip_whitelist` in the `Webhook` class to include authorized IP addresses. This restricts access to the webhook endpoint.

4. **Run the Application**

   Run the Flask application:
   ```
   python app.py
   ```
   You can also change `app` to something else, `server`, `main`, etc.

### Functionality

- **IP Whitelisting**
  - Define authorized IPs in the `ip_whitelist` attribute of the `Webhook` class.
  - Incoming requests from unauthorized IPs will receive a `403 Forbidden` response.

- **Request Type Check**
  - Requests using unauthorized HTTP methods (e.g., DELETE) will receive a `405 Method Not Allowed` response.

- **Rate Limiting**
  - Limit the number of requests from a single IP within a specified timeframe (`ratelimit` attribute in seconds).
  - Exceeding the limit triggers a `429 Too Many Requests` response.
---


Licensed under `MIT`.
