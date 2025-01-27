from flask import Flask, request, jsonify, render_template, session
import pandas as pd

# Uncomment to enable OpenAI integration
# import openai

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Uncomment and set your OpenAI API key
# openai.api_key = "your_openai_api_key"

# Load historical supplier data
try:
    historical_supplier_data = pd.read_csv("data/historical_supplier_data.csv").to_dict(orient="records")
    print(f"Loaded {len(historical_supplier_data)} historical supplier records.")
except Exception as e:
    print(f"Error loading supplier data: {e}")
    historical_supplier_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_suppliers', methods=['POST'])
def get_suppliers():
    buyer_input = request.json
    print(f"Buyer Input: {buyer_input}")

    # Uncomment the OpenAI integration code below for supplier recommendations

    # """
    # prompt = f"""
    # You are an AI procurement assistant. Based on the following historical supplier data and buyer input, provide:
    # 1. Ranked supplier recommendations with match percentage and reasons.
    # 2. Risks associated with each supplier.
    # 3. AI insights including trends and optimizations.

    # Historical Supplier Data:
    # {historical_supplier_data}

    # Buyer Input:
    # {buyer_input}

    # Respond in JSON format:
    # {{
    #   "ranked_suppliers": [
    #       {{
    #           "supplier_name": "Supplier Name",
    #           "score": 95,
    #           "match_percentage": 97,
    #           "ranking_reason": "Reason for ranking.",
    #           "region": "Supplier region",
    #           "risks": ["Risk 1", "Risk 2"],
    #           "ai_insights": {{
    #               "trends": ["Trend 1", "Trend 2"],
    #               "optimizations": ["Optimization 1", "Optimization 2"]
    #           }}
    #       }},
    #       ...
    #   ],
    #   "ai_insights": {{
    #       "trends": [...],
    #       "risks": [...],
    #       "optimizations": [...]
    #   }}
    # }}
    # """
    # try:
    #     response = openai.ChatCompletion.create(
    #         model="gpt-4",
    #         messages=[{"role": "system", "content": "You are a procurement AI assistant."},
    #                   {"role": "user", "content": prompt}]
    #     )
    #     output = eval(response['choices'][0]['message']['content'])
    # except Exception as e:
    #     print(f"OpenAI GPT-4 Error: {e}")
    #     return jsonify({"error": "Failed to get AI recommendations."}), 500

    # Mocked GPT-4 output for now
    output = {
        "ranked_suppliers": [
            {
                "supplier_name": "TechWorld",
                "score": 95,
                "match_percentage": 97,
                "ranking_reason": "Reliable and cost-effective.",
                "region": "North America",
                "risks": ["Occasional delays during peak seasons."],
                "ai_insights": {
                    "trends": ["Increased demand for electronics in North America."],
                    "optimizations": ["Negotiate long-term contracts for better pricing."]
                }
            },
            {
                "supplier_name": "DataMax",
                "score": 90,
                "match_percentage": 92,
                "ranking_reason": "Fast delivery and good pricing.",
                "region": "Europe",
                "risks": ["Slightly lower quality rating for certain items."],
                "ai_insights": {
                    "trends": ["European suppliers are offering discounts this quarter."],
                    "optimizations": ["Combine orders with other commodities to save costs."]
                }
            }
        ],
        "ai_insights": {
            "trends": [
                "RAM prices are expected to increase by 10% next quarter."
            ],
            "risks": [
                "Potential supply chain delays during peak seasons."
            ],
            "optimizations": [
                "Split orders across suppliers for better pricing and delivery times."
            ]
        }
    }

    session["supplier_recommendations"] = output
    return jsonify(output)

@app.route('/edit_event', methods=['GET', 'POST'])
def edit_event():
    if request.method == 'POST':
        data = request.json
        session['selected_suppliers'] = data.get('selected_suppliers', [])
        session['quantity'] = data.get('quantity', '')
        session['commodity'] = data.get('commodity', '')
        session['budget'] = data.get('budget', '')
        return jsonify({"message": "Suppliers selected successfully!"})

    # Pass the stored data to the template
    return render_template(
        'edit_event.html',
        selected_suppliers=session.get('selected_suppliers', []),
        quantity=session.get('quantity', ''),
        commodity=session.get('commodity', ''),
        budget=session.get('budget', '')
    )

@app.route('/publish_event', methods=['POST'])
def publish_event():
    event_data = request.json
    print(f"Published Event Data: {event_data}")

    # Store the published event data in the session
    session["published_event"] = {
        "selected_suppliers": session.get("selected_suppliers", []),
        "quantity": session.get("quantity", ""),
        "commodity": session.get("commodity", ""),
        "budget": session.get("budget", ""),
        "payment_terms": event_data.get("payment_terms", ""),
        "delivery_deadline": event_data.get("delivery_deadline", "")
    }

    return jsonify({"message": "Event published successfully! Redirecting to analyze quotes."})

@app.route('/analyze_quotes', methods=['GET'])
def analyze_quotes():
    try:
        event_data = session.get("published_event", {})
        if not event_data:
            raise ValueError("No event data found. Please publish an event first.")

        print(f"Event Data for Analysis: {event_data}")

        # Uncomment the OpenAI integration code below for analyzing quotes

        # """
        # prompt = f"""
        # You are an AI procurement assistant. Based on the following supplier quotations and buyer requirements, provide:
        # 1. Ranked supplier quotes based on price, delivery time, quality, and additional terms.
        # 2. Explanations for the rankings, highlighting trade-offs.
        # 3. AI insights including trends, risks, and optimizations.

        # Buyer Requirements:
        # {event_data}

        # Supplier Quotations:
        # {supplier_quotations}

        # Respond in JSON format:
        # {{
        #   "ranked_quotes": [
        #       {{
        #           "supplier_name": "Supplier Name",
        #           "price_per_unit": 1200,
        #           "total_cost": 120000,
        #           "delivery_date": "2025-01-25",
        #           "additional_terms": "Free shipping for orders above $10,000.",
        #           "score": 96,
        #           "explanation": "Ranked high due to competitive pricing, fast delivery, and excellent terms."
        #       }},
        #       ...
        #   ],
        #   "ai_insights": {{
        #       "trends": [...],
        #       "risks": [...],
        #       "optimizations": [...],
        #       "sustainability": [...]
        #   }}
        # }}
        # """
        # try:
        #     response = openai.ChatCompletion.create(
        #         model="gpt-4",
        #         messages=[{"role": "system", "content": "You are a procurement AI assistant."},
        #                   {"role": "user", "content": prompt}]
        #     )
        #     output = eval(response['choices'][0]['message']['content'])
        # except Exception as e:
        #     print(f"OpenAI GPT-4 Error: {e}")
        #     return jsonify({"error": "Failed to get AI insights."}), 500

        # Mocked supplier quotes for testing
        quotes = [
            {
                "supplier_name": "TechWorld",
                "price_per_unit": 1200,
                "total_cost": 120000,
                "delivery_date": "2025-01-25",
                "additional_terms": "Free shipping for orders above $10,000.",
                "score": 96,
                "explanation": "Ranked high due to competitive pricing, fast delivery, and excellent terms."
            },
            {
                "supplier_name": "DataMax",
                "price_per_unit": 1150,
                "total_cost": 138000,
                "delivery_date": "2025-01-24",
                "additional_terms": "5% discount for orders above 150 units.",
                "score": 92,
                "explanation": "Strong ranking due to discounted pricing and early delivery."
            }
        ]

        # Mocked AI insights
        analysis = {
            "ranked_quotes": quotes,
            "ai_insights": {
                "trends": ["RAM prices are stable this quarter.", "High demand expected in Q2."],
                "risks": ["Potential delivery delays due to global chip shortages."],
                "optimizations": ["Negotiate bulk discounts with top suppliers.", "Split orders to minimize risks."]
            }
        }

        return render_template('analyze_quotes.html', analysis=analysis, enumerate=enumerate)

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
