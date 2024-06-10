import spacy
import re
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Load SpaCy model
nlp = spacy.load('en_core_web_sm')

# Create a dictionary to map the original terms to standardized terms
standardized_terms = {
    "debit": "debit",
    "credit": "credit",
    "sent": "debit",
    "received": "credit"
}

# Regular expressions to extract specific patterns
transaction_param = ["debit","credit", "sent", "received"]
transaction_pattern = re.compile("|".join(transaction_param), re.IGNORECASE)
# amount_pattern = re.compile(r'(?:Rs|Rs\.)\s*(\d+\.\d{2})', re.IGNORECASE)
amount_pattern = re.compile(r'(?:Rs|Rs\.)\s*(\d+(?:\.\d{1,2})?)', re.IGNORECASE)
date_time_pattern = re.compile(r'(\d{2}/\d{2}/\d{2,4}) (\d{2}:\d{2}) | (\d{2}[A-Za-z]{3}\d{2}) | (\d{2}-\d{2}-\d{4}) (\d{2}:\d{2}:\d{2}) | (\d{2}-\d{2}-\d{2})')
upi_ref_no_pattern = re.compile(r'UPI.*?(\d{12})', re.IGNORECASE)
account_pattern = re.compile(r'\b(?:a/c|ac)\s*(?:no\.\s*)?(\w+\d+)\b', re.IGNORECASE)

@app.route('/process_sentence',methods=['GET'])
def process_sentence():
    sentence = request.args.get('sentence')
    # Initialize dictionary to store extracted information
    extracted_info = {
        "Account_Number": None,
        "Transaction_Type": None,
        "Amount": None,
        "Date_of_Transaction": None,
        "Time_of_Transaction": None,
        "UPI_Reference_Number": None
    }

    # Find all matches using regular expressions
    transaction_match = transaction_pattern.search(sentence)
    amount_match = amount_pattern.search(sentence)
    date_time_match = date_time_pattern.search(sentence)
    upi_ref_no_match = upi_ref_no_pattern.search(sentence)
    account_match = account_pattern.search(sentence)

    # Extract and standardize the transaction type
    if transaction_match:
        original_type = transaction_match.group(0).lower()
        standardized_type = standardized_terms.get(original_type)
        if standardized_type:
            extracted_info["Transaction_Type"] = standardized_type

    if amount_match:
        extracted_info["Amount"] = amount_match.group(1)
    if upi_ref_no_match:
        extracted_info["UPI_Reference_Number"] = upi_ref_no_match.group(1)
    if account_match:
        extracted_info["Account_Number"] = account_match.group(1)
    if  date_time_match.group(1) and date_time_match.group(2):
        extracted_info["Date_of_Transaction"] = date_time_match.group(1)
        extracted_info["Time_of_Transaction"] = date_time_match.group(2)
    elif date_time_match.group(4) and date_time_match.group(5):
        extracted_info["Date_of_Transaction"] = date_time_match.group(4)
        extracted_info["Time_of_Transaction"] = date_time_match.group(5)
    elif date_time_match.group(3):
        extracted_info["Date_of_Transaction"] = date_time_match.group(3)
        extracted_info["Time_of_Transaction"] = None
    elif date_time_match.group(6):
        extracted_info["Date_of_Transaction"] = date_time_match.group(6)
        extracted_info["Time_of_Transaction"] = None


    # Print extracted information
    # for key, value in extracted_info.items():
    #     print(f"{key}: {value}")

    # Return the extracted information as JSON
    return jsonify(extracted_info)

if __name__ == '__main__':
    app.run(debug=True)