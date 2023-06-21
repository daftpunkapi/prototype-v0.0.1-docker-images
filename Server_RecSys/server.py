from flask import Flask, request
from os import environ
from model import get_recommendations

app = Flask(__name__)

@app.route('/customerinput', methods=['POST'])
def customer_input():
    body_params = request.json
    customer_id = body_params["customer_id"]
    zone = body_params["zone"]
    print("Customer ID:", customer_id)
    print("Zone:", zone)

    top5 = get_recommendations(customer_id,zone)
    print(top5)
    json_top5 = top5.to_json(orient='records')

    return json_top5

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=environ.get("PORT", 3000))