# Douane-Illicit-Product-Detector

🛡️ **Intelligent multi-agent system built with CrewAI to monitor e-commerce platforms and combat digital fraud.** It automatically scrapes, analyzes, and scores product listings to detect and prioritize illicit goods for efficient targeting by Tunisian Customs agents.

## Demo

![Demo GIF](Douane_demo_.gif)

*Demo showing the system in action - automated product analysis, suspicion scoring, and WHOIS domain lookup.*

## Developed by

**Montassar Bellah Abdallah**

---

## 🚀 Overview

The Douane-Illicit-Product-Detector is a sophisticated AI-powered system designed to help Tunisian Customs authorities identify potentially illicit products being sold on e-commerce platforms. The system uses a multi-agent architecture to automate the detection process, providing real-time analysis and scoring of suspicious product listings.

### Key Capabilities

- **Automated Detection**: Continuously monitors e-commerce platforms for suspicious product listings
- **Intelligent Scoring**: Uses AI to analyze products and assign suspicion scores (0-100)
- **WHOIS Analysis**: Performs domain registration analysis to identify potentially fraudulent sellers
- **Real-time Dashboard**: Web-based interface for customs agents to review and act on findings
- **PDF Reporting**: Generates comprehensive reports for documentation and analysis

## 🏗️ System Architecture

The system employs a **multi-agent architecture** using CrewAI, with three specialized agents working in sequence:

### 1. Queries Agent (`queries_agent/`)
- **Role**: Generates optimized search queries for product categories
- **Function**: Analyzes product categories and creates targeted search strategies
- **Output**: List of search queries and platform recommendations

### 2. Search Agent (`search_agent/`)
- **Role**: Performs web searches using Serper API
- **Function**: Searches for product listings across e-commerce platforms
- **Output**: Ranked list of potential product listings with initial scoring

### 3. Web Scraping Agent (`web_scraping_agent/`)
- **Role**: Extracts detailed product information
- **Function**: Scrapes product pages using Crawl4AI and ScrapFly
- **Output**: Complete product analysis with suspicion reasons and WHOIS data



## 🛠️ Technical Stack

### Core Technologies
- **CrewAI**: Multi-agent orchestration framework
- **Streamlit**: Web dashboard and user interface
- **Google Gemini**: AI model for analysis and scoring
- **Python 3.10+**: Primary programming language

### Key Libraries
- **crawl4ai**: web scraping 
- **python-whois**: Domain registration analysis
- **reportlab**: PDF report generation
- **agentops**: Agent performance monitoring
- **requests**: HTTP client for API integrations

### APIs & Services
- **Google Gemini API**: AI model for product analysis
- **Serper API**: Google search integration
- **AgentOps**: Agent performance tracking

## 🎯 Usage

### Starting an Analysis

1. **Access the Dashboard**: Open the provided URL in your web browser
2. **Configure Parameters**:
   - Enter the product category to analyze (e.g., "produits électroniques")
   - Optionally exclude specific platforms
3. **Start Analysis**: Click "Démarrer l'Analyse 🚀"

### Dashboard Features

#### Main Analysis Interface
- **Product Category Input**: Specify what type of products to monitor
- **Platform Exclusion**: Filter out specific e-commerce platforms
- **Real-time Progress**: Monitor the analysis progress
- **Results Display**: View detected products with suspicion scores

#### Product Analysis Results
- **Suspicion Score**: 0-100 scale indicating likelihood of illicit activity
- **Product Information**: Title, price, images, and seller details
- **Suspicion Reasons**: AI-generated explanations for the score
- **WHOIS Data**: Domain registration information for seller verification

#### WHOIS Lookup Tool
- **Domain Search**: Enter any domain name for investigation
- **Registration Details**: View owner, registrar, and registration dates
- **PDF Export**: Download WHOIS information as PDF

### Analysis Process

1. **Query Generation**: The system creates optimized search queries
2. **Web Search**: Searches e-commerce platforms for relevant listings
3. **Product Scraping**: Extracts detailed information from product pages
4. **Analysis & Scoring**: AI analyzes products and assigns suspicion scores
5. **Results Presentation**: Displays findings in the dashboard with PDF export options

## 📄 License

This project is developed by Montassar Bellah Abdallah for educational and research purposes in combating digital fraud.
