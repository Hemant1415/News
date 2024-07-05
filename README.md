# News
# News Analysis Web App

This Flask-based web application analyzes news articles from provided URLs, extracting various statistics and storing cleaned data in a PostgreSQL database. Users can log in using Google OAuth for access and view their browsing history.

## Features

- **Google OAuth Login:** Users can authenticate via Google OAuth to access the application.
- **URL Parsing:** Extracts text content, metadata (title, site, genre, keywords), and performs text cleaning.
- **Text Analysis:** Utilizes NLTK and Gensim libraries for tokenization, POS tagging, and keyword extraction.
- **Database Integration:** Stores analyzed data in a PostgreSQL database for retrieval and history tracking.
- **User Access Control:** Admin access for specific users based on email domain.

## Prerequisites

- Python 3.x
- Flask
- Authlib
- NLTK
- Gensim
- psycopg2
- Requests
- BeautifulSoup

## Setup

1. Clone the repository:


3. Set up PostgreSQL:
- Create a database with the name news_dfn0.
- Update DB_PARAMS in app.py with your database credentials.

4. Configure Google OAuth:
- Obtain client credentials from Google Developers Console.
- Update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in app.py.
- Update client_secrets_file with your OAuth client secrets file path.

5. Run the application:

Access the application at http://localhost:5000.

## Usage

- Navigate to http://localhost:5000/ in your web browser.
- Log in using Google OAuth to start analyzing news articles.
- Enter a valid URL of a news article to analyze its content.
- View cleaned text, statistics, and metadata extracted from the article.
- Access browsing history by logging in as an admin (username: postgres, password: Hemant1415) or through Google OAuth.

## Contributions

Contributions are welcome! Please fork the repository and create a pull request with your improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
