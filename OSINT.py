import requests
from bs4 import BeautifulSoup
import whois
import dns.resolver
import re
from fpdf import FPDF
import socket
import ssl
import threading
import json
from datetime import datetime
import readability as Readability
from urllib.parse import urljoin

# Constants for APIs
VIRUSTOTAL_API_KEY = "API_KEY"
SHODAN_API_KEY = "API_KEY"
IPSTACK_API_KEY = "API_KEY"
GOOGLE_PAGESPEED_API_KEY = "API_KEY"

# Port scanning configuration
PORTS_TO_SCAN = [21, 22, 25, 53, 80, 110, 143, 443, 3389]

class AdvancedInfoHunter:
    def __init__(self, domain):
        self.domain = domain
        self.report = {}
        self.security_score = 0
        self.visibility_score = 0
        self.readability_score = 0

    # WHOIS Lookup
    def get_whois_info(self):
        try:
            w = whois.whois(self.domain)
            self.report['WHOIS'] = {
                "Domain Name": w.domain_name,
                "Registrar": w.registrar,
                "Creation Date": w.creation_date,
                "Expiration Date": w.expiration_date,
                "Name Servers": w.name_servers,
                "Status": w.status
            }
        except Exception as e:
            self.report['WHOIS'] = {"Error": str(e)}

    # DNS Records
    def get_dns_records(self):
        dns_types = ['A', 'MX', 'NS', 'TXT']
        dns_records = {}
        try:
            for record_type in dns_types:
                answers = dns.resolver.resolve(self.domain, record_type, raise_on_no_answer=False)
                dns_records[record_type] = [r.to_text() for r in answers]
            self.report['DNS'] = dns_records
        except Exception as e:
            self.report['DNS'] = {"Error": str(e)}

    # SEO Lookups
    def seo_analysis(self):
        try:
            response = requests.get(f"http://{self.domain}")
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            meta_description = soup.find("meta", attrs={"name": "description"})
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            robots_txt = requests.get(urljoin(f"http://{self.domain}", "/robots.txt")).status_code == 200
            sitemap_xml = requests.get(urljoin(f"http://{self.domain}", "/sitemap.xml")).status_code == 200

            self.report['SEO'] = {
                "Title": title,
                "Meta Description": meta_description["content"] if meta_description else "Not Found",
                "Meta Keywords": meta_keywords["content"] if meta_keywords else "Not Found",
                "Robots.txt Found": robots_txt,
                "Sitemap.xml Found": sitemap_xml
            }

            # Adjust visibility score
            self.visibility_score += 2 if title else 0
            self.visibility_score += 2 if meta_description else 0
            self.visibility_score += 2 if robots_txt else 0
            self.visibility_score += 2 if sitemap_xml else 0
        except Exception as e:
            self.report['SEO'] = {"Error": str(e)}

    # Readability Analysis
    def analyze_readability(self):
        try:
            response = requests.get(f"http://{self.domain}")
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = " ".join(soup.stripped_strings)
            if text_content:
                r = Readability(text_content)
                flesch_score = r.flesch().score
                self.report['Readability'] = {"Flesch Reading Ease": flesch_score}
                self.readability_score += min(max((flesch_score - 30) / 70 * 10, 0), 10)
            else:
                self.report['Readability'] = {"Error": "No readable content found"}
        except Exception as e:
            self.report['Readability'] = {"Error": str(e)}

    # PageSpeed Analysis
    def analyze_pagespeed(self):
        try:
            url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=http://{self.domain}&key={GOOGLE_PAGESPEED_API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                speed_score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0) * 100
                self.report['PageSpeed'] = {"Performance Score": speed_score}
                self.visibility_score += min(speed_score / 10, 10)
            else:
                self.report['PageSpeed'] = {"Error": "Unable to fetch PageSpeed data"}
        except Exception as e:
            self.report['PageSpeed'] = {"Error": str(e)}

    # SSL Certificate Details
    def get_ssl_info(self):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
            self.report['SSL'] = {
                "Issuer": cert['issuer'],
                "Valid From": cert['notBefore'],
                "Valid Until": cert['notAfter'],
                "Subject": cert['subject']
            }
            self.security_score += 5  # Add points for valid SSL
        except Exception as e:
            self.report['SSL'] = {"Error": str(e)}

    # Security Enforcement
    def check_https(self):
        try:
            response = requests.get(f"https://{self.domain}")
            if response.status_code == 200:
                self.report['HTTPS'] = "HTTPS Enforced"
                self.security_score += 5
            else:
                self.report['HTTPS'] = "HTTPS Not Enforced"
        except:
            self.report['HTTPS'] = "HTTPS Not Enforced"

    # Overall Rating
    def calculate_ratings(self):
        avg_score = (self.security_score + self.visibility_score + self.readability_score) / 3
        self.report['Overall Rating'] = {
            "Security": self.security_score,
            "Visibility": self.visibility_score,
            "Readability": self.readability_score,
            "Overall Score": round(avg_score, 2)
        }

    # PDF Report Generation
    def generate_pdf_report(self):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"OSINT and SEO Report for {self.domain}", ln=True, align="C")
        pdf.ln(10)
        for section, data in self.report.items():
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(0, 10, txt=f"{section}:", ln=True)
            pdf.set_font("Arial", size=10)
            if isinstance(data, dict):
                for key, value in data.items():
                    pdf.multi_cell(0, 10, txt=f"{key}: {value}")
            else:
                pdf.multi_cell(0, 10, txt=str(data))
            pdf.ln(5)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_output = f"{self.domain}_Report_{timestamp}.pdf"
        pdf.output(pdf_output)
        print(f"PDF Report saved as {pdf_output}")

    # Full Analysis
    def generate_report(self):
        self.get_whois_info()
        self.get_dns_records()
        self.seo_analysis()
        self.analyze_readability()
        self.analyze_pagespeed()
        self.get_ssl_info()
        self.check_https()
        self.calculate_ratings()
        self.generate_pdf_report()

# Run the tool
if __name__ == "__main__":
    domain = input("Enter the domain (e.g., example.com): ")
    osint_tool = AdvancedInfoHunter(domain)
    osint_tool.generate_report()