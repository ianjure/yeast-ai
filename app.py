from supabase import create_client, Client
from datetime import datetime
from flask import Flask, request
from pymessenger import Bot
from tabulate import tabulate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Supabase Configuration
SUPABASE_URL = "https://tfsimbugdbcqrwadiwbg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRmc2ltYnVnZGJjcXJ3YWRpd2JnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzAwOTk3OTIsImV4cCI6MjA0NTY3NTc5Mn0.OoyLtHdn8y32hCfocWQN669jeRQTEF5ZNi4qJ0Bj9cU"

# Messenger and Google API Configuration
PAGE_ID = "488959514289720"
PAGE_ACCESS_TOKEN = "EAAY6ZBeZAOy6gBOZCYM3DqOEsxPdEtXAZBerCUnoWIxi8B68ajvqiVWb6lgNLYIHQdR8zlXMSTJaDCNm1hDaGLcDIqZBsuQ5It2iGZCmDtccEyMs7QFKK62q3w6Dm2MzMpRzzhOoe4Wn4tMnihKkr9EIdTqi7GD2TchfeL6IJFz9XC9ZBihvBqK5UevzNrLxGQZCbRbSwyuFRgZDZD"
GOOGLE_API_KEY = "AIzaSyCkoQCn0rlZuRaUZioYsuEAy9JFWrfInc0"

# Initialize Supabase, Pymessenger Bot and Flask App
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = Bot(PAGE_ACCESS_TOKEN)
app = Flask(__name__)

# Function: Supabase Data Entry
def save_data(profits: float, expenses: float):
    data = {
        "bakery_id": 1,
        "profits": profits,
        "expenses": expenses,
        "date": str(datetime.now().date())
    }
    supabase.table("Financial_Record").insert(data).execute()

# Function: Supabase Data Update
def update_data(profits: float, expenses: float):
    data = {
        "bakery_id": 1,
        "profits": profits,
        "expenses": expenses,
        "date": str(datetime.now().date())
    }
    supabase.table("Financial_Record").update(data).eq("date", str(datetime.now().date())).execute()

#Function: Send a Generic Message Template
def send_generic_template(recipient_id):
    elements = [
        {
            "title": "Welcome to Yeast AI!",
            "image_url": "https://i.imgur.com/3XN9LQF.jpeg",
            "subtitle": "Let’s grow your business, one loaf at a time!",
            "buttons": [
                {
                    "type": "web_url",
                    "url": "https://forms.gle/U5kpXjS1DnaNAEfd6",
                    "title": "Sign-up"
                },
            ]
        }
    ]
    bot.send_generic_message(recipient_id, elements)

# Function: LLM Chain for Generating Business Overview
def generate_business_overview(llm, answers):
    template = """
        Generate a business overview of a bakery using these answers from a questionnaire:

        1. How long has your bakery been open? (Years in business) - {q1}
        2. Who owns the bakery? (Ownership) - {q2}
        3. How much money did your bakery make last year? (Annual revenue) - {q3}
        4. Are your bakery's sales steady throughout the year? (Sales consistency) - {q4}
        5. Can you tell when your bakery has its busiest times? (Peak seasons) - {q5}
        6. Do you keep track of your bakery's spending? (Expense records) - {q6}
        7. Do you feel okay looking at your bakery's money reports? (Financial comfort) - {q7}
        8. Do you understand words like "sales," "income," "costs," and "profit"? (Financial terms) - {q8}
        9. Can you tell if your bakery is doing well by looking at its money reports? (Financial understanding) - {q9}
        10. Would you like to learn more about managing your bakery's money? (Learning needs) - {q10}
        11. If you needed a loan, what would you use it for? (e.g., new oven, more ingredients, bigger space) - {q11}
        12. About how much money would you need to borrow? - {q12}
        13. How many months would you need to pay the loan back? (provide number of months, e.g., 8) - {q13}

        Make it short while maintaining the important details. Please answer directly.
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"q1": answers["q1"], "q2": answers["q2"], "q3": answers["q3"],
                           "q4": answers["q4"], "q5": answers["q5"], "q6": answers["q6"],
                           "q7": answers["q7"], "q8": answers["q8"], "q9": answers["q9"],
                           "q10": answers["q10"], "q11": answers["q11"], "q12": answers["q12"], 
                           "q13": answers["q13"]})
    return result.content

# Function: LLM Chain for User Message Categorization
def categorize_message(llm, message):
    template = """
        You are an AI categorizer that categorizes what the user replies using these 5 categories:
        1. Question - if the user replies with a question.
        2. Profits - if the user enters a profit.
        3. Expenses - if the user enters an expense.
        4. Profits and Expenses - if the user enters a profit and expense at the same time.
        5. Report - if the user wants to create a report.
        6. Conversation - if the user message does not fit with the other categories.

        Only answer one of these 5 categories. Please answer directly.

        This is what the user sent: {message}
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"message": message})
    return result.content

# Function: LLM Chain for User Data Entry
def data_message(llm, message):
    template = """
        You are an AI that replies to the user after they inputted their profits and expenses.
        Always reply that their data is entered successfully, but use a different phrase.

        This is what the user sent: {message}
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"message": message})
    return result.content

# Function: LLM Chain for Extracting Data Entry Amount
def data_extract(llm, message):
    template = """
        Extract the profits and expenses from user input into a list.
        If the user did not input a profit or an expense, set it to zero.
        Answer directly and follow this format: [profit,expenses]

        This is what the user inputted: {message}
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"message": message})
    return result.content.replace(" ","").replace("[","").replace("]","")

# Function: LLM Chain for Question Answering
def answer_question(llm, message):
    template = """
        You are Yeast AI, an AI that helps small local bakeries in the Philippines manage their finances.
        Answer only question related to business, bakeries, and finance.
        Answer this question like a financial partner of a small local bakery and provide solutions in 2-3 sentences:
        {message}
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"message": message})
    return result.content

# Function: LLM Chain for Generating Report
def generate_report(llm, record):
    template = """
        You are Yeast AI, an AI that helps small local bakeries in the Philippines manage their finances.
        Generate a report based on this financial record:
        {record}

        Answer only in 2-3 sentences and focus on the important insights.
        Act as if you are giving a small presentation to the user.
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"record": record})
    return result.content

# Function: LLM Chain for Generating Business Status
def generate_status(llm, overview, record):
    template = """
        You are Yeast AI, an AI that helps small local bakeries in the Philippines manage their finances.
        Generate a business status based on this business overview:
        {overview}
        
        Also, use this financial record:
        {record}

        Answer only in 2-3 sentences and focus on the important insights.
        Act as if you are giving a small presentation to the user.
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"overview": overview, "record": record})
    return result.content

# Function: LLM Chain for User Conversation
def converse(llm, message):
    template = """
        You are Yeast AI, an AI that helps small local bakeries in the Philippines manage their finances.
        Answer only question related to business, bakeries, and finance.
        Interact with the user like a financial partner of a small local bakery in 1-2 sentences only.

        This is the user's message: {message}
        """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    result = chain.invoke({"message": message})
    return result.content

# Webhook Verification
@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "yeastai":
            return "Verification token missmatch", 403
        return request.args['hub.challenge'], 200
    
    return "Hello world", 200

# Main Route
@app.route("/", methods=['POST'])
def webhook():
    data = request.get_json()

    # Loop through the Entries
    for entry in data['entry']:
        for messaging_event in entry['messaging']:
            sender_id = messaging_event['sender']['id']

            # Check if Event Contains 'message' Key & Page is not the Sender
            if ('message' in messaging_event) and (sender_id != PAGE_ID):
                message = messaging_event['message'].get('text')

                if message:

                    # Initializing LLM Model
                    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, google_api_key=GOOGLE_API_KEY)

                    # Sign-up Process
                    code = supabase.table("Bakery").select("*").eq("username", message).execute()

                    if (code.data) and (code.data[0]['bakery_id'] == 0):
                        answers = {
                            "q1": code.data[0]['q1'],
                            "q2": code.data[0]['q2'],
                            "q3": code.data[0]['q3'],
                            "q4": code.data[0]['q4'],
                            "q5": code.data[0]['q5'],
                            "q6": code.data[0]['q6'],
                            "q7": code.data[0]['q7'],
                            "q8": code.data[0]['q8'],
                            "q9": code.data[0]['q9'],
                            "q10": code.data[0]['q10'],
                            "q11": code.data[0]['q11'],
                            "q12": code.data[0]['q12'],
                            "q13": code.data[0]['q13']
                        }

                        data = {
                            "bakery_id": sender_id,
                            "overview": generate_business_overview(llm, answers)
                        }
                        supabase.table("Bakery").update(data).eq("username", code.data[0]["username"]).execute()

                    # Authenticate User
                    authenticate = supabase.table("Bakery").select("*").eq("bakery_id", sender_id).execute()

                    if authenticate.data:

                        # Categorize the Message
                        category = categorize_message(llm, message).strip().lower()

                        # Process Outputs Based on User Input
                        if category == "question":
                            bot.send_text_message(sender_id, answer_question(llm, message))
                        elif category == "profits":
                            result = data_extract(llm, message)
                            profits = result.split(",")[0]
                            record_found = supabase.table("Financial_Record").select("*").eq("date", str(datetime.now().date())).execute()
                            if record_found.data:
                                update_data(profits, record_found.data[0]["expenses"])
                            else:
                                save_data(profits, 0)
                            bot.send_text_message(sender_id, data_message(llm, message))
                        elif category == "expenses":
                            result = data_extract(llm, message)
                            expenses = result.split(",")[1]
                            record_found = supabase.table("Financial_Record").select("*").eq("date", str(datetime.now().date())).execute()
                            if record_found.data:
                                update_data(record_found.data[0]["profits"], expenses)
                            else:
                                save_data(0, expenses)
                            bot.send_text_message(sender_id, data_message(llm, message))
                        elif category == "profits and expenses":
                            result = data_extract(llm, message)
                            profits = result.split(",")[0]
                            expenses = result.split(",")[1]
                            record_found = supabase.table("Financial_Record").select("*").eq("date", str(datetime.now().date())).execute()
                            if record_found.data:
                                update_data(profits, expenses)
                            else:
                                save_data(profits, expenses)
                            bot.send_text_message(sender_id, data_message(llm, message))
                        elif category == "report":
                            record_found = supabase.table("Financial_Record").select("*").eq("bakery_id", sender_id).execute()
                            if record_found.data:
                                filtered_data = [{k: v for k, v in row.items() if k != "bakery_id"} for row in record_found.data]
                                headers = filtered_data[0].keys()
                                rows = [list(row.values()) for row in filtered_data]
                                record = tabulate(rows, headers=headers, tablefmt="grid")
                                print(record)
                                bot.send_text_message(sender_id, generate_report(llm, record))
                        elif category == "status":
                            overview_found = supabase.table("Bakery").select("*").eq("bakery_id", sender_id).execute()
                            if overview_found.data:
                                overview = overview_found.data[0]["overview"]
                                record_found = supabase.table("Financial_Record").select("*").eq("bakery_id", sender_id).execute()
                                if record_found.data:
                                    filtered_data = [{k: v for k, v in row.items() if k != "bakery_id"} for row in record_found.data]
                                    headers = filtered_data[0].keys()
                                    rows = [list(row.values()) for row in filtered_data]
                                    record = tabulate(rows, headers=headers, tablefmt="grid")
                                    print(record)
                                    bot.send_text_message(sender_id, generate_status(llm, overview, record))
                        else:
                            bot.send_text_message(sender_id, converse(llm, message))
                    else:
                        send_generic_template(sender_id)
            elif 'read' in messaging_event:
                continue
            elif 'delivery' in messaging_event:
                continue
            elif 'postback' in messaging_event:
                continue
    return "OK", 200

if __name__ == '__main__':
   app.run(port=8080, debug=True)