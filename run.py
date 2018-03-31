from flask import Flask, render_template, jsonify, request
import numpy as np

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
@app.route('/', methods=['GET', 'POST'])
def index():
    message = setup()
    return render_template('index.html', message=message)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

################################################
# Setup functions
def setup():
    """
    Sets up objects
    """
    params = ["vx", "vy", "T", "p", "P"]
    mat = np.random.rand(100,32,32,5)
    shape = mat.shape
    d = {t: {x: {y: dict(zip(params, mat[t][x][y])) for y in range(shape[2])} for x in range(shape[1])} for t in range(shape[0])}
    return d


if __name__ == "__main__":
    app.run(debug = True)
