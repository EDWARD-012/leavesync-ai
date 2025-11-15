# 📌 **LeaveSync-AI – Online Leave Management System**

LeaveSync-AI is a modern web-based Leave Management System designed to automate leave requests, approvals, notifications, and holiday planning.  
It supports role-based dashboards for Employees, Managers, and Admins, along with smart AI leave recommendations.

## 🚀 Features

- 🔐 User Registration & Login  
- 👤 Role-Based Dashboards (Employee / Manager / Admin)  
- 📝 Apply for Leave (Date Range + Reason)  
- 📜 Leave History (Approved / Rejected / Pending)  
- ✔️ Manager/HR Approval Workflow  
- 📅 Holiday Calendar Integration  
- 🤖 AI-Based Smart Leave Recommendations  
- 📧 Email & In-App Notifications  
- 📊 Leave Analytics Dashboard for HR  
- 🔄 Real-Time Leave Balance Updates  
- 🧩 Modular Backend Architecture

## 🛠️ Tech Stack

**Backend:** Python  
**Frontend:** HTML, JavaScript, CSS  
**Database:** MySQL / PostgreSQL / SQLite  
**Deployment:** Vercel / Cloud Hosting  
**License:** MIT License

## 📂 Project Structure

```
leavesync-ai/
│
├── api/                   # API routes & backend logic
├── core/                  # Core application modules
├── leavesync_backend/     # Main backend application
├── templates/             # Frontend HTML templates
├── vercel.json            # Deployment configuration
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/EDWARD-012/leavesync-ai
cd leavesync-ai
```

### 2️⃣ Create and activate a virtual environment
**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables  
Create a `.env` file in the root folder and include:
```
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
EMAIL_HOST=your_email_smtp
EMAIL_USER=your_email
EMAIL_PASSWORD=your_password
HOLIDAY_API_KEY=optional
```

### 5️⃣ Run migrations
```bash
python manage.py migrate
```

### 6️⃣ Create admin user
```bash
python manage.py createsuperuser
```

### 7️⃣ Start the development server
```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000/

## 🚀 Deployment Guide (Vercel)

1. Ensure `vercel.json` is configured correctly  
2. Add environment variables in the Vercel dashboard  
3. Connect the GitHub repository to Vercel  
4. Deploy from the main branch  
5. Verify live deployment

## 🤝 Contributing

Contributions are welcome!  
Submit pull requests for bug fixes, features, documentation, etc.

## 📄 License

This project is licensed under the **MIT License**.

## 📬 Contact

Developer: Ravi Kumar Gupta  
GitHub: https://github.com/EDWARD-012  
