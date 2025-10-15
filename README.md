# 🏛️ eCourts India Case Scraper & Analyzer ⚖️

[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](./LICENSE)
[![Selenium 4.15.0](https://img.shields.io/badge/selenium-4.15.0-brightgreen.svg?style=flat-square)](https://www.selenium.dev/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9C%93-success.svg?style=flat-square)](https://github.com/yourusername/ecourts-scraper)

[![eCourts India Case Scraper](https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80)](https://github.com/yourusername/ecourts-scraper)

---

## 📘 Project Overview

**eCourts India Case Scraper & Analyzer** is a powerful Python automation tool designed to fetch detailed case information, verify hearing dates, and generate **court-ready PDF reports** directly from the [eCourts India portal](https://services.ecourts.gov.in/).  

It streamlines case management for lawyers, researchers, and legal analysts through automation, structured reporting, and real-time updates.

---

## ✨ Key Features

### 🔍 Advanced Case Management
- **Dual Search Modes:** Search by 16-digit CNR numbers or case details  
- **Real-Time Hearing Checks:** Instantly verify if a case is listed for today or tomorrow  
- **Comprehensive Data Extraction:** Retrieve full case history, party information, and current status  

### 📊 Professional Reporting
- **Automated PDF Generation:** Generate professional, court-ready reports  
- **Smart Data Presentation:** Beautiful table-based layouts with text wrapping  
- **Court-Specific Styling:** Custom formatting for different jurisdictions  

### ⚡ Automation & Efficiency
- **CAPTCHA Handling:** Intelligent retry logic with manual input support  
- **Cross-Platform:** Works on Windows, macOS, and Linux  
- **Batch Processing:** Process multiple cases efficiently  

---

## 🚀 Quick Start

### 🧩 Prerequisites
- Python **3.7+**  
- Google Chrome browser  
- Stable internet connection  

### 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Devredhat/Intern-Task-eCourts-Scraper.git
cd ecourts-scraper

# Install dependencies
pip install -r requirements.txt
```

📋 Requirements

```selenium==4.15.0
beautifulsoup4==4.12.2
webdriver-manager==4.0.1
reportlab==4.0.4
requests==2.31.0
lxml==4.9.3
```

🎯 Usage Examples (Recommended)

🔹 Basic Case Search

```# Search by CNR number
python ecourts_scraper.py MHAU030151912016

# Check if case is listed today
python ecourts_scraper.py --today MHAU030151912016

# Check if case is listed tomorrow
python ecourts_scraper.py --tomorrow MHAU030151912016
```

🔹 Advanced Search Options

```# Search by case details
python ecourts_scraper.py --today MHAU03 0151912 2016

# Download cause list (manual)
python ecourts_scraper.py --causelist

# Automated cause list download
python ecourts_scraper.py --causelist --state "Maharashtra" --district "Mumbai" --court "City Civil Court"
```

📁 Project Structure
```
ecourts-scraper/
├── 📄 ecourts_scraper.py     # Main scraper class
├── 📋 requirements.txt       # Python dependencies
├── 📖 README.md              # Project documentation
└── 📁 downloads/             # Generated files
```

🔧 Technical Features
🎨 PDF Report Generation
Professional Formatting: Court-appropriate document layout

Dynamic Content Handling: Smart text wrapping for long text

Security Features: Confidential watermarks and timestamps

Structured Layout: Table-based data representation

🔄 CAPTCHA Management
User-Friendly Interface: Clear CAPTCHA display

Retry Logic: Auto-retry on invalid inputs

Attempt Limiting: 3 attempts per search

Case Sensitivity: Correct handling of uppercase/lowercase



📊 Data Extraction Example

```
{
  "case_details": {
    "cnr_number": "MHAU030151912016",
    "filing_date": "2016-01-15",
    "registration_date": "2016-01-20",
    "case_status": "Pending",
    "court_number": "Court Room 12"
  },
  "hearing_information": {
    "next_date": "2024-01-15",
    "purpose": "Hearing",
    "previous_dates": ["2023-12-01", "2023-11-15"]
  }
}
```

🐛 Troubleshooting Guide


Issue	Solution
WebDriver Errors	Update Chrome and check internet connection
CAPTCHA Failures	Enter carefully (case-sensitive)
No Results Found	Verify CNR format (16 chars), check jurisdiction
PDF Generation Issues	Ensure reportlab is installed and file permissions are correct

💡 Tips:
Use stable internet

Avoid peak hours

Clear browser cache periodically

Keep dependencies updated

⚖️ Legal Disclaimer
⚠️ This tool is for informational and research purposes only.
Users are solely responsible for:

Complying with eCourts India's terms of service

Respecting rate limits and avoiding excessive requests

Verifying official court records before legal use

🤝 Contributing
We welcome contributions from the open-source community!


First Use this : 

```
python ecourts_scraper.py --today MHAU030151912016
```
IMG output: 

![Image](https://drive.google.com/uc?export=view&id=1ySwAqrsfr2LUor181Rdyb40tQdDb7Lfz)



Second : 
it will open the chrome browser 

![Image](https://drive.google.com/uc?export=view&id=11-QId3hjo7QzeCRhjUmA-ThPInwPTF7e)


third : 
Dont submit the captch in the website you need to copy that captcha in the terminal and past it 

![Image](https://drive.google.com/uc?export=view&id=1oC-U6o81lfW_tnTR2kTrqO2HrjMPiJ8t)


Fourth  : 

put that captcha in the terminal not in the website 

![Image](https://drive.google.com/uc?export=view&id=1NziMn1NaYwrHC1XWkoer6qkVEkAXIPEA)

Fifth :

when you click in the terminal so autometicly i the web broser in the website it will put captch and load the data 

![Image](https://drive.google.com/uc?export=view&id=1KVAPnPUGK3IaQD09YrbBzZ72z9AJMPPD)

Sixth : 

And in that website show the data and also in the terminal you will see that whole data 

![Image](https://drive.google.com/uc?export=view&id=1BAUYZVNzr0A9s2nt3QSKDTxclkLGk2Ce)

sevnth : 

it will Generate the PDF and Json file in that folder

![Image](https://drive.google.com/uc?export=view&id=1qXQ4RGygm6DL_q2ruTIF_mZOjHcu53Va)

![Image](https://drive.google.com/uc?export=view&id=1E8J--AJzAfwSJa3KHJwZvywfDjagzoHx)







