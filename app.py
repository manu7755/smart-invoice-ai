import pytesseract
from PIL import Image
from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def extract_details(text):
    data = {}

    vendor = re.search(r"Vendor[:\- ]*(.*)", text)
    total = re.search(r"Total[:\- ]*₹?([\d,]+)", text)
    date = re.search(r"(?i)(?:Date|Invoice Date)[:\- ]*([\d\/\-]+)", text)

    if vendor: data["vendor"] = vendor.group(1).strip()
    if total: data["total_amount"] = total.group(1).strip()
    if date: data["invoice_date"] = date.group(1).strip()

    # Basic expense classification
    if "medical" in text.lower():
        data["category"] = "Medical"
    elif "travel" in text.lower() or "flight" in text.lower():
        data["category"] = "Travel"
    else:
        data["category"] = "General Business Expense"

    return data

@app.route("/extract", methods=["POST"])
def extract_invoice():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    
    img_path = "invoice.png"
    file.save(img_path)

    text = pytesseract.image_to_string(Image.open(img_path))
    result = extract_details(text)

    os.remove(img_path)
    return jsonify(result)

@app.route("/")
def home():
    return "SmartInvoice AI Running Successfully!"

if __name__ == "__main__":
    app.run(debug=True)
