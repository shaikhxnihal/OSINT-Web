from flask import Flask, request, jsonify
from flask_cors import CORS
from OSINT import AdvancedInfoHunter

app = Flask(__name__)
CORS(app)


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    domain = data.get('domain')
    if not domain:
        return jsonify({"error": "Domain is required"}), 400

    try:
        osint_tool = AdvancedInfoHunter(domain)
        osint_tool.generate_report()

        # Example: Calculate ratings (0–10) for different categories
        report = osint_tool.report
        ratings = {
            "security": min(report.get("ssl_score", 0), 10),  # Adjust to 0-10 scale
            "seo": len(report.get("meta_tags", {}).get("keywords", [])) / 2,  # Example logic
            "readability": report.get("readability", {}).get("score", 0) / 10,  # Normalize
            "visibility": report.get("google_rank", {}).get("position", 10),  # Example logic
        }

        return jsonify({"report": report, "ratings": ratings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
