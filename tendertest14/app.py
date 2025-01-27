from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import json

# Uncomment to enable OpenAI integration
# import openai

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Uncomment and set your OpenAI API key
# openai.api_key = "your_openai_api_key"

# Load historical supplier data
try:
    historical_supplier_data = pd.read_csv("data/historical_supplier_data.csv")
    historical_supplier_data["embedding"] = historical_supplier_data["Commodity"].apply(lambda x: x.lower())
    print(f"Loaded {len(historical_supplier_data)} historical supplier records.")
except Exception as e:
    print(f"Error loading supplier data: {e}")
    historical_supplier_data = pd.DataFrame()

# FAISS index setup
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Replace with your preferred embedding model
commodity_embeddings = embedding_model.encode(historical_supplier_data["embedding"].tolist())
faiss_index = faiss.IndexFlatL2(commodity_embeddings.shape[1])
faiss_index.add(commodity_embeddings)


def call_gpt_in_chunks(prompt_template, data, chunk_size=10):
    """Handle large data by chunking and aggregating GPT responses."""
    all_responses = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        prompt = prompt_template.format(data=json.dumps(chunk, indent=2))
        
        # Uncomment for OpenAI Integration
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "system", "content": "You are a procurement AI assistant."},
        #               {"role": "user", "content": prompt}]
        # )
        # chunk_response = eval(response['choices'][0]['message']['content'])
        
        # Mocked response for testing
        chunk_response = {
            "ranked_suppliers": [
                {
                    "supplier_name": supplier["Supplier Name"],
                    "score": 95,
                    "match_percentage": 97,
                    "ranking_reason": f"High performance for {supplier['Commodity']}.",
                    "region": supplier["Region"],
                    "risks": ["Occasional delays during peak seasons."]
                }
                for supplier in chunk
            ]
        }
        all_responses.extend(chunk_response["ranked_suppliers"])
    return all_responses


@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/get_suppliers', methods=['POST'])
# def get_suppliers():
    # buyer_input = request.json
    # print(f"Buyer Input: {buyer_input}")

    # commodity = buyer_input["commodity"].lower()
    # query_embedding = embedding_model.encode([commodity])[0]

    # _, indices = faiss_index.search(query_embedding.reshape(1, -1), k=50)
    # relevant_suppliers = historical_supplier_data.iloc[indices[0]].to_dict(orient="records")

    # # Chunked processing for large data
    # prompt_template = """
    # You are an AI procurement assistant. Based on the following supplier data, provide:
    # 1. Ranked supplier recommendations with match percentage and reasons.
    # 2. Risks associated with each supplier.

    # Supplier Data:
    # {data}

    # Respond in JSON format:
    # {{
        # "ranked_suppliers": [...]
    # }}
    # """
    # ranked_suppliers = call_gpt_in_chunks(prompt_template, relevant_suppliers)

    # session["supplier_recommendations"] = {"ranked_suppliers": ranked_suppliers}
    # return jsonify({"ranked_suppliers": ranked_suppliers})
    
@app.route('/get_suppliers', methods=['POST'])
def get_suppliers():
    buyer_input = request.json
    print(f"Buyer Input: {buyer_input}")

    # Mocked GPT-4 output
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
                "ai_insights": {}  # Default empty ai_insights
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

    # Ensure every supplier has an 'ai_insights' field
    for supplier in output["ranked_suppliers"]:
        if "ai_insights" not in supplier:
            supplier["ai_insights"] = {"trends": [], "optimizations": []}

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

        # Read supplier quotations from a file
        with open('supplier_quotations.txt', 'r') as f:
            supplier_quotations = json.loads(f.read())

        # Chunked processing for large supplier quotes
        prompt_template = """
        You are an AI procurement assistant. Based on the following supplier quotations and buyer requirements, provide:
        1. Ranked supplier quotes based on price, delivery time, and terms.
        2. AI insights including trends, risks, and optimizations.

        Buyer Requirements:
        {buyer_requirements}

        Supplier Quotations:
        {data}

        Respond in JSON format:
        {{
            "ranked_quotes": [...],
            "ai_insights": {{...}}
        }}
        """
        chunked_prompt = prompt_template.format(buyer_requirements=json.dumps(event_data, indent=2))
        ranked_quotes = call_gpt_in_chunks(chunked_prompt, supplier_quotations)

        # Mocked response
        analysis = {
            "ranked_quotes": ranked_quotes,
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
