from flask import Flask, render_template, url_for, redirect, request, session
from authlib.integrations.flask_client import OAuth
from google_auth_oauthlib.flow import Flow
import re
from nltk import sent_tokenize, word_tokenize
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import OperationalError
from collections import Counter
import nltk
from gensim.parsing.preprocessing import strip_tags, strip_numeric, strip_multiple_whitespaces, stem_text, strip_punctuation, remove_stopwords
from gensim.parsing import preprocess_string
import datetime
from flask import Flask, render_template, url_for, redirect, request, session
from google_auth_oauthlib.flow import Flow
import requests
nltk.download('averaged_perceptron_tagger')
nltk.download("stopwords")
nltk.download("punkt")
nltk.download('universal_tagset')
DB_PARAMS = {
    'user': 'news_dfn0_user',
    'password': 'XKvxnngz8Ut0J89YsYcjQSzQGsefx2pt',
    'host': 'dpg-cnn0haicn0vc738gjan0-a',
    'port': '5432',
    'database': 'news_dfn0'
}

app = Flask(__name__)
app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GOOGLE_CLIENT_ID'] = "7378263340-080j378qi5v96jcipg0uc5vs17s9shd0.apps.googleusercontent.com"
app.config['GOOGLE_CLIENT_SECRET'] = "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"

# Define OAuth flow
client_secrets_file = 'we.json'  # Replace with your actual client secrets file
scopes = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid']
redirect_uri = 'https://news-9maa.onrender.com/callback'
flow = Flow.from_client_secrets_file(client_secrets_file, scopes=scopes, redirect_uri=redirect_uri)
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return render_template('home.html')
    return render_template('home.html')

@app.route('/google')
def google_login():
    authorization_url, _ = flow.authorization_url(prompt='consent')
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(code=request.args.get('code'))
    session['google_token'] = flow.credentials.token
    return redirect(url_for('protected'))

@app.route('/protected',methods=['POST', 'GET'])
def protected():
    if 'google_token' in session:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('out'))

@app.route('/out')
def logout():
    session.pop('google_token', None)
    return render_template('logout.html')
@app.route("/index", methods=['POST', 'GET'])
def index():
    url_entered = False
    time = datetime.datetime.now()
    time = time.strftime("%H:%M %d %B %Y")
    site = ""
    word = 0
    sent = 0
    pos = {}
    cleaned = ""
    title = ""
    genre = ""
    key = ""
    text = ""
    
    if request.method == "POST":
        url = request.form["URL"]
        text = url
        
        try:
            page = requests.get(url)
        except Exception as e:
            error = "INVALID URL"
            return render_template("index.html", url_entered=url_entered, error=error)
        
        url_entered = True
        soup = BeautifulSoup(page.content, "html.parser")
        word = ""
        
        for i in soup.find_all("p"):
            word = word + i.get_text() + ""
            sent = sent + len(sent_tokenize(i.get_text()))
        
        cleaned = word
        list1 = nltk.pos_tag(word_tokenize(word), tagset="universal")
        list2 = []
        list3 = []
        
        for i in list1:
            list2.append(i[1])
            if i[1] not in list3:
                list3.append(i[1])
        
        for i in list3:
            pos[i] = list2.count(i)
        
        word = len(word_tokenize(word))
        title = soup.find("meta", {"property": "og:title"}).get("content")
        site = soup.find("meta", {"property": "og:site_name"}).get("content")
        list1 = nltk.corpus.stopwords.words("english")
        
        def cleaning_the_text(n):
            list = []
            list_word = word_tokenize(n)
            for i in list_word:
                if i not in list1:
                    list.append(i)
            return list
        
        transfer_to_lower = lambda s: s.lower()
        remove_single_char = lambda s: re.sub(r"\b\w\b", "", s)  # Modify to keep full-stop punctuation
        CLEAN_FILTERS = [strip_tags, strip_numeric, strip_punctuation, strip_multiple_whitespaces, transfer_to_lower, remove_stopwords, remove_single_char]
        
        def cleaning_pipe(document):
            processed_words = preprocess_string(document, CLEAN_FILTERS)
            return processed_words
        
        cleaned = cleaning_pipe(cleaned)
        key1 = Counter(cleaned).most_common(5)
        key2 = cleaned
        cleaned = " ".join(cleaned)
        
        try:
            genre = soup.find("meta", {"property": "article:section"}).get("content")
            if "news" not in genre:
                genre = genre + " news"
        except Exception as e:
            genre = Counter(key2).most_common(5)
        
        try:
            key = soup.find("meta", {"name": "news_keywords"}).get("content")
        except Exception as e:
            if site == "The Wire":
                key = soup.find("meta", {"name": "keywords"}).get("content")
            else:
                try:
                    key = cleaning_pipe(key)
                    key = list(set(key))
                except Exception as e:
                    key = key1
        
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(**DB_PARAMS)
            
            # Create a cursor object to execute SQL commands
            cur = conn.cursor()
            
            # Define the SQL command to create a table
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS News (URL varchar(200),
                    Time varchar(50),
                    News_Website VARCHAR(200),
                    No_of_words FLOAT,
                    No_of_sent FLOAT,
                    Title varchar(200),
                    Cleaned_text TEXT
                )
            '''
            
            # Execute the SQL command to create the table
            cur.execute(create_table_query)
            print("Table created successfully")
            
            # Commit the transaction
            conn.commit()
            
        except OperationalError as e:
            print("Error while connecting to PostgreSQL database:", e)
        
        try:
            # Define variables for data to be inserted into the table
            time = time
            site = site
            word = word
            sent = sent
            title = title
            cleaned = cleaned
            url = url
            
            # Define the SQL command to insert data into the table
            insert_query = '''
                INSERT INTO News (Time, News_Website, No_of_words, No_of_sent, Title, Cleaned_text, URL)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            
            # Execute the SQL command to insert data into the table
            cur.execute(insert_query, (time, site, word, sent, title, cleaned, url))
            print("Data inserted successfully")
            
            # Commit the transaction
            conn.commit()
        
        except Exception as e:
            print("Error:", e)
        
        finally:
            # Close the cursor and the database connection
            if conn:
                cur.close()
                conn.close()
                print("PostgreSQL connection is closed")
        
        return render_template("index.html", word=word, sent=sent, pos=pos, cleaned=cleaned, title=title, genre=genre, key=key, site=site, text=text, url_entered=url_entered)
    
    return render_template("index.html", url_entered=url_entered)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == DB_PARAMS["user"] and password == DB_PARAMS["password"]:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM News")
            data = cursor.fetchall()
            data=reversed(data)
            cursor.close()
            conn.close()
            return render_template('history.html', data=data) 
        else:
            fault = "Invalid Information"
            return render_template('login.html', fault=fault)
    return render_template('login.html')
if __name__ == '__main__':
    app.run(debug=True)
