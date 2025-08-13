import type { Lead } from '../types/index.js';
export declare const springService: {
    createProject({ name, description, industry }: {
        name: string;
        description: string;
        industry: string;
    }): Promise<any>;
    listProjects(): Promise<any>;
    createLead({ companyName, industry, contactEmail, contactName, size, language }: {
        companyName: string;
        industry: string;
        contactEmail: string;
        contactName?: string;
        size?: string;
        language?: string;
    }): Promise<{
        status: string;
        data: any;
    }>;
    listLeads(): Promise<any>;
    autoConnectLeadsByNameAndLeads(projectName: string, leadNames: string[]): Promise<{
        status: string;
        data: any;
    }>;
    getProjectById(projectId: number): Promise<any>;
    getLeadById(leadId: number): Promise<any>;
    saveEmail(projectId: number, leadId: number, subject: string, body: string): Promise<any>;
    submitFeedback({ emailId, feedbackText }: {
        emailId: number;
        feedbackText: string;
    }): Promise<any>;
    getLeadByName(companyName: string): Promise<Lead | null>;
    getProjectByName(projectName: string): Promise<any>;
    summarizeFeedbackResult({ projectId, leadId, emailId, originalText, responseSummary, responseType }: {
        projectId: number;
        leadId: number;
        emailId: number;
        originalText: string;
        responseSummary: string;
        responseType: string;
    }): Promise<any>;
    saveEmailToSession(emailData: any): Promise<any>;
};
