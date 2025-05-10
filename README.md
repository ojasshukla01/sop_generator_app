# 📝 SOP Generator App

Welcome to the SOP Generator App – a streamlined backend service designed to dynamically generate customized Statements of Purpose (SOPs) based on user input.

This project is maintained by [Ojas Shukla](https://github.com/ojasshukla01), a Data Engineer with expertise in Python, FastAPI, and cloud-native systems.

---

## 🚀 Features

- 🔐 **User Authentication** – Secure sign-up and login functionality
- 📄 **SOP Generation Engine** – Tailors output using templates and inputs
- 🗃️ **User Profile Management** – Save and manage personal academic/career data
- 🔄 **API Integration** – Optimized RESTful endpoints using FastAPI
- 🛠️ **Configurable Templates** – Support for editing and storing multiple SOP formats
- 🧠 **AI/LLM-ready Architecture** – Pluggable structure for LLM integration (coming soon)

---

## 🧰 Tech Stack

| Layer        | Technology         |
|--------------|--------------------|
| Backend      | Python, FastAPI     |
| Database     | SQLAlchemy, Alembic |
| Auth         | JWT-based security  |
| Deployment   | Docker-ready        |
| Others       | Pydantic, Uvicorn   |

---

## 📁 Project Structure

```
sop_generator_app/
│
├── api/                 # FastAPI route handlers
│   └── routes/
├── auth/                # JWT Authentication utils
├── config/              # App configuration settings
├── database/            # Database models and session manager
├── migrations/          # Alembic DB migrations
├── templates/           # SOP template HTMLs or Jinja files
├── utils/               # Helper functions
├── main.py              # FastAPI entrypoint
└── requirements.txt     # Python dependencies
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ojasshukla01/sop_generator_app.git
cd sop_generator_app
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
alembic upgrade head
```

### 5. Run the App

```bash
uvicorn main:app --reload
```

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API docs.

---

## 🧪 Example API Usage

### POST `/generate-sop`

**Request JSON:**
```json
{
  "name": "John Doe",
  "program": "Master of Data Science",
  "university": "University of Melbourne",
  "goals": "Contribute to data-driven healthcare"
}
```

**Response:**
```json
{
  "sop_text": "Dear Admission Committee, My name is John Doe..."
}
```

---

## 👤 About the Author

**Ojas Shukla**  
Data Engineer | Cloud-Native Enthusiast | FastAPI Specialist  
[LinkedIn](https://linkedin.com/in/ojasshukla01) · [GitHub](https://github.com/ojasshukla01)

---


## 📌 Future Enhancements

- Integration with GPT-based LLMs for SOP drafting
- Export SOPs in PDF/Docx format
- Frontend UI built with React + TailwindCSS
- Cloud deployment with CI/CD
