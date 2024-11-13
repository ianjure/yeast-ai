from pymessenger import Bot
import os
from tabulate import tabulate
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

GOOGLE_API_KEY = "AIzaSyCkoQCn0rlZuRaUZioYsuEAy9JFWrfInc0"

# Initialize LLM Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, google_api_key=GOOGLE_API_KEY)

# Supabase Configuration
SUPABASE_URL = "https://tfsimbugdbcqrwadiwbg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRmc2ltYnVnZGJjcXJ3YWRpd2JnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAwOTk3OTIsImV4cCI6MjA0NTY3NTc5Mn0.OoyLtHdn8y32hCfocWQN669jeRQTEF5ZNi4qJ0Bj9cU"

# Access token for the bot (stored in GitHub secrets)
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
bot = Bot(PAGE_ACCESS_TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function: LLM Chain for Generating Report
def generate_report(llm, overview, record, request):
    template = """
        You are Yeast AI, an AI that helps small local bakeries in the Philippines manage their finances.

        This is the business overview of the bakery that you are helping:
        {overview}
        
        Generate a report for this week based on this financial record:
        {record}

        Make sure that your answer is simple and easy to understand without too much technical words.
        Answer only in 2-3 sentences and focus on the important insights.
        Act as if you are giving a small presentation to the user.
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"overview": overview, "record": record, "request": request})
    return result.content

# List of user IDs to send the message to
user_id = supabase.table("Bakery").select("*").execute()

USER_IDS = ["USER_ID_1", "USER_ID_2"]  # Replace with actual Facebook user IDs

def send_weekly_message():
    for user_id in USER_IDS:
        overview_found = supabase.table("Bakery").select("*").eq("bakery_id", sender_id).execute()
            if overview_found.data:
                overview = overview_found.data[0]["overview"]
                record_found = supabase.table("Financial_Record").select("*").eq("bakery_id", sender_id).execute()
                if record_found.data:
                    filtered_data = [{k: v for k, v in row.items() if k != "bakery_id"} for row in record_found.data]
                    headers = filtered_data[0].keys()
                    rows = [list(row.values()) for row in filtered_data]
                    record = tabulate(rows, headers=headers, tablefmt="grid")
                    bot.send_text_message(sender_id, "Hello! Here's your weekly business update.")
                    bot.send_text_message(sender_id, generate_report(llm, overview, record, message))
                    bot.send_text_message(sender_id, "Keep up the good work! Let's grow your bakery, one loaf at a time.")
                else:
                    bot.send_text_message(sender_id, "Hello! Here's your weekly business update.")
                    bot.send_text_message(sender_id, generate_report(llm, overview, "None", message))
                    bot.send_text_message(sender_id, "Keep up the good work! Let's grow your bakery, one loaf at a time.")

if __name__ == "__main__":
    send_weekly_message()
