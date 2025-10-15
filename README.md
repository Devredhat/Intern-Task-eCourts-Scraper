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
https://drive.google.com/drive-viewer/AKGpihZLfo4UHP_ant-pYV1sn_9afxTJWOyBBYlQPczdLiuXhrnNy-2izNAJPY9aa2ubwp5_yRV5ivfqxFmnNuiswCNUbk-3Yr8fEJ0=w1920-h922-rw-v1

Second : 
it will open the chrome browser 

https://drive.google.com/drive-viewer/AKGpihawPo9ia2VuljWG04EVAXHapSE-s1QMkK2oKlz0sQ39BF-4F5d6UADDM1qoaSoP_MR8PIfjBRYeKF2iNiFJ9MGVdoisXBbDTQ=w1920-h922-rw-v1?auditContext=forDisplay

third : 
Dont submit the captch in the website you need to copy that captcha in the terminal and past it 

https://drive.google.com/drive-viewer/AKGpihYvr_eYA_uvVWbDgqxnk5_VlVF1EhpDBtmQq30rag4lqRhl8jEzKOaIAA5XjWNksWfkQaN5kUWVsqXQ-gyBOyjNwEOY1MQsLSA=w1920-h922

Fourth  : 

put that captcha in the terminal not in the website 

https://drive.google.com/drive-viewer/AKGpihbh4yUhE8BfZfbIayheGQk0lCJv7ieLg42qtF_R1JNb194ZIxiiZ6qUHCp1A-9Vt1HAXVteuIr14pW02KNj5cpC7RNVrylIkG4=w1920-h922?auditContext=forDisplay

Fifth :

when you click in the terminal so autometicly i the web broser in the website it will put captch and load the data 

https://drive.google.com/drive-viewer/AKGpihZGdekmlxES4vwfpn1tQyES10pm2_KrvUevqknwzr7lgGrhm1MMnpsikO7flrnyNcWsFUYxasARRTzxAAkkxdLFl_qPsuew_g=w1920-h922-rw-v1

Sixth : 

And in that website show the data and also in the terminal you will see that whole data 

https://drive.google.com/drive-viewer/AKGpihbbnMO1LTPcaMJ4-nuKelRCL6-YqRV_Yk34QNnd8b9Hwgy8IVBjB6LS14LC4piBQej5M0uC3kPxazQV8SiJTfCr7YHnfLitWpQ=w1920-h922-rw-v1

sevnth : 

it will Generate the PDF and Json file in that folder

https://drive.google.com/drive-viewer/AKGpihbUHkm9UhgqUOO2n2h2LT8Y9V9LKon0hYb0kM_3zM8kKuymHcHFVXTGO78FPsPpY_oU1A7KMydYHkbZpYlQhfzNmu0lHxrvSg=w1920-h922-rw-v1?auditContext=forDisplay

https://drive.google.com/drive-viewer/AKGpihY7wvwz54KBNFRXqd_z8dSQ04-IK-LiB9uMBWjypTYVEC0qeLbSaV6TnHp64sXBrlECJtmX5WXflCmHQGDHTwUN6fu8jQwjeuI=w1920-h922


