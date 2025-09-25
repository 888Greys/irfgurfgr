// API utility for assessment endpoints
interface QuestionData {
  question_id: string;
  section_id: string;
  section_name: string;
  question: string;
  description?: string;
  scoring_rubric: Record<string, string>;
}

interface AssessmentGuidance {
  explanation?: string;
  why_it_matters?: string;
  kenya_context?: string;
  improvement_tips?: string[];
  local_examples?: {
    good_practice?: string;
    common_mistake?: string;
  };
  next_steps?: string[];
  message?: string;
  detailed_explanation?: string;
}
export async function startAssessment(businessInfo: {
  name: string;
  industry: string;
  size: string;
  location: string;
}): Promise<{ success: boolean; assessment_id?: string; error?: string }> {
  const res = await fetch("/api/assessment/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_info: businessInfo }),
  });
  if (!res.ok) throw new Error("Failed to start assessment");
  return res.json();
}

export async function getNextQuestion(assessmentId: string): Promise<QuestionData | { completed: boolean }> {
  const res = await fetch(`/api/assessment/${assessmentId}/next`);
  if (!res.ok) throw new Error("Failed to fetch next question");
  return res.json();
}

export async function submitAnswer(assessmentId: string, data: { section_id: string; question_id: string; score: number }): Promise<{ success: boolean; error?: string }> {
  const res = await fetch(`/api/assessment/${assessmentId}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to submit answer");
  return res.json();
}

export async function getAssessmentGuidance(assessmentId: string, questionId: string, userMessage: string, section: string = ""): Promise<AssessmentGuidance> {
  const res = await fetch(`/api/assessment/${assessmentId}/guidance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: questionId,
      user_message: userMessage,
      section: section,
    }),
  });
  if (!res.ok) throw new Error("Failed to get guidance");
  return res.json();
}
