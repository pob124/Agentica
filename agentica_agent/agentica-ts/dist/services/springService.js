import axios from 'axios';
const BASE_URL = 'http://localhost:8080';
export const springService = {
    async createProject({ name, description, industry }) {
        const res = await axios.post(`${BASE_URL}/projects`, { name, description, industry });
        return res.data;
    },
    async listProjects() {
        const res = await axios.get(`${BASE_URL}/projects`);
        return res.data;
    },
    async createLead({ companyName, industry, contactEmail, contactName, size, language }) {
        const res = await axios.post(`${BASE_URL}/leads`, { companyName, industry, contactEmail, contactName, size, language });
        return {
            status: 'success',
            data: res.data,
        };
    },
    async listLeads() {
        const res = await axios.get(`${BASE_URL}/leads`);
        return res.data;
    },
    async autoConnectLeadsByNameAndLeads(projectName, leadNames) {
        const res = await axios.post(`${BASE_URL}/projects/auto-connect-by-name-with-leads`, {
            projectName,
            leadNames,
        });
        return {
            status: 'success',
            data: res.data,
        };
    },
    async getProjectById(projectId) {
        const res = await axios.get(`${BASE_URL}/projects/${projectId}`);
        return res.data;
    },
    async getLeadById(leadId) {
        const res = await axios.get(`${BASE_URL}/leads/${leadId}`);
        return res.data;
    },
    async saveEmail(projectId, leadId, subject, body) {
        const res = await axios.post(`${BASE_URL}/emails`, { projectId, leadId, subject, body });
        return res.data;
    },
    async submitFeedback({ emailId, feedbackText }) {
        const res = await axios.post(`${BASE_URL}/feedbacks`, { emailId, feedbackText });
        return res.data;
    },
    async getLeadByName(companyName) {
        const res = await axios.get(`${BASE_URL}/leads`);
        const leads = res.data;
        return (leads.find((l) => l.name?.trim().toLowerCase() === companyName.trim().toLowerCase()) ?? null);
    },
    async getProjectByName(projectName) {
        const res = await axios.get(`${BASE_URL}/projects`, {
            params: { name: projectName.trim() }
        });
        const projects = res.data;
        // 정확히 일치하는 것만 리턴
        return projects.find((p) => p.name.trim() === projectName.trim()) ?? null;
    },
    async summarizeFeedbackResult({ projectId, leadId, emailId, originalText, responseSummary, responseType }) {
        const res = await axios.post(`${BASE_URL}/feedback`, {
            projectId,
            leadId,
            emailId,
            originalText,
            responseSummary,
            responseType
        });
        return res.data;
    },
    async saveEmailToSession(emailData) {
        const res = await axios.post(`${BASE_URL}/emails/save-to-session`, emailData);
        return res.data;
    }
    // 필요시 추가 엔드포인트 여기에 계속 확장
};
