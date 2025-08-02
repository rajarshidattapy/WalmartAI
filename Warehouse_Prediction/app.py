from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Load CSV once
df = pd.read_csv('data/data.csv', parse_dates=['LAST_ORDER_DATE', 'EXPECTED_DELIVERY_DATE', 'ACTUAL_DELIVERY_DATE'])
df['MONTH'] = df['LAST_ORDER_DATE'].dt.to_period('M').astype(str)

@app.route('/')
def index():
    locations = df['SHIPPING_LOCATION'].dropna().unique().tolist()
    months = df['MONTH'].dropna().unique().tolist()
    products = df['PRODUCT_NAME'].dropna().unique().tolist()
    return render_template('index.html', locations=locations, months=months, products=products)

@app.route('/get_data', methods=['POST'])
def get_data():
    location = request.json.get('location')
    month = request.json.get('month')
    product_search = request.json.get('product_search', '')

    filtered = df.copy()
    if location != 'All':
        filtered = filtered[filtered['SHIPPING_LOCATION'] == location]
    if month:
        filtered = filtered[filtered['MONTH'] == month]
    if product_search:
        filtered = filtered[filtered['PRODUCT_NAME'].str.contains(product_search, case=False, na=False)]

    grouped = filtered.groupby(['SHIPPING_LOCATION', 'PRODUCT_NAME', 'MONTH'])['ORDER_UNITS'].sum().reset_index()
    
    # Use quantiles for balanced demand levels
    if len(grouped) >= 3:
        grouped['Demand_Level'] = pd.qcut(
            grouped['ORDER_UNITS'],
            q=3,
            labels=['Low', 'Medium', 'High']
        )
    else:
        # Fallback to original bins if not enough products
        grouped['Demand_Level'] = pd.cut(
            grouped['ORDER_UNITS'],
            bins=[0, 20, 40, float('inf')],
            labels=['Low', 'Medium', 'High']
        )

    records = grouped.to_dict(orient='records')
    return jsonify(records)

@app.route('/search_products', methods=['POST'])
def search_products():
    search_term = request.json.get('search_term', '')
    if not search_term:
        return jsonify([])
    
    # Search for products containing the search term
    matching_products = df[df['PRODUCT_NAME'].str.contains(search_term, case=False, na=False)]['PRODUCT_NAME'].unique().tolist()
    return jsonify(matching_products[:10])  # Limit to 10 results

@app.route('/analytic/<analytic_type>', methods=['POST'])
def analytic(analytic_type):
    location = request.json.get('location')
    month = request.json.get('month')
    # Dummy responses for each analytic type
    if analytic_type == 'on_time_delivery_rate':
        return jsonify({"rate": "92.5%"})
    elif analytic_type == 'avg_lead_time':
        return jsonify({"average_lead_time_days": 4.2})
    elif analytic_type == 'supplier_otif_leaderboard':
        return jsonify({"leaderboard": [
            {"supplier": "Supplier A", "otif": "98%"},
            {"supplier": "Supplier B", "otif": "95%"}
        ]})
    elif analytic_type == 'delay_heatmap':
        return jsonify({"heatmap": [["Location 1", 5], ["Location 2", 2]]})
    elif analytic_type == 'units_received_vs_planned':
        return jsonify({"received": 1200, "planned": 1500})
    elif analytic_type == 'rolling_lateness_trend':
        return jsonify({"trend": [
            {"month": "2024-01", "late": 10},
            {"month": "2024-02", "late": 7},
            {"month": "2024-03", "late": 12}
        ]})
    elif analytic_type == 'pareto_late_units':
        return jsonify({"pareto": [
            {"supplier": "Supplier A", "late_units": 50},
            {"supplier": "Supplier B", "late_units": 30}
        ]})
    elif analytic_type == 'scatter_leadtime_ordersize':
        return jsonify({"scatter": [
            {"order_units": 100, "lead_time": 3},
            {"order_units": 200, "lead_time": 5}
        ]})
    elif analytic_type == 'calendar_inbound_volume':
        return jsonify({"calendar": [
            {"date": "2024-03-01", "units": 300},
            {"date": "2024-03-02", "units": 250}
        ]})
    elif analytic_type == 'expected_vs_actual_gap':
        return jsonify({"gaps": [
            {"date": "2024-03-01", "gap_days": 1},
            {"date": "2024-03-02", "gap_days": -1}
        ]})
    else:
        return jsonify({"error": "Unknown analytic type"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
