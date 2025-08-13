// server.ts
import express from 'express';
import feedbackRouter from './routes/feedbackRouter.js';
import chatbotRouter from './routes/chatbotRouter.js';
const app = express();
const PORT = 3000;
app.use(express.json());
// 라우터 등록
app.use('/feedback', feedbackRouter);
app.use('/chatbot', chatbotRouter);
// 서버 시작
app.listen(PORT, () => {
    console.log(`🚀 Express 서버 실행 중: http://localhost:${PORT}`);
});
