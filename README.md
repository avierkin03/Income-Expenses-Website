# SpendWise 💸

**SpendWise** is a Django-based web application for tracking personal **income and expenses**, designed to give users full control over their finances through analytics, visualization, and a clean user experience.

---

## 🚀 Features

### 🔐 Authentication & Security
- User registration with **email confirmation**
- Password reset via **email verification**
- Secure authentication system
- Each user can access **only their own data**

---

### ⚡ Real-time UX (AJAX)
- **Instant form validation** (email, password, etc.)
- Real-time error and success messages
- **Live search** without page reloads

---

### 💰 Income & Expense Management
- Create, edit, and delete **income and expense records**
- Separate sections for **Income** and **Expenses**
- Categorization for better analysis
- Each record includes:
  - Amount
  - Category
  - Descriptionекм 
  - Date

---

### 🔍 Advanced Live Search
Search works instantly and supports:
- Amount
- Description
- Category
- Date
- **Partial matches**
- **Case-insensitive search**
- Matching even with **incomplete input**

---

### 📊 Analytics & Statistics
Dedicated analytics pages for **Income** and **Expenses** including:
- Total amount
- Daily average
- Monthly average
- Number of transactions
- Top income / expense category

Implemented **export** of income and expense data in **PDF, CSV, XLSX format**.

---

### 📈 Data Visualization (Chart.js)
- Interactive charts powered by **Chart.js**
- User can choose chart type:
  - Doughnut
  - Pie
  - Bar
- Flexible period selection:
  - Last month
  - Last 6 months
  - Last year
  - All time
  - **Custom date range**

---

### 🌍 Currency & Theme
- User can choose a **preferred currency**
- Full **Dark / Light mode** support
- Theme preference is persisted across sessions

---

## 🛠 Tech Stack

- **Backend:** Django
- **Frontend:** HTML, CSS, Bootstrap 5
- **JavaScript:** Vanilla JS, AJAX
- **Charts:** Chart.js
- **Database:** PostgreSQL
- **Authentication:** Django auth + email verification

---

## 📷 Screenshots
| Login Page | User Preferences Page |
|-------------|--------------|
| ![Login Page](screenshots\login_page.jpg) | ![User Preferences Page](screenshots\user_preferences.jpg) |

| Income Page | Expenses Page |
|-------------|--------------|
| ![Income Page](screenshots\income_page.jpg) | ![Expenses Page](screenshots\expenses_page.jpg) |


| Add Income Page | Add Expenses Page |
|-------------|--------------|
| ![Add Income Page](screenshots\income_stats_page.png) | ![Add Expenses Page](screenshots\expenses_stats_page.png) |

| Income Stats Page | Expenses Stats Page |
|-------------|--------------|
| ![Income Stats Page](screenshots\add_income_page.jpg) | ![Expenses Stats Page](screenshots\add_expenses_page.jpg) |