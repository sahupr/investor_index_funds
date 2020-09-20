from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
import backtesting.backtester as bt
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/input', methods=['POST'])
def handle_data():
    data = request.form.get('list_stock', 'rebalance')
    try:
        return 
    except:
        return "Error fetching your data"

@app.route('/chart', methods=['POST'])
def get_chart():
    cap = bt.CapWeightedBacktester(['AAPL', 'GOOG'], 1)
    chart_data = cap.get_chart()
    # chart_data = "hello world"
    foo = {'p': chart_data}
    print(request)
    foo=['a', 'b', 'c', 'd']
    return jsonify(chart_data)

if __name__ == "__main__":
    app.run(debug=True)