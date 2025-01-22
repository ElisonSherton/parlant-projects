import json
import requests
import os
from pprint import pprint

def process_json_file(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
        
        # Handle different JSON structures
        if "FAQs" in list(data.values())[0]:  # Most files have this structure
            faqs = list(data.values())[0]["FAQs"]
        else:  # Insurance FAQ has a different structure
            faqs = list(data.values())[0]

        for faq in faqs:
            # Prepare the payload
            payload = {
                "variants": [faq["question"]],
                "answer": faq["answer"] if isinstance(faq["answer"], str) else " ".join(faq["answer"])
            }

            # Make the POST request
            try:
                response = requests.post(
                    'http://localhost:8807/questions',
                    headers={'Content-Type': 'application/json', "accept": "application/json"},
                    json=payload
                )
                print()
                print(payload)
                print()
                print(f"Posted question: {faq['question']}")
                print(f"Status code: {response.status_code}")
                if not str(response.status_code).startswith("2"):
                    print(f"Error response: {response.text}")
            except Exception as e:
                print(f"Error posting question: {faq['question']}")
                print(f"Error: {str(e)}")

def main():
    # List of JSON files
    json_files = [
        'samsung-pay-faqs.json',
        'apple-pay-faqs.json',
        'balance-transfers-faqs.json',
        'dispute-faqs.json',
        'business-credit-card-faqs.json',
        'lost-stolen-card-faqs.json'
    ]

    # Process each file
    for filename in json_files:
        filepath = "qnas/" + filename
        if os.path.exists(filepath):
            print(f"\nProcessing file: {filename}")
            process_json_file(filepath)
        else:
            print(f"File not found: {filename}")

if __name__ == "__main__":
    main()