declare const INTENT_LIST: readonly ["register_project", "register_lead", "connect_leads", "initial_email", "followup_email", "analyze_email", "handle_email_rejection", "list_projects", "list_leads"];
type Intent = typeof INTENT_LIST[number];
export interface AnalyzePromptResult {
    intent: Intent | 'unknown';
    extracted_params: any;
    confidence: number;
}
export declare function analyzePromptAI(prompt: string): Promise<AnalyzePromptResult>;
export {};
