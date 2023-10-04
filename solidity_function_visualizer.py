from graph_tool.all import *
import openai
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import SolidityLexer
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route("/contract-analysis", methods=["POST"])
def contract_analysis():
    contract_code = request.json["code"]

    result = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Summarize the functions in the following Solidity contract:\n\n{contract_code}\n\nFunction Summaries:\n",
        temperature=0.5,
        max_tokens=600
    )

    function_summary = result.choices[0].text.strip()

    G = Graph(directed=True)
    name = G.new_vertex_property("string")

    function_dict = {}

    for line in function_summary.split("\n"):
        if "calls" in line:
            function, calls = line.split(" calls ")
            if function not in function_dict:
                function_dict[function] = G.add_vertex()
                name[function_dict[function]] = function
            if calls not in function_dict:
                function_dict[calls] = G.add_vertex()
                name[function_dict[calls]] = calls
            G.add_edge(function_dict[function], function_dict[calls])

    graph_draw(G, vertex_text=name, vertex_font_size=18, output_size=(200, 200),
               output=os.path.join(app.root_path, 'static', 'graph.png'))

    formatter = HtmlFormatter(style='colorful', linenos=True)
    code = highlight(contract_code, SolidityLexer(), formatter)
    style = f"<style>{formatter.get_style_defs('.highlight')}</style><body>{code}</body>"

    return {
        "functionSummary": function_summary,
        "contractCode": style,
        "graphPath": f'{request.url_root}static/graph.png'
    }

@app.route("/static/<image_name>", methods=["GET"])
def serve_image(image_name):
    return send_from_directory('static', filename=image_name, as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
