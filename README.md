# 🩺 MedSafe Backend

**MedSafe** is a backend system designed to support a medication information and adherence management service tailored for young adults. This project was developed as part of the **Google Solution Challenge 2025** and provides automated drug information lookup, prescription tracking, and medication reminder features through a RESTful API.

---

## ✅ Project Purpose

Medication adherence among young adults is often low due to limited health awareness and lack of intuitive tools. **MedSafe** addresses this issue by offering a user-friendly platform that encourages consistent medication habits with minimal user friction.

---

## ⚙️ Key Features

- **Automatic Drug Information Lookup**  
  When users scan medication names or item codes via OCR, the system queries the Korean public API “e약은요” to automatically fetch detailed data such as efficacy, usage instructions, warnings, interactions, and side effects.

- **Prescription Upload and Management**  
  Users can upload prescription images. The server handles image storage via Google Cloud Storage and processes them for record keeping.

- **Calendar-Based Medication Logging and Reminders**  
  Users can track their medication intake history and attach notes/reminders on a personal calendar.

- **Conversational Medication Info Assistant**  
  A chatbot-style interface allows users to ask about medication information using natural language.

---

## 🛠️ Tech Stack

- **Framework**: Django (with Django REST Framework)  
- **Database**: PostgreSQL  
- **Deployment**: Google Cloud Run, Docker  
- **Others**: Celery, Upstash Redis, Google Cloud Storage, Task Queue

---

## 📁 Project Structure

```
medsafe-backend/
├── chat/                 # Chatbot logic
├── core/                 # Common utilities and cloud storage logic
├── prescriptions/        # Prescription & drug model and views
├── calendar/             # Medication schedule and memos
├── manage.py             # Django entry point
├── requirements.txt      # Python dependencies
├── Dockerfile, Procfile  # Deployment settings
```

---

## 🚀 Local Development Setup

```bash
git clone https://github.com/funrace2/medsafe-backend.git
cd medsafe-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Sample API Endpoints

- `POST /api/prescriptions/`  
  Upload prescription image and data (requires authentication)

- `GET /api/chat/medications/?query=headache`  
  Query chatbot for medication information

- `GET /api/calendar/memos/`  
  Retrieve user-specific medication memos

---

## ☁️ Deployment Info

This backend is deployed on **Google Cloud Run** with asynchronous background jobs handled by **Celery** and **Upstash Redis**.

---

## 📣 References

- Drug data provided by: [DrbEasyDrugInfoService - Data.go.kr](http://apis.data.go.kr/1471000/DrbEasyDrugInfoService)
- Authentication and storage are implemented with user privacy and data security in mind.

---

## 🙋 Contributors & Contact

- Backend Developer: Hyeonmo Koo  
- Contact: [GitHub Issues](https://github.com/funrace2/medsafe-backend/issues)

---

This README is intended to help **Google Solution Challenge judges** quickly understand the **technical and social value** of the MedSafe project.