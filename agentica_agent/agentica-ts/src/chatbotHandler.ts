// chatbotHandler.ts
import { analyzePromptAI } from './analyzePromptAI.js';
import * as projectFuncs from './functions/projectFunctions.js';
import * as leadFuncs from './functions/leadFunctions.js';
import * as emailFuncs from './functions/emailFunctions.js';
import * as feedbackFuncs from './functions/feedbackFunctions.js';

export async function chatbotHandler(input: string) {
  const { intent, extracted_params } = await analyzePromptAI(input);
  console.log('🛠 DEBUG — analyzePromptAI 결과:', intent, extracted_params);
  switch (intent) {
    case 'register_project':
      return await projectFuncs.createProject(extracted_params);
    case 'register_lead':
      return await leadFuncs.createLead(extracted_params);
    case 'connect_leads':
      return await leadFuncs.autoConnectLeads(extracted_params);
    case 'initial_email':{
      const { userPrompt } = extracted_params;
      const result = await emailFuncs.generateInitialEmail({ userPrompt });
      return {
        status: 'success',
        message: `초안 생성 완료: ${result.length}건`,
        data: result
      };
    }
    case 'followup_email':
      return await emailFuncs.generateFollowupEmail(extracted_params);
    case 'analyze_email':
      return await emailFuncs.analyzeEmailIssues(extracted_params);
    case 'handle_email_rejection':
      // 통합된 이메일 재작성 처리 (거부/취소 모두 처리)
      return await emailFuncs.handleEmailRejection(extracted_params);
    case 'list_projects':
      return await projectFuncs.listProjects();
    case 'list_leads':
      return await leadFuncs.listLeads();  
    default:
      return { message: '의도를 이해하지 못했습니다.' };
  }
}
