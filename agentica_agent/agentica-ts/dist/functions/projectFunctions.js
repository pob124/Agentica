// functions/projectFunctions.ts
import { agent } from '../agent.js';
import { springService } from '../services/springService.js';
export async function createProject({ userPrompt }) {
    const systemPrompt = `
사용자의 프롬프트에서 사업 정보(name, description, industry)를 추출해 JSON 형식으로 응답해.

제약사항:
- 설명 금지. JSON만 반환.
- industry는 다음 중 하나만 선택: ["AI", "금융", "마케팅", "헬스케어", "교육", "게임", "커머스", "자동차", "건설", "기타"]

예시:
{
  "name": "AI 마케팅",
  "description": "AI 기반 마케팅 자동화 서비스, 초기 개발비 5만 달러, 6개월 개발 기간",
  "industry": "마케팅"
}
`.trim();
    const result = await agent.conversate([
        { type: 'text', text: systemPrompt },
        { type: 'text', text: userPrompt }
    ]);
    const last = Array.isArray(result) ? result[result.length - 1] : result;
    const lastText = typeof last === 'string'
        ? last
        : last.content ?? last.text ?? '';
    const match = lastText.match(/\{[\s\S]*\}/);
    if (match) {
        try {
            const parsed = JSON.parse(match[0].trim());
            if (!parsed.name)
                return { status: 'error', error: '사업명(name) 추출 실패' };
            return await springService.createProject(parsed);
        }
        catch (error) {
            return { status: 'error', error: 'JSON 파싱 실패' };
        }
    }
    return { status: 'error', error: '사업 정보 추출 실패' };
}
export async function listProjects() {
    return await springService.listProjects();
}
