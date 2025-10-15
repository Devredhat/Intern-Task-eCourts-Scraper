from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import argparse
from datetime import datetime, timedelta
import time
import os
import requests
import re
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import textwrap

class ECourtsScraper:
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        self.wait = WebDriverWait(self.driver, 25)
        
        # Create downloads folder
        os.makedirs("downloads", exist_ok=True)
    
    def submit_captcha(self):
        """Handle CAPTCHA submission with retry logic"""
        for attempt in range(3):
            try:
                # Wait for CAPTCHA image to load
                time.sleep(2)
                captcha_text = input("Enter CAPTCHA: ")
                captcha_field = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "fcaptcha_code"))
                )
                captcha_field.clear()
                captcha_field.send_keys(captcha_text)
                time.sleep(1)
                
                # Click search button
                submit_button = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "searchbtn"))
                )
                submit_button.click()
                print(f"Attempt {attempt + 1}: Submitted CAPTCHA")
                
                # Wait for page transition
                time.sleep(5)
                
                # Check for visible error alerts
                try:
                    alert_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, ".alert-danger, .alert-danger-cust, .error"
                    )
                    
                    has_error = False
                    for alert in alert_elements:
                        if alert.is_displayed() and alert.text.strip():
                            error_text = alert.text.lower()
                            if "captcha" in error_text or "invalid" in error_text:
                                print(f"Error: {alert.text}")
                                has_error = True
                                break
                    
                    if has_error and attempt < 2:
                        print("Invalid CAPTCHA, retrying...")
                        self.driver.execute_script("refreshCaptcha();")
                        time.sleep(2)
                        continue
                    
                    print("CAPTCHA accepted! Loading results...")
                    return True
                    
                except Exception:
                    print("CAPTCHA submitted! Proceeding...")
                    return True
                    
            except Exception as e:
                print(f"CAPTCHA error: {str(e)}")
                if attempt < 2:
                    time.sleep(1)
                    continue
                return False
        
        return False
    
    def wait_for_results(self):
        """Wait for results to load"""
        print("Waiting for case details to load...")
        time.sleep(5)
        
        for check_attempt in range(5):
            try:
                # Check multiple possible result containers
                selectors = ["#history_cnr", ".case-details", ".result-container", ".table-responsive"]
                
                for selector in selectors:
                    try:
                        result_div = self.driver.find_element(By.CSS_SELECTOR, selector)
                        result_html = result_div.get_attribute('innerHTML')
                        
                        if result_html and len(result_html.strip()) > 50:
                            print("Results loaded successfully!")
                            return True
                    except:
                        continue
                
                print(f"Loading... ({check_attempt + 1}/5)")
                time.sleep(2)
                
            except Exception:
                print(f"Checking... ({check_attempt + 1}/5)")
                time.sleep(2)
        
        return False
    
    def fetch_case_by_cnr(self, cnr_full):
        """Fetch case details using CNR number"""
        try:
            url = "https://services.ecourts.gov.in/ecourtindia_v6/"
            self.driver.get(url)
            time.sleep(3)
            
            # Enter CNR
            search_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "cino"))
            )
            search_field.clear()
            search_field.send_keys(cnr_full)
            
            print(f"Searching for CNR: {cnr_full}")
            print("Please enter the CAPTCHA visible on screen.")
            
            # Submit CAPTCHA
            if not self.submit_captcha():
                return None
            
            # Wait for results
            if not self.wait_for_results():
                print("Failed to load results")
                return None
            
            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            history_div = soup.find('div', {'id': 'history_cnr'})
            
            if not history_div or not history_div.get_text(strip=True):
                print("No case details found")
                return None
            
            case_data = self.parse_case_details(history_div, cnr_full)
            
            # Create PDF from case data
            pdf_path = self.create_case_pdf(case_data)
            if pdf_path:
                case_data["pdf_created"] = True
                case_data["pdf_path"] = pdf_path
            else:
                case_data["pdf_created"] = False
            
            return case_data
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def fetch_case_by_details(self, case_type, case_number, case_year):
        """Fetch case details using case type, number, and year"""
        try:
            url = "https://services.ecourts.gov.in/ecourtindia_v6/"
            self.driver.get(url)
            time.sleep(3)
            
            # Select case type
            case_type_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "case_type"))
            )
            select = Select(case_type_dropdown)
            
            # Try to find matching case type
            case_type_found = False
            for option in select.options:
                if case_type.upper() in option.text.upper() or option.get_attribute("value") == case_type:
                    select.select_by_visible_text(option.text)
                    case_type_found = True
                    break
            
            if not case_type_found:
                print(f"Case type '{case_type}' not found. Using first available option.")
                select.select_by_index(1)
            
            # Enter case number
            case_no_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "case_no"))
            )
            case_no_field.clear()
            case_no_field.send_keys(case_number)
            
            # Enter case year
            case_year_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "rgyear"))
            )
            case_year_field.clear()
            case_year_field.send_keys(case_year)
            
            print(f"Searching for Case: {case_type}/{case_number}/{case_year}")
            print("Please enter the CAPTCHA visible on screen.")
            
            # Submit CAPTCHA
            if not self.submit_captcha():
                return None
            
            # Wait for results
            if not self.wait_for_results():
                print("Failed to load results")
                return None
            
            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            history_div = soup.find('div', {'id': 'history_cnr'})
            
            if not history_div or not history_div.get_text(strip=True):
                print("No case details found")
                return None
            
            # Extract CNR if available
            cnr_match = re.search(r'CNR No[.:]\s*([A-Z0-9]+)', history_div.get_text())
            cnr_full = cnr_match.group(1) if cnr_match else f"{case_type}{case_number}{case_year}"
            
            case_data = self.parse_case_details(history_div, cnr_full)
            
            # Create PDF from case data
            pdf_path = self.create_case_pdf(case_data)
            if pdf_path:
                case_data["pdf_created"] = True
                case_data["pdf_path"] = pdf_path
            else:
                case_data["pdf_created"] = False
            
            return case_data
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_case_details(self, history_div, cnr_full):
        """Parse case details from HTML"""
        case_data = {
            "cnr_number": cnr_full,
            "search_date": str(datetime.now().date()),
            "available": True,
            "case_details": {},
            "hearings": [],
            "orders": [],
            "listing_info": {}
        }
        
        # Extract tables
        tables = history_div.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True).replace(':', '').strip()
                    value = cols[1].get_text(strip=True)
                    if key and value:
                        # Clean up the value - remove extra spaces and fix formatting
                        value = re.sub(r'\s+', ' ', value).strip()
                        case_data["case_details"][key] = value
        
        # Extract hearing information more accurately
        text_content = history_div.get_text().lower()
        
        # Look for next hearing date pattern
        hearing_patterns = [
            r'next hearing date[:\s]*([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})',
            r'next date[:\s]*([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})',
            r'hearing date[:\s]*([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})',
            r'listed on[:\s]*([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})'
        ]
        
        for pattern in hearing_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                case_data["listing_info"]["next_hearing_date"] = matches[0]
                break
        
        # Extract court information
        court_info_patterns = [
            r'court[:\s]*([^\n]+)',
            r'before[:\s]*([^\n]+)',
            r'judge[:\s]*([^\n]+)'
        ]
        
        for pattern in court_info_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                case_data["listing_info"]["court"] = matches[0].strip()
                break
        
        # Extract serial number if available
        serial_patterns = [
            r'serial no[.:]\s*([^\s]+)',
            r'sl no[.:]\s*([^\s]+)',
            r'sr no[.:]\s*([^\s]+)'
        ]
        
        for pattern in serial_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                case_data["listing_info"]["serial_number"] = matches[0]
                break
        
        # Store raw HTML for further processing
        case_data["raw_html"] = str(history_div)
        case_data["plain_text"] = history_div.get_text(strip=True)
        
        return case_data
    
    def wrap_text(self, text, width=80):
        """Wrap long text to specified width"""
        if not text:
            return ""
        wrapped_lines = textwrap.wrap(str(text), width=width)
        return '\n'.join(wrapped_lines)
    
    def create_case_pdf(self, case_data):
        """Create a professional PDF from case data with proper text wrapping"""
        try:
            if not case_data:
                return None
            
            # Generate filename
            cnr = case_data.get('cnr_number', 'unknown_case')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"case_{cnr}_{timestamp}.pdf"
            filepath = os.path.join(self.download_dir, filename)
            
            # Create PDF document with larger margins
            doc = SimpleDocTemplate(
                filepath, 
                pagesize=A4, 
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.4*inch,
                rightMargin=0.4*inch
            )
            styles = getSampleStyleSheet()
            
            # Custom styles with better formatting
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=20,
                alignment=1,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=11,
                spaceAfter=8,
                spaceBefore=12,
                textColor=colors.darkblue,
                fontName='Helvetica-Bold'
            )
            
            # Style for table content with word wrap
            table_style = ParagraphStyle(
                'TableStyle',
                parent=styles['Normal'],
                fontSize=8,
                leading=10,
                wordWrap='LTR',  # Enable word wrap
                fontName='Helvetica'
            )
            
            bold_table_style = ParagraphStyle(
                'BoldTableStyle',
                parent=table_style,
                fontName='Helvetica-Bold'
            )
            
            # Build story (content)
            story = []
            
            # Title
            title = Paragraph("eCourts India - Case Details", title_style)
            story.append(title)
            story.append(Spacer(1, 0.1*inch))
            
            # Case Information Section
            case_info_heading = Paragraph("Case Information", heading_style)
            story.append(case_info_heading)
            
            # CNR and Search Date
            story.append(Paragraph(f"<b>CNR Number:</b> {case_data.get('cnr_number', 'N/A')}", table_style))
            story.append(Paragraph(f"<b>Search Date:</b> {case_data.get('search_date', 'N/A')}", table_style))
            story.append(Spacer(1, 0.05*inch))
            
            # Case Details Table with proper text wrapping
            case_details = case_data.get('case_details', {})
            if case_details:
                details_heading = Paragraph("Case Details", heading_style)
                story.append(details_heading)
                
                # Create table data with wrapped text
                table_data = []
                
                # Header row
                header_row = [
                    Paragraph('<b>Field</b>', bold_table_style),
                    Paragraph('<b>Value</b>', bold_table_style)
                ]
                table_data.append(header_row)
                
                # Data rows with text wrapping
                for key, value in case_details.items():
                    if key and value:
                        # Clean and wrap the text
                        clean_key = re.sub(r'\s+', ' ', str(key)).strip()
                        clean_value = re.sub(r'\s+', ' ', str(value)).strip()
                        
                        # Wrap long values
                        wrapped_key = self.wrap_text(clean_key, 30)
                        wrapped_value = self.wrap_text(clean_value, 50)
                        
                        key_para = Paragraph(wrapped_key, table_style)
                        value_para = Paragraph(wrapped_value, table_style)
                        
                        table_data.append([key_para, value_para])
                
                if len(table_data) > 1:
                    # Create table with dynamic row heights
                    case_table = Table(
                        table_data, 
                        colWidths=[1.8*inch, 4.5*inch],
                        repeatRows=1
                    )
                    
                    # Table style with better formatting for wrapped text
                    case_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ]))
                    
                    story.append(case_table)
                    story.append(Spacer(1, 0.1*inch))
            
            # Listing Information with better formatting
            listing_info = case_data.get('listing_info', {})
            if listing_info and any(listing_info.values()):
                listing_heading = Paragraph("Hearing & Court Information", heading_style)
                story.append(listing_heading)
                
                listing_data = []
                listing_data.append([
                    Paragraph('<b>Information</b>', bold_table_style),
                    Paragraph('<b>Details</b>', bold_table_style)
                ])
                
                for key, value in listing_info.items():
                    if value:
                        formatted_key = key.replace('_', ' ').title()
                        wrapped_key = self.wrap_text(formatted_key, 25)
                        wrapped_value = self.wrap_text(value, 40)
                        
                        key_para = Paragraph(wrapped_key, table_style)
                        value_para = Paragraph(wrapped_value, table_style)
                        
                        listing_data.append([key_para, value_para])
                
                if len(listing_data) > 1:
                    listing_table = Table(
                        listing_data, 
                        colWidths=[2*inch, 4.3*inch],
                        repeatRows=1
                    )
                    listing_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ]))
                    story.append(listing_table)
                    story.append(Spacer(1, 0.1*inch))
            
            # Additional Notes
            notes_heading = Paragraph("Additional Information", heading_style)
            story.append(notes_heading)
            
            notes = [
                "• This document was automatically generated from eCourts India portal",
                f"• Generated on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}",
                "• For official purposes, please verify with the original court records",
                "• Document ID: " + case_data.get('cnr_number', 'N/A')
            ]
            
            for note in notes:
                story.append(Paragraph(note, table_style))
                story.append(Spacer(1, 0.02*inch))
            
            # Footer
            story.append(Spacer(1, 0.1*inch))
            footer = Paragraph(
                "<i>Confidential - Generated by eCourts Scraper System</i>",
                ParagraphStyle(
                    'FooterStyle',
                    parent=styles['Italic'],
                    fontSize=7,
                    textColor=colors.grey,
                    alignment=1
                )
            )
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            print(f"✓ PDF created successfully: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error creating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def check_case_listing(self, case_data, check_date):
        """Check if case is listed on specific date"""
        if not case_data:
            return False
        
        check_date_str = check_date.strftime("%d-%m-%Y")
        check_date_short = check_date.strftime("%d-%m")
        
        # Check in listing info
        next_hearing = case_data.get("listing_info", {}).get("next_hearing_date", "")
        if check_date_str in next_hearing or check_date_short in next_hearing:
            return True
        
        # Check in case details
        for key, value in case_data.get("case_details", {}).items():
            if "date" in key.lower() or "hearing" in key.lower():
                if check_date_str in value or check_date_short in value:
                    return True
        
        # Check in raw text
        raw_text = case_data.get("raw_html", "").lower()
        if check_date_str in raw_text or check_date_short in raw_text:
            return True
        
        return False
    
    def download_cause_list(self, state=None, district=None, court_complex=None, date=None):
        """Download cause list for a specific date"""
        try:
            # Navigate to cause list page
            cause_list_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index"
            self.driver.get(cause_list_url)
            time.sleep(3)
            
            if state and district and court_complex:
                # Automated cause list selection
                return self._automate_cause_list(state, district, court_complex, date)
            else:
                # Manual mode
                print("\n" + "="*60)
                print("CAUSE LIST DOWNLOAD - MANUAL MODE")
                print("="*60)
                print("Please manually select the cause list options in the browser.")
                print("After viewing the cause list, we will create a PDF from the page content.")
                print("Press Enter when you're ready to create PDF...")
                input()
                
                # Create PDF from the current page
                cause_list_data = {
                    "type": "cause_list",
                    "url": self.driver.current_url,
                    "title": "eCourts Cause List",
                    "content": self.driver.page_source
                }
                
                pdf_path = self.create_cause_list_pdf(cause_list_data)
                if pdf_path:
                    return {
                        "status": "success",
                        "pdf_path": pdf_path,
                        "message": "Cause list PDF created successfully"
                    }
                else:
                    return {
                        "status": "manual_mode",
                        "message": "Please manually save the cause list from the browser"
                    }
            
        except Exception as e:
            print(f"Error downloading cause list: {str(e)}")
            return None
    
    def create_cause_list_pdf(self, cause_list_data):
        """Create PDF from cause list page"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cause_list_{timestamp}.pdf"
            filepath = os.path.join(self.download_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1,
                textColor=colors.darkblue
            )
            
            title = Paragraph("eCourts India - Cause List", title_style)
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Basic info
            story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"<b>URL:</b> {cause_list_data.get('url', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Note
            note = Paragraph(
                "<i>Note: This is an automatically generated document from the eCourts portal. "
                "For official purposes, please refer to the original website.</i>",
                styles['Italic']
            )
            story.append(note)
            
            doc.build(story)
            print(f"✓ Cause list PDF created: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error creating cause list PDF: {str(e)}")
            return None
    
    def _automate_cause_list(self, state, district, court_complex, date=None):
        """Automate cause list form filling"""
        try:
            if not date:
                date = datetime.now().strftime("%d-%m-%Y")
            
            print(f"Automating cause list for: {state} → {district} → {court_complex} on {date}")
            
            # Select state
            state_select = Select(self.wait.until(
                EC.presence_of_element_located((By.ID, "state_code"))
            ))
            state_select.select_by_visible_text(state)
            time.sleep(2)
            
            # Select district
            district_select = Select(self.wait.until(
                EC.presence_of_element_located((By.ID, "dist_code"))
            ))
            district_select.select_by_visible_text(district)
            time.sleep(2)
            
            # Select court complex
            complex_select = Select(self.wait.until(
                EC.presence_of_element_located((By.ID, "court_complex_code"))
            ))
            complex_select.select_by_visible_text(court_complex)
            time.sleep(2)
            
            # Set date
            date_field = self.driver.find_element(By.ID, "search_date")
            date_field.clear()
            date_field.send_keys(date)
            
            # Submit form
            submit_btn = self.driver.find_element(By.ID, "submit1")
            submit_btn.click()
            time.sleep(5)
            
            print(f"✓ Cause list generated for {court_complex} on {date}")
            
            # Create PDF from the cause list page
            cause_list_data = {
                "type": "cause_list",
                "state": state,
                "district": district,
                "court_complex": court_complex,
                "date": date,
                "content": self.driver.page_source
            }
            
            pdf_path = self.create_cause_list_pdf(cause_list_data)
            
            return {
                "status": "success",
                "state": state,
                "district": district,
                "court_complex": court_complex,
                "date": date,
                "pdf_created": pdf_path is not None,
                "pdf_path": pdf_path
            }
            
        except Exception as e:
            print(f"Error automating cause list: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def close(self):
        """Close the browser"""
        try:
            self.driver.quit()
        except:
            pass

def save_to_file(data, filename):
    """Save data to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        if filename.endswith('.json'):
            json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            f.write(str(data))
    print(f"✓ Data saved to {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="eCourts Scraper - Fetch case details and generate PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check if case is listed today using CNR and generate PDF
  python ecourts_scraper.py --today MHAU030151912016
  
  # Check if case is listed tomorrow using CNR and generate PDF
  python ecourts_scraper.py --tomorrow MHAU030151912016
  
  # Check using case type, number, year and generate PDF
  python ecourts_scraper.py --today MHAU03 0151912 2016
  
  # Download cause list manually and generate PDF
  python ecourts_scraper.py --causelist
  
  # Download cause list automatically and generate PDF
  python ecourts_scraper.py --causelist --state "Maharashtra" --district "Mumbai" --court "City Civil Court"
        """
    )
    
    parser.add_argument(
        "--today", 
        action="store_true", 
        help="Check if case is listed today"
    )
    parser.add_argument(
        "--tomorrow", 
        action="store_true", 
        help="Check if case is listed tomorrow"
    )
    parser.add_argument(
        "--causelist", 
        action="store_true", 
        help="Download today's cause list and generate PDF"
    )
    parser.add_argument(
        "--state",
        help="State name for cause list (e.g., 'Maharashtra')"
    )
    parser.add_argument(
        "--district",
        help="District name for cause list (e.g., 'Mumbai')"
    )
    parser.add_argument(
        "--court",
        help="Court complex name for cause list"
    )
    parser.add_argument(
        "cnr_number", 
        nargs="?", 
        help="Full 16-digit CNR (e.g., MHAU030151912016) or case type (e.g., MHAU03)"
    )
    parser.add_argument(
        "number", 
        nargs="?", 
        help="Case number (if providing separate components)"
    )
    parser.add_argument(
        "year", 
        nargs="?", 
        help="Case year (if providing separate components)"
    )
    
    args = parser.parse_args()
    
    # Install required packages reminder
    print("Note: Make sure you have installed required packages:")
    print("pip install reportlab")
    
    # Cause list mode
    if args.causelist:
        scraper = ECourtsScraper()
        try:
            if args.state and args.district and args.court:
                result = scraper.download_cause_list(args.state, args.district, args.court)
            else:
                result = scraper.download_cause_list()
            
            if result:
                save_to_file(result, "cause_list_result.json")
        finally:
            print("\nPress Enter to close browser...")
            input()
            scraper.close()
        return
    
    # Case search mode
    scraper = ECourtsScraper()
    try:
        case_data = None
        
        # Determine input format and fetch case
        if args.cnr_number and len(args.cnr_number) == 16 and not args.number:
            # Full CNR provided
            cnr_full = args.cnr_number
            case_data = scraper.fetch_case_by_cnr(cnr_full)
        elif args.cnr_number and args.number and args.year:
            # Separate components provided
            case_data = scraper.fetch_case_by_details(args.cnr_number, args.number, args.year)
        else:
            print("Error: Please provide either:")
            print("  1. Full 16-digit CNR: MHAU030151912016")
            print("  2. Separate components: MHAU03 0151912 2016")
            parser.print_help()
            return
        
        # Process results
        if case_data:
            print("\n" + "="*50)
            print("CASE DETAILS")
            print("="*50)
            
            # Display case information
            for key, value in case_data.get("case_details", {}).items():
                print(f"{key}: {value}")
            
            # Determine check date
            check_date = None
            date_label = ""
            if args.today:
                check_date = datetime.now().date()
                date_label = "today"
            elif args.tomorrow:
                check_date = (datetime.now() + timedelta(days=1)).date()
                date_label = "tomorrow"
            
            # Check if listed on specific date
            if check_date:
                is_listed = scraper.check_case_listing(case_data, check_date)
                
                print("\n" + "="*50)
                print(f"LISTING CHECK FOR {date_label.upper()} ({check_date})")
                print("="*50)
                
                if is_listed:
                    print(f"✓ Case IS listed {date_label}")
                    
                    # Extract serial number and court name
                    listing_info = case_data.get("listing_info", {})
                    serial = listing_info.get("serial_number", "N/A")
                    court = listing_info.get("court", "N/A")
                    
                    print(f"Serial Number: {serial}")
                    print(f"Court Name: {court}")
                    print(f"Next Hearing: {listing_info.get('next_hearing_date', 'N/A')}")
                else:
                    print(f"✗ Case is NOT listed {date_label}")
            
            # PDF creation status
            pdf_created = case_data.get("pdf_created", False)
            if pdf_created:
                pdf_path = case_data.get("pdf_path", "")
                print(f"✓ PDF Created: {pdf_path}")
            else:
                print("✗ PDF creation failed")
            
            # Save results
            cnr = case_data.get('cnr_number', 'case')
            filename = f"case_{cnr}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_to_file(case_data, filename)
            
        else:
            print("✗ Failed to fetch case details")
    
    finally:
        print("\nPress Enter to close browser...")
        input()
        scraper.close()

if __name__ == "__main__":
    main()