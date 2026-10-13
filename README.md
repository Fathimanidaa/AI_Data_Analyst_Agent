# AI Data Analyst Agent

🚀 Live Demo:" https://ai-data-analyst-agent-l68y.onrender.com "

An interactive data analysis application built with Python, Streamlit, and AI. It helps users explore CSV datasets, understand data quality, perform basic analysis, create visualizations, and ask questions in natural language.


## Features

* **CSV Upload:** Upload a dataset in CSV format.
* **Dataset Overview:** View dataset dimensions and preview records.
* **Data Profiling:** Inspect column information, missing values, and duplicate rows.
* **Numerical Analysis:** Generate descriptive statistics for numerical columns.
* **Interactive Visualizations:** Explore data using charts.
* **Data Cleaning:** Remove duplicates, handle missing values, and perform supported cleaning operations.
* **Quick Data Questions:** Ask basic questions about the uploaded dataset.
* **AI Data Analyst Agent:** Uses an AI model to select an appropriate analysis tool and explain the calculated results.
* **Download Options:** Download supported analysis outputs.

## Technologies Used

* Python
* Streamlit
* Pandas
* Gradio Client
* Publicly hosted Qwen AI model through a Gradio API

## Project Structure

```text
AI_Data_Analyst_Agent/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── services/
│   ├── llm_service.py
│   ├── agent_service.py
│   └── data_tools.py
├── utils/
├── styles/
├── tests/
└── data/
```

## Run Locally

### 1. Clone the repository

Replace the example URL with your GitHub repository URL.

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI_Data_Analyst_Agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

The application will display a local URL in the terminal. Open that URL in your browser.

## AI Integration

The application connects to a publicly hosted AI model using `gradio_client`. The model helps interpret questions, select analysis tools, and explain calculated results.

The model runs on an external service, so its availability, response speed, and usage limits may vary. This project does not require downloading a large AI model locally.

## Privacy Note

Questions and information sent to the hosted AI service leave your local environment. Avoid uploading confidential, sensitive, or personally identifiable data.

## Future Improvements

* More advanced analysis tools
* Additional interactive visualizations
* Improved AI error handling
* Downloadable analysis reports

## Author

Developed as a Python and AI-powered data analytics portfolio project.
