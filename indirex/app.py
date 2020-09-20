from flask import Flask, render_template, url_for, request, redirect, jsonify
from datetime import datetime
import backtesting.backtester as bt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

# @app.route('/input', methods=['POST'])
# def handle_data():
#     # data = request.form.get('list_stock', 'rebalance')
#     try:
#         return 
#     except:
#         return "Error fetching your data"

@app.route('/chart', methods=['POST'])
def get_chart():
    l_stock = request.form.get('list_stock')
    rbl = request.form.get('rebalance')
    print(l_stock, rbl)
    cap = bt.CapWeightedBacktester([str(l_stock)], int(rbl))
    chart_data = cap.get_chart()
    # chart_data = "hello world"
    foo = {'p': chart_data}
    # print(request)
    # foo=['a', 'b', 'c', 'd']
    return jsonify(foo['p'])

if __name__ == "__main__":
    app.run(debug=True)