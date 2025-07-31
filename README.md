# Confluence How-To Bot

A Python application for querying Redshift data and potentially creating Confluence documentation.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd confluence-how-to-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root with your database credentials:
   ```
   REDSHIFT_HOST=your-redshift-host
   REDSHIFT_DATABASE=your-database
   REDSHIFT_PORT=5439
   REDSHIFT_USER=your-username
   REDSHIFT_PASSWORD=your-password
   ```

5. **Run the application**
   ```bash
   python query_redshift.py
   ```

## Project Structure

```
confluence-how-to-bot/
├── main.py              # Main application entry point
├── query_redshift.py    # Redshift query functionality
├── utils/               # Utility functions
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
└── README.md           # This file
```

## Security

- Never commit the `.env` file to version control
- Keep database credentials secure
- Review `.gitignore` to ensure sensitive files are excluded