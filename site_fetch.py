import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document

GOOGLE_API_KEY = "AIzaSyCkoQCn0rlZuRaUZioYsuEAy9JFWrfInc0"

# Function to fetch page content using Selenium with retries
def fetch_content_with_selenium(url, max_retries=5, backoff_factor=1.5):
    # Set up Chrome options for headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    # Set up the Chrome WebDriver with custom timeouts
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)  # 30 seconds timeout for page load

    attempt = 0
    while attempt < max_retries:
        try:
            # Attempt to open the URL
            driver.get(url)
            # Wait for the page to load completely (you can add further waits for specific elements if needed)
            time.sleep(5)  # Let the page load fully if necessary
            content = driver.page_source  # Retrieve page source
            return content  # Return the HTML content
        except (TimeoutException, WebDriverException) as e:
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {backoff_factor ** attempt:.1f} seconds...")
            attempt += 1
            time.sleep(backoff_factor ** attempt)
    
    # Quit the driver and raise an error if all retries are exhausted
    driver.quit()
    raise Exception(f"Failed to retrieve content from {url} after {max_retries} attempts.")

def create_vector_store(texts):
    # Convert each text into a Document object
    documents = [Document(page_content=text) for text in texts]
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_documents = text_splitter.split_documents(documents)
    
    # Generate embeddings and create vector store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    vector_store = FAISS.from_documents(split_documents, embeddings)
    return vector_store

# Usage
personal_loan_url = 'https://www.banko.com.ph/products/instacashko-personal-loan/'
negosyoko_loan_url = 'https://www.banko.com.ph/products/fund-your-business-with-banko/'

try:
    page_content = fetch_content_with_selenium(personal_loan_url)
    print("Content fetched successfully!")
    soup = BeautifulSoup(page_content, 'html.parser')
    content = [p.text for p in soup.find_all('p')]
    print(content)

    vector_store = create_vector_store(content)

    query = "How to avail the loan?"
    relevant_docs = vector_store.similarity_search(query, k=5)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    print(context)

except Exception as e:
    print(e)
