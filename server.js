const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));
app.set("view engine", "ejs");

const QUESTIONS_FILE = path.join(__dirname, "data/questions.json");
const STARRED_FILE = path.join(__dirname, "data/starred.json");
const SCORES_FILE = path.join(__dirname, "data/scores.json");

function loadJson(file) {
  if (!fs.existsSync(file)) fs.writeFileSync(file, "[]");
  return JSON.parse(fs.readFileSync(file, "utf8"));
}
function saveJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function normalizeQuestions(rawQuestions) {
  return rawQuestions.map(q => {
    // clean options (loại bỏ "" hoặc null)
    const cleanOpts = q.options.filter(opt => opt && opt.trim() !== "");

    return {
      question: q.question,
      options: cleanOpts,
      answer: q.answer,   // có thể là số hoặc mảng số
      is_multiple_choice: q.is_multiple_choice || false,  // thêm thuộc tính multiple choice
      source: q.source || {}
    };
  });
}


// Menu chọn đề
app.get("/", (req, res) => {
  const questions = loadJson(QUESTIONS_FILE);
  const starred = loadJson(STARRED_FILE);
  const scores = loadJson(SCORES_FILE);

  const perTest = 20;
  const examsCount = Math.ceil(questions.length / perTest);

  // Tạo object chứa điểm cao nhất cho mỗi đề
  const examScores = {};
  scores.forEach(score => {
    const examId = score.examId;
    if (!examScores[examId] || score.score > examScores[examId].score) {
      examScores[examId] = {
        score: score.score,
        percentage: score.percentage,
        totalQuestions: score.totalQuestions
      };
    }
  });

  // Đếm tổng số câu hỏi đã đánh dấu (tất cả user)
  const totalStarredCount = starred.reduce((total, entry) => total + entry.questions.length, 0);

  res.render("index", { 
    examsCount, 
    starredCount: totalStarredCount,
    examScores: examScores
  });
});

// Trang làm đề (chia sẵn 20 câu/đề)
app.get("/quiz/:id", (req, res) => {
  const raw = loadJson(QUESTIONS_FILE);
  const questions = normalizeQuestions(raw);

  const perTest = 20;
  const exams = [];
  for (let i = 0; i < questions.length; i += perTest) {
    exams.push(questions.slice(i, i + perTest));
  }

  const id = parseInt(req.params.id, 10);
  if (id < 1 || id > exams.length) return res.send("Đề không tồn tại");

  res.render("quiz", { examId: id, questions: exams[id - 1], isStarredPage: false });
});

// Trang câu hỏi đã đánh dấu - cập nhật để nhận username
app.get("/starred", (req, res) => {
  const username = req.query.username || 'anonymous';
  const starred = loadJson(STARRED_FILE);
  
  // Tìm câu hỏi đã đánh dấu của user cụ thể
  const userStarred = starred.find(entry => entry.username === username);
  const questions = userStarred ? userStarred.questions : [];
  
  res.render("quiz", { examId: "⭐", questions: questions, isStarredPage: true });
});

// Trang lịch sử điểm
app.get("/scores", (req, res) => {
  res.render("scores");
});

// API để bỏ đánh dấu câu hỏi
app.post("/unstar", (req, res) => {
  const { questionText, username } = req.body;
  
  if (!username) {
    return res.status(400).json({ error: "Username is required" });
  }
  
  let starred = loadJson(STARRED_FILE);

  // Tìm entry của user
  const userIndex = starred.findIndex(entry => entry.username === username);
  
  if (userIndex !== -1) {
    // Xóa câu hỏi khỏi danh sách của user
    starred[userIndex].questions = starred[userIndex].questions.filter(q => q.question !== questionText);
    
    // Nếu user không còn câu hỏi nào đã đánh dấu, xóa entry
    if (starred[userIndex].questions.length === 0) {
      starred.splice(userIndex, 1);
    }
  }

  saveJson(STARRED_FILE, starred);
  
  // Đếm số câu hỏi còn lại của user
  const userStarred = starred.find(entry => entry.username === username);
  const userCount = userStarred ? userStarred.questions.length : 0;
  
  res.json({ success: true, count: userCount });
});

// API để lưu điểm số
app.post("/save-score", (req, res) => {
  const { username, examId, score, totalQuestions, percentage, timeSpent } = req.body;
  
  if (!username || !examId || score === undefined || !totalQuestions) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  let scores = loadJson(SCORES_FILE);
  
  const scoreEntry = {
    username,
    examId,
    score,
    totalQuestions,
    percentage,
    timeSpent: timeSpent || 0,
    timestamp: new Date().toISOString(),
    date: new Date().toLocaleDateString('vi-VN')
  };

  scores.push(scoreEntry);
  saveJson(SCORES_FILE, scores);
  
  res.json({ success: true, message: "Điểm đã được lưu thành công!" });
});

// API để lấy lịch sử điểm của user
app.get("/scores/:username", (req, res) => {
  const username = req.params.username;
  const scores = loadJson(SCORES_FILE);
  
  const userScores = scores
    .filter(score => score.username === username)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  
  res.json(userScores);
});

// API để lấy số lượng câu hỏi đã đánh dấu của user
app.get("/starred/:username/count", (req, res) => {
  const username = req.params.username;
  const starred = loadJson(STARRED_FILE);
  
  const userStarred = starred.find(entry => entry.username === username);
  const count = userStarred ? userStarred.questions.length : 0;
  
  res.json({ count });
});

// Debug endpoint - hiển thị thông tin câu hỏi
app.get("/debug", (req, res) => {
  const raw = loadJson(QUESTIONS_FILE);
  const questions = normalizeQuestions(raw);
  
  // Hiển thị thống kê tổng quan
  const multipleChoiceCount = questions.filter(q => q.is_multiple_choice).length;
  const singleChoiceCount = questions.length - multipleChoiceCount;
  
  res.json({
    total_questions: questions.length,
    single_choice: singleChoiceCount,
    multiple_choice: multipleChoiceCount,
    sample_questions: questions.slice(0, 3).map((q, idx) => ({
      id: idx,
      question: q.question.substring(0, 100) + "...",
      is_multiple_choice: q.is_multiple_choice,
      answer_type: Array.isArray(q.answer) ? 'array' : 'single'
    }))
  });
});

app.get("/debug/:questionId", (req, res) => {
  const raw = loadJson(QUESTIONS_FILE);
  const questions = normalizeQuestions(raw);
  
  const questionId = parseInt(req.params.questionId);
  const question = questions[questionId];
  
  if (!question) {
    return res.json({ error: "Question not found" });
  }
  
  res.json({
    questionId,
    question: question.question,
    options: question.options,
    answer: question.answer,
    is_multiple_choice: question.is_multiple_choice,
    answer_type: Array.isArray(question.answer) ? 'array' : 'single',
    total_questions: questions.length
  });
});

// API để toggle đánh dấu câu hỏi theo user
app.post("/star", (req, res) => {
  const { question, username } = req.body;
  
  if (!username) {
    return res.status(400).json({ error: "Username is required" });
  }
  
  let starred = loadJson(STARRED_FILE);

  // Tìm hoặc tạo entry cho user
  let userIndex = starred.findIndex(entry => entry.username === username);
  
  if (userIndex === -1) {
    // Tạo entry mới cho user
    starred.push({
      username: username,
      questions: []
    });
    userIndex = starred.length - 1;
  }

  const userQuestions = starred[userIndex].questions;
  const questionExists = userQuestions.find(q => q.question === question.question);

  if (questionExists) {
    // Bỏ đánh dấu
    starred[userIndex].questions = userQuestions.filter(q => q.question !== question.question);
    
    // Nếu user không còn câu hỏi nào, xóa entry
    if (starred[userIndex].questions.length === 0) {
      starred.splice(userIndex, 1);
    }
  } else {
    // Thêm đánh dấu
    starred[userIndex].questions.push(question);
  }

  saveJson(STARRED_FILE, starred);
  
  // Đếm số câu hỏi của user hiện tại
  const currentUserEntry = starred.find(entry => entry.username === username);
  const userCount = currentUserEntry ? currentUserEntry.questions.length : 0;
  
  res.json({ success: true, count: userCount });
});

const PORT = 4000;
app.listen(PORT, () => console.log(`✅ Server chạy tại http://localhost:${PORT}`));
