import axios from 'axios';
import type { Lead } from '../types/index.js';
const BASE_URL = 'http://localhost:8080';

export const springService = {
  async createProject({ name, description, industry }: { name: string; description: string; industry: string }) {
    const res = await axios.post(`${BASE_URL}/projects`, { name, description, industry });
    return res.data;
  },
  async listProjects() {
    const res = await axios.get(`${BASE_URL}/projects`);
    return res.data;
  },
  async createLead({
    companyName,
    industry,
    contactEmail,
    contactName,
    size,        
    language 
  }: { companyName: string; industry: string; contactEmail: string; contactName?: string; size?: string; language?: string }) {
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
  async autoConnectLeadsByNameAndLeads(projectName: string, leadNames: string[]) {
    const res = await axios.post(`${BASE_URL}/projects/auto-connect-by-name-with-leads`, {
      projectName,
      leadNames,
    });
    return {
      status: 'success',
      data: res.data,
    };
  },
  async getProjectById(projectId: number) {
    const res = await axios.get(`${BASE_URL}/projects/${projectId}`);
    return res.data;
  },
  async getLeadById(leadId: number) {
    const res = await axios.get(`${BASE_URL}/leads/${leadId}`);
    return res.data;
  },
  async saveEmail(projectId: number, leadId: number, subject: string, body: string) {
    const res = await axios.post(`${BASE_URL}/emails`, { projectId, leadId, subject, body });
    return res.data;
  },
  async submitFeedback({ emailId, feedbackText }: { emailId: number; feedbackText: string }) {
    const res = await axios.post(`${BASE_URL}/feedbacks`, { emailId, feedbackText });
    return res.data;
  },

  async getLeadByName(companyName: string): Promise<Lead | null> {
    const res = await axios.get(`${BASE_URL}/leads`);
    const leads: Lead[] = res.data;

    return (
      leads.find(
        (l) => l.name?.trim().toLowerCase() === companyName.trim().toLowerCase()
      ) ?? null
    );
  },

  async getProjectByName(projectName: string) {
    const res = await axios.get(`${BASE_URL}/projects`, {
      params: { name: projectName.trim() }
    });

    const projects = res.data;

    // 정확히 일치하는 것만 리턴
    return projects.find((p: any) => p.name.trim() === projectName.trim()) ?? null;
  },

  async summarizeFeedbackResult({
    projectId,
    leadId,
    emailId,
    originalText,
    responseSummary,
    responseType
  }: {
    projectId: number;
    leadId: number;
    emailId: number;
    originalText: string;
    responseSummary: string;
    responseType: string;
  }) {
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
  
  async saveEmailToSession(emailData: any) {
    const res = await axios.post(`${BASE_URL}/emails/save-to-session`, emailData);
    return res.data;
  }
  // 필요시 추가 엔드포인트 여기에 계속 확장
};
