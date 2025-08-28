# SAP Practice Quiz Application

A comprehensive web-based quiz application designed for AWS Solutions Architect Professional (SAP-C02) exam preparation. Built with Express.js, EJS templating, and modern responsive design.

## 🚀 Features

### 📚 Quiz Management
- **Multiple Exam Sets**: Automatically divides questions into sets of 20 questions each
- **Question Types**: Supports both single-choice and multiple-choice questions
- **Smart Question Parsing**: Advanced PDF parser to extract questions from ExamTopics materials
- **Progress Tracking**: Auto-save quiz progress in localStorage

### 👤 User Management
- **Individual User Accounts**: Track progress and scores per user
- **Persistent Login**: Username stored in localStorage for convenience
- **User-Specific Data**: Each user has their own starred questions and score history

### ⭐ Question Bookmarking
- **Star Questions**: Bookmark important or difficult questions
- **User-Specific Bookmarks**: Each user maintains their own starred questions list
- **Dedicated Starred Page**: Review all bookmarked questions in one place
- **Quick Toggle**: Easy star/unstar functionality during quiz

### 📊 Score Tracking & Analytics
- **Comprehensive Scoring**: Track score, percentage, time spent, and timestamp
- **Score History**: View all previous attempts with detailed statistics
- **Best Score Tracking**: System remembers highest score for each exam
- **Performance Analytics**: Visual indicators for exam completion status

### 🎨 Smart Visual Indicators
- **Color-Coded Status**:
  - 🔵 **Blue**: Exam not attempted yet
  - 🔴 **Red**: Attempted but not perfect score
  - 🟢 **Green**: Perfect score (100%)
- **Progress Badges**: Display percentage scores on completed exams
- **Achievement Icons**: Special icons for different completion states

### 📱 Responsive Design
- **Mobile-First**: Optimized for all device sizes
- **Touch-Friendly**: Large buttons and intuitive touch interactions
- **Modern UI**: Beautiful gradient backgrounds and smooth animations
- **Accessibility**: Clear typography and color contrast

## 🛠️ Technical Stack

- **Backend**: Node.js with Express.js
- **Frontend**: EJS templating engine
- **Styling**: TailwindCSS for responsive design
- **Data Storage**: JSON file-based storage
- **PDF Processing**: Python script with pdfplumber for question extraction

## 📁 Project Structure

```
quizzz/
├── server.js              # Main Express server
├── package.json           # Node.js dependencies
├── data/
│   ├── questions.json     # Quiz questions database
│   ├── starred.json       # User bookmarked questions
│   └── scores.json        # User score history
├── views/
│   ├── index.ejs         # Homepage with exam selection
│   ├── quiz.ejs          # Quiz interface
│   └── scores.ejs        # Score history page
├── public/               # Static assets (if any)
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

3. **Create a user account**
   - Click on the login section
   - Enter your username
   - Start taking quizzes!

## 📖 Usage Guide

### Taking a Quiz
1. **Login**: Enter your username on the homepage
2. **Select Exam**: Choose from available exam sets (20 questions each)
3. **Answer Questions**: Click on options to select answers
4. **Bookmark**: Use the star (⭐) button to bookmark important questions
5. **Submit**: Complete the quiz to see your score and save progress

### Viewing Starred Questions
1. Click on "Câu hỏi đã đánh dấu" (Starred Questions) card
2. Review all your bookmarked questions
3. Remove stars by clicking the "Bỏ đánh dấu" button

### Checking Score History
1. Click on "Lịch sử điểm" (Score History) card
2. View all your previous attempts
3. See detailed statistics and performance trends

## 🔧 Adding New Questions

### Using the PDF Parser

1. **Place your PDF file** in the scripts directory
2. **Run the parser**:
   ```bash
   cd scripts
   python final_parser.py your_exam_file.pdf
   ```
3. **The parser will generate** a JSON file with extracted questions
4. **Copy the questions** to `data/questions.json`
5. **Restart the server** to load new questions

### Manual Addition

Edit `data/questions.json` directly:
```json
{
  "question": "Your question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": 0,
  "is_multiple_choice": false,
  "source": {
    "correct_answer": "A",
    "community_answer": "A",
    "community_confidence": "high"
  }
}
```

## 🎯 API Endpoints

### Quiz Management
- `GET /` - Homepage with exam selection
- `GET /quiz/:id` - Take specific exam
- `GET /starred?username=:username` - View starred questions

### User Management
- `GET /scores/:username` - Get user's score history
- `POST /save-score` - Save quiz results
- `GET /starred/:username/count` - Get user's starred question count

### Question Bookmarking
- `POST /star` - Toggle question bookmark
- `POST /unstar` - Remove question bookmark

## 🎨 Customization

### Changing Questions Per Exam
Edit the `perTest` variable in `server.js`:
```javascript
const perTest = 20; // Change to desired number
```

### Modifying Color Scheme
Update the TailwindCSS classes in the EJS templates to change colors and styling.

### Adding New Features
The modular structure makes it easy to add new routes and functionality to `server.js`.

## 📊 Data Format

### Questions Format
```json
{
  "question": "Question text",
  "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
  "answer": 0,
  "is_multiple_choice": false,
  "source": {
    "correct_answer": "A",
    "community_answer": "A", 
    "community_confidence": "high"
  }
}
```

### Score Format
```json
{
  "username": "user123",
  "examId": 1,
  "score": 18,
  "totalQuestions": 20,
  "percentage": 90,
  "timeSpent": 1200,
  "timestamp": "2025-08-28T15:43:12.787Z",
  "date": "28/8/2025"
}
```

### Starred Questions Format
```json
[
  {
    "username": "user123",
    "questions": [
      {
        "question": "Starred question text",
        "options": ["A", "B", "C", "D"],
        "answer": 0
      }
    ]
  }
]
```

## 🔒 Security Notes

- This is a **local development application**
- No password authentication (username only)
- Data stored in local JSON files
- Not recommended for production use without additional security measures

## 🤝 Contributing

Feel free to contribute by:
- Adding new question sets
- Improving the UI/UX
- Adding new features
- Fixing bugs
- Improving documentation

## 📝 License

This project is for educational purposes. Please ensure you have proper rights to any exam materials you use.

## 🆘 Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 4000 is available
   - Ensure Node.js is installed correctly
   - Run `npm install` to install dependencies

2. **Questions not loading**
   - Check `data/questions.json` exists and has valid JSON
   - Restart the server after adding new questions

3. **PDF parser not working**
   - Ensure Python and pdfplumber are installed
   - Check PDF file path and permissions

4. **Scores not saving**
   - Check if `data/scores.json` exists and is writable
   - Ensure user is logged in before taking quiz

### Support

For issues and questions, please check the code comments or create an issue in the project repository.

---

**Happy studying! 🎓 Good luck with your AWS SAP-C02 exam! 🚀**
