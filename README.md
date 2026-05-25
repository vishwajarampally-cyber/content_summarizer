# AI Content Summarizer

A production-ready Python application for summarizing long text, PDF files, and article URLs using Grok. Summaries are stored in MongoDB along with usage metadata and statistics.

## Features

- Paste or paste long text for summarization
- Upload and summarize PDF content
- Summarize article pages from URLs
- Support for multiple summary styles:
  - Short Summary
  - Detailed Summary
  - Bullet Point Summary
  - Key Insights
  - Beginner Friendly Explanation
- Advanced prompt engineering for technical, academic, business, and general content
- MongoDB history storage with timestamps
- Word count and reading time analysis
- Robust error handling and environment configuration

## Installation

1. Clone or copy the project folder.
2. Create and activate a Python virtual environment.

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file at the project root with the following values:

```env
GROK_API_KEY=your_grok_api_key
MONGODB_URL=your_mongodb_connection_url
```

Alternatively, copy `.env.example` and update values.

## MongoDB Setup

1. Create a MongoDB Atlas cluster or use an existing MongoDB connection.
2. Set `MONGODB_URL` to your connection string, for example:

```env
MONGODB_URL=mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority
```

## Grok API Setup

1. Create a Grok or OpenAI API key.
2. Save the key as `GROK_API_KEY` in your `.env` file.
3. Make sure the key has access to the `grok-1.5` model.

## Running the Application

Run the app from the project root:

```bash
python main.py
```

Follow the prompts to enter text, provide a PDF file path, or enter an article URL.

## Project Structure

```text
project/
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
├── .gitignore
├── database/
│   └── mongodb.py
├── models/
│   └── summary_model.py
├── services/
│   ├── grok_service.py
│   └── summary_service.py
└── utils/
    ├── pdf_handler.py
    ├── prompts.py
    ├── summarizer.py
    ├── text_cleaner.py
    └── url_extractor.py
```

## Notes

- Keep `.env` private and never commit secrets to source control.
- Use only `GROK_API_KEY` and `MONGODB_URL`.
- The application validates input and handles common errors such as invalid URLs, missing API keys, and PDF extraction issues.
