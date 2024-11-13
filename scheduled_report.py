import os
import datetime
from pymessenger import Bot
from tabulate import tabulate
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Messenger and Google API Configuration
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize LLM Model, Supabase and Pymessenger Bot
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, google_api_key=GOOGLE_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = Bot(PAGE_ACCESS_TOKEN)

# Function: LLM Chain for Generating Report
def generate_report(llm, overview, record, request):
    template = """
        You are Yeast AI, an AI that helps small local bakeries in the Philippines manage their finances.

        This is the business overview of the bakery that you are helping:
        {overview}
        
        Generate a report based on this financial record:
        {record}

        Make sure that the report is correctly calculated and is inclined to this request:
        {request}

        Make sure that your answer is simple and easy to understand without too much technical words.
        Answer only in 2-3 sentences and focus on the important insights.
        Act as if you are giving a small presentation to the user.
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"overview": overview, "record": record, "request": request})
    return result.content

# Function: Get All User ID
def get_id():
    response = supabase.table("Bakery").select("bakery_id").execute()
    user_ids = [user["bakery_id"] for user in response.data]
    return user_ids

# Function: Send Report to Users
def send_report():
    USER_IDS = get_id()
    today = datetime.utcnow()
    if today.day == 1:
        for id in USER_IDS:
            overview_found = supabase.table("Bakery").select("*").eq("bakery_id", id).execute()
            if overview_found.data:
                overview = overview_found.data[0]["overview"]
                record_found = supabase.table("Financial_Record").select("*").eq("bakery_id", id).execute()
                if record_found.data:
                    filtered_data = [{k: v for k, v in row.items() if k != "bakery_id"} for row in record_found.data]
                    headers = filtered_data[0].keys()
                    rows = [list(row.values()) for row in filtered_data]
                    record = tabulate(rows, headers=headers, tablefmt="grid")
                    bot.send_text_message(id, "Hello! Here's your monthly business report.")
                    bot.send_text_message(id, generate_report(llm, overview, record, "Generate a report for last month."))
                    bot.send_text_message(id, "Keep up the good work! Let's grow your bakery, one loaf at a time.")
                else:
                    bot.send_text_message(id, "Hello! Here's your monthly business report.")
                    bot.send_text_message(id, generate_report(llm, overview, "None", "Generate a report for last month."))
                    bot.send_text_message(id, "Keep up the good work! Let's grow your bakery, one loaf at a time.")
    else:
        for id in USER_IDS:
            overview_found = supabase.table("Bakery").select("*").eq("bakery_id", id).execute()
            if overview_found.data:
                overview = overview_found.data[0]["overview"]
                record_found = supabase.table("Financial_Record").select("*").eq("bakery_id", id).execute()
                if record_found.data:
                    filtered_data = [{k: v for k, v in row.items() if k != "bakery_id"} for row in record_found.data]
                    headers = filtered_data[0].keys()
                    rows = [list(row.values()) for row in filtered_data]
                    record = tabulate(rows, headers=headers, tablefmt="grid")
                    bot.send_text_message(id, "Hello! Here's your weekly business report.")
                    bot.send_text_message(id, generate_report(llm, overview, record, "Generate a report for last week."))
                    bot.send_text_message(id, "Keep up the good work! Let's grow your bakery, one loaf at a time.")
                else:
                    bot.send_text_message(id, "Hello! Here's your weekly business report.")
                    bot.send_text_message(id, generate_report(llm, overview, "None", "Generate a report for last week."))
                    bot.send_text_message(id, "Keep up the good work! Let's grow your bakery, one loaf at a time.")

if __name__ == "__main__":
    send_report()
