# Daily Quote Generator

![Daily Quote](public/daily_quote.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.10-blue)
[![Docker](https://img.shields.io/badge/Docker-Available-green.svg)](https://www.docker.com/)
![Build Status](https://img.shields.io/github/actions/workflow/status/hipnologo/daily_quote/daily-quote.yml?branch=main)
![Last Commit](https://img.shields.io/github/last-commit/hipnologo/daily_quote)
![Code Size](https://img.shields.io/github/languages/code-size/hipnologo/daily_quote)
![Issues](https://img.shields.io/github/issues/hipnologo/daily_quote)
![Forks](https://img.shields.io/github/forks/hipnologo/daily_quote)
![Stars](https://img.shields.io/github/stars/hipnologo/daily_quote)

The **Daily Quote Generator** is a Python-based automation tool that fetches a random inspirational quote daily from a public API and commits it to this repository. This project showcases automation, API integration, sentiment analysis, and containerization using Docker.

## Technologies Used

![Python](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub](https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![HTML](https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![Shell](https://img.shields.io/badge/shell_script-121011?style=for-the-badge&logo=gnu-bash&logoColor=white)

## Table of Contents

- [Daily Quote Generator](#daily-quote-generator)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Screenshot](#screenshot)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Automated Quote Fetching:** Retrieves a new inspirational quote daily from the [API Ninjas Quotes API](https://api-ninjas.com/api/quotes).
- **Multi-language Support:** Translates quotes into Spanish and Portuguese using the [MyMemory Translation API](https://mymemory.translated.net/doc/spec.php).
- **Sentiment Analysis:** Analyzes the sentiment of each quote using NLTK's VADER and visualizes the results with t-SNE.
- **Version Control Integration:** Commits and pushes new quotes to the repository automatically.
- **Dockerized Setup:** Easily build and run the application in a Docker container.
- **Logging:** Comprehensive logging for monitoring and troubleshooting.

## Screenshot

![Daily Quote](public/daily_quote.png)

## Getting Started

Follow these instructions to set up and run the Daily Quote Generator on your local machine.

### Prerequisites

- **Python:** Version 3.8 or higher. [Download Python](https://www.python.org/downloads/)
- **Git:** For version control. [Download Git](https://git-scm.com/downloads)
- **Docker:** (Optional) For containerization. [Download Docker](https://www.docker.com/get-started)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/hipnologo/daily_quote.git
   ```
2. **Navigate to the project directory:**
   ```
   cd daily_quote
   ```
3. **Install Python Dependencies:**
   It's recommended to use a virtual environment.
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Install NLTK Data:
   The script uses NLTK's VADER for sentiment analysis.
   ```
   python -c "import nltk; nltk.download('vader_lexicon')"
   ```

### Usage

Run the script manually to generate and commit a new quote:
```
python daily_quote.py
```

To automate the execution, schedule the script using cron jobs (Linux/macOS) or Task Scheduler (Windows).

## Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for more details.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

<a href="https://www.buymeacoffee.com/hipnologod" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>


<p align="center"> <a href="https://github.com/hipnologo/daily_quote/issues">Report Bug</a> • <a href="https://github.com/hipnologo/daily_quote/issues">Request Feature</a> </p> ```
