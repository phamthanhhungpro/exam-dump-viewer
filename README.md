# Multi-Exam Practice Quiz Application

A comprehensive web-based quiz application supporting multiple AWS certification exams. Built with Express.js, EJS templating, and modern responsive design with dynamic routing and configuration-based exam management.

## 🚀 Features

### 📚 Multi-Exam Support
- **Dynamic Exam Types**: Configure multiple exam types via JSON
- **Separate Data Storage**: Each exam type has its own questions, scores, and bookmarks
- **Dynamic Routing**: Clean URLs like `/sap`, `/saa` for different exam types
- **Centralized Configuration**: Easy to add new exam types through config file

### 🎯 Current Supported Exams
- **SAP-C02**: AWS Solutions Architect Professional
- **SAA-C03**: AWS Solutions Architect Associate
- **Extensible**: Easy to add more exam types

### 👤 User Management (Per Exam Type)
- **Individual User Accounts**: Track progress separately for each exam type
- **Persistent Login**: Username stored in localStorage
- **Exam-Specific Data**: Each user has separate starred questions and scores per exam

### ⭐ Question Bookmarking (Exam-Specific)
- **Star Questions**: Bookmark important questions per exam type
- **User-Specific Bookmarks**: Each user maintains separate starred questions for each exam
- **Dedicated Starred Page**: Review bookmarked questions per exam type

### 📊 Score Tracking & Analytics (Per Exam)
- **Comprehensive Scoring**: Track score, percentage, time spent per exam type
- **Separate Score History**: View attempts history for each exam type
- **Best Score Tracking**: System remembers highest score for each exam set per exam type

### 🎨 Smart Visual Indicators
- **Color-Coded Status**:
  - 🔵 **Blue**: Exam not attempted yet
  - 🔴 **Red**: Attempted but not perfect score
  - 🟢 **Green**: Perfect score (100%)
- **Dynamic Exam Colors**: Each exam type can have its own color scheme

## 🛠️ Technical Stack

- **Backend**: Node.js with Express.js
- **Frontend**: EJS templating engine
- **Styling**: TailwindCSS for responsive design
- **Data Storage**: JSON file-based storage (organized by exam type)
- **Configuration**: JSON-based exam configuration
- **PDF Processing**: Python script with pdfplumber for question extraction

## 📁 Project Structure

```
quizzz/
├── server.js              # Main Express server with multi-exam routing
├── package.json           # Node.js dependencies
├── config/
│   └── exams.json         # Exam configuration file
├── data/
│   ├── sap/               # SAP-C02 exam data
│   │   ├── questions.json
│   │   ├── starred.json
│   │   └── scores.json
│   └── saa/               # SAA-C03 exam data
│       ├── questions.json
│       ├── starred.json
│       └── scores.json
├── views/
│   ├── home.ejs          # Homepage with exam selection
│   ├── index.ejs         # Exam-specific homepage
│   ├── quiz.ejs          # Quiz interface
│   └── scores.ejs        # Score history page
├── public/               # Static assets
└── scripts/
    └── final_parser.py   # PDF question parser
```

## 🚀 Getting Started

### Prerequisites
- Node.js (version 14 or higher)
- Python 3 (for PDF parsing)

### Installation

1. **Clone or download the project**
   ```bash
   cd quizzz
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install express ejs
   ```

3. **Install Python dependencies (for PDF parsing)**
   ```bash
   pip install pdfplumber
   ```

### Running the Application

1. **Start the server**
   ```bash
   node server.js
   ```

2. **Open your browser**
   Navigate to `http://localhost:4000`

3. **Choose your exam type**
   - Go to `http://localhost:4000/sap` for AWS SAP-C02
   - Go to `http://localhost:4000/saa` for AWS SAA-C03

## � Adding New Exam Types

### 1. Update Configuration

Edit `config/exams.json`:
```json
{
  "exams": {
    "dva": {
      "id": "dva",
      "name": "AWS Developer Associate",
      "code": "DVA-C01",
      "description": "AWS Developer Associate Certification",
      "icon": "💻",
      "color": {
        "primary": "purple",
        "gradient": "from-purple-500 to-purple-600"
      },
      "questionsPerExam": 20,
      "dataFiles": {
        "questions": "data/dva/questions.json",
        "starred": "data/dva/starred.json",
        "scores": "data/dva/scores.json"
      }
    }
  },
  "settings": {
    "enabledExams": ["sap", "saa", "dva"]
  }
}
```

### 2. Create Data Directory

```bash
mkdir data/dva
echo "[]" > data/dva/questions.json
echo "[]" > data/dva/starred.json
echo "[]" > data/dva/scores.json
```

### 3. Add Questions

Use the PDF parser or manually add questions to the questions.json file.

### 4. Restart Server

The new exam type will be automatically available at `/dva`

## 🎯 API Endpoints

### Homepage
- `GET /` - Main homepage with all exam types
- `GET /:examType` - Exam-specific homepage

### Quiz Management
- `GET /:examType/quiz/:id` - Take specific exam set
- `GET /:examType/starred?username=:username` - View starred questions

### User Management
- `GET /:examType/scores/:username` - Get user's score history for exam type
- `POST /:examType/save-score` - Save quiz results for exam type
- `GET /:examType/starred/:username/count` - Get user's starred question count

### Question Bookmarking
- `POST /:examType/star` - Toggle question bookmark for exam type
- `POST /:examType/unstar` - Remove question bookmark for exam type

## 📊 Configuration Format

### Exam Configuration (`config/exams.json`)
```json
{
  "exams": {
    "examId": {
      "id": "examId",
      "name": "Display Name",
      "code": "Exam Code",
      "description": "Description",
      "icon": "📚",
      "color": {
        "primary": "blue",
        "gradient": "from-blue-500 to-blue-600"
      },
      "questionsPerExam": 20,
      "dataFiles": {
        "questions": "data/examId/questions.json",
        "starred": "data/examId/starred.json",
        "scores": "data/examId/scores.json"
      }
    }
  },
  "settings": {
    "defaultExam": "sap",
    "enabledExams": ["sap", "saa"],
    "appTitle": "AWS Practice Quiz",
    "appDescription": "Multi-exam practice platform"
  }
}
```

## 🌐 URL Structure

- `/` - Homepage with exam selection
- `/:examType` - Exam-specific homepage
- `/:examType/quiz/:id` - Take quiz
- `/:examType/starred` - View starred questions
- `/:examType/scores` - View score history

## 🎨 Customization

### Adding New Color Schemes
Update the exam configuration with new Tailwind color classes:
```json
"color": {
  "primary": "emerald",
  "gradient": "from-emerald-500 to-emerald-600"
}
```

### Changing Questions Per Exam
Modify the `questionsPerExam` value in the exam configuration.

## 🔒 Security Notes

- Local development application
- Username-only authentication
- File-based data storage
- Each exam type has isolated data

## 🤝 Contributing

Contribute by:
- Adding new exam types and questions
- Improving UI/UX
- Adding new features
- Bug fixes and optimizations

## 📝 License

Educational use only. Ensure proper rights to exam materials.

---

**Multi-Exam Support! 🚀 Practice for multiple AWS certifications in one place! 🎯**
