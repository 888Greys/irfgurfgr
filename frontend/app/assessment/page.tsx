"use client";

import { useState, useEffect } from "react";
import { startAssessment, getNextQuestion, submitAnswer, getAssessmentGuidance } from "@/lib/api";
import { motion } from "framer-motion";
import ReactMarkdown from 'react-markdown';
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";

// Placeholder for categories/sections
const categories = [
  "Data Infrastructure",
  "Technology Infrastructure",
  "Human Resources & Skills",
  "Business Process Maturity",
  "Strategic & Financial Readiness",
  "Regulatory & Compliance Readiness",
];

interface QuestionData {
  question_id: string;
  section_id: string;
  section_name: string;
  question: string;
  description?: string;
  scoring_rubric: Record<string, string>;
}

export default function AssessmentPage() {
  const [businessInfo, setBusinessInfo] = useState({ name: "", industry: "", size: "", location: "" });
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [showQuestions, setShowQuestions] = useState(false);
  const [questionData, setQuestionData] = useState<QuestionData | null>(null);
  const [answerLoading, setAnswerLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Chat state - now per question
  const [chatMessage, setChatMessage] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHistories, setChatHistories] = useState<Record<number, Array<{role: 'user' | 'assistant', content: string}>>>({});

  // Clear chat message when question changes
  useEffect(() => {
    setChatMessage("");
  }, [currentQuestionIdx]);

  const handleChatSubmit = async () => {
    if (!chatMessage.trim() || !questionData || !assessmentId) return;
    
    const userMessage = chatMessage.trim();
    setChatMessage("");
    setChatLoading(true);
    
    // Add user message to current question's chat history
    setChatHistories(prev => ({
      ...prev,
      [currentQuestionIdx]: [
        ...(prev[currentQuestionIdx] || []),
        { role: 'user', content: userMessage }
      ]
    }));
    
    try {
      // Call the assessment guide agent API
      const guidance = await getAssessmentGuidance(
        assessmentId,
        questionData.question_id,
        userMessage,
        questionData.section_id
      );
      
      // Extract and format the response content
      let assistantResponse = "";
      
      try {
        if (guidance.explanation) {
          assistantResponse += `**Explanation:** ${guidance.explanation}\n\n`;
        }
        
        if (guidance.why_it_matters) {
          assistantResponse += `**Why It Matters:** ${guidance.why_it_matters}\n\n`;
        }
        
        if (guidance.kenya_context) {
          assistantResponse += `**Kenya Context:** ${guidance.kenya_context}\n\n`;
        }
        
        if (guidance.improvement_tips && Array.isArray(guidance.improvement_tips)) {
          assistantResponse += `**Improvement Tips:**\n`;
          guidance.improvement_tips.forEach((tip: string) => {
            assistantResponse += `• ${tip}\n`;
          });
          assistantResponse += `\n`;
        }
        
        if (guidance.local_examples) {
          if (guidance.local_examples.good_practice) {
            assistantResponse += `**Good Practice Example:** ${guidance.local_examples.good_practice}\n\n`;
          }
          if (guidance.local_examples.common_mistake) {
            assistantResponse += `**Common Mistake to Avoid:** ${guidance.local_examples.common_mistake}\n\n`;
          }
        }
        
        if (guidance.next_steps && Array.isArray(guidance.next_steps)) {
          assistantResponse += `**Next Steps:**\n`;
          guidance.next_steps.forEach((step: string, index: number) => {
            assistantResponse += `${index + 1}. ${step}\n`;
          });
          assistantResponse += `\n`;
        }
      } catch (error) {
        console.warn('Error formatting guidance response:', error);
      }
      
      // Fallback if no structured content or formatting failed
      if (!assistantResponse.trim()) {
        assistantResponse = guidance.detailed_explanation || guidance.explanation || guidance.message || "I understand your question. Let me provide some guidance on this assessment question.";
      }
      
      setChatHistories(prev => ({
        ...prev,
        [currentQuestionIdx]: [
          ...(prev[currentQuestionIdx] || []),
          { role: 'assistant', content: assistantResponse }
        ]
      }));
      
    } catch (error) {
      console.error('Chat error:', error);
      setChatHistories(prev => ({
        ...prev,
        [currentQuestionIdx]: [
          ...(prev[currentQuestionIdx] || []),
          { role: 'assistant', content: 'Sorry, I encountered an error while processing your question. Please try again.' }
        ]
      }));
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Top Bar */}
      <div className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background/80 backdrop-blur-md px-4 md:px-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <h1 className="text-lg font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent md:text-2xl">
            DeepAgents AI Assessment
          </h1>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-xs font-medium text-primary">System Online</span>
          </div>
        </div>
      </div>
      {/* Main Content: Four-Column Layout */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-center max-w-screen-2xl mx-auto py-8 px-2 md:px-8 gap-8">
        {/* Left Column: Vertical Progress Indicator */}
        <aside className="hidden md:block w-16">
          <motion.div
            className="sticky top-24 flex flex-col items-center gap-2"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Progress Snake */}
            <div className="relative">
              {/* Connecting line */}
              <div className="absolute left-1/2 top-6 bottom-6 w-0.5 bg-gradient-to-b from-primary/20 via-primary/40 to-primary/20 transform -translate-x-1/2"></div>
              
              {/* Progress dots */}
              {Array.from({ length: 21 }, (_, i) => {
                const isCompleted = i < currentQuestionIdx;
                const isCurrent = i === currentQuestionIdx;
                return (
                  <motion.div
                    key={i}
                    className={`relative w-3 h-3 rounded-full border-2 mb-4 ${
                      isCompleted
                        ? 'bg-primary border-primary shadow-lg'
                        : isCurrent
                        ? 'bg-primary/20 border-primary animate-pulse'
                        : 'bg-muted border-border'
                    }`}
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.3, delay: i * 0.05 }}
                  >
                    {isCompleted && (
                      <motion.div
                        className="absolute inset-0 bg-primary rounded-full"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.2 }}
                      />
                    )}
                    {isCurrent && (
                      <motion.div
                        className="absolute inset-0 bg-primary rounded-full animate-ping"
                        style={{ animationDuration: '2s' }}
                      />
                    )}
                  </motion.div>
                );
              })}
            </div>
            
            {/* Progress percentage */}
            <div className="mt-4 text-center">
              <div className="text-xs font-medium text-primary">
                {Math.round((currentQuestionIdx / 21) * 100)}%
              </div>
              <div className="text-xs text-muted-foreground">
                {currentQuestionIdx}/21
              </div>
            </div>
          </motion.div>
        </aside>
        
        {/* Left Column: Business Info Form */}
        <aside className="w-full md:w-1/4 mb-8 md:mb-0">
          <motion.div
            className="rounded-2xl shadow-xl border bg-gradient-to-br from-card to-card/50 p-6 md:p-8 backdrop-blur-sm"
            whileHover={{ scale: 1.02 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            <div className="mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent mb-2">
                Business Information
              </h2>
              <p className="text-sm text-muted-foreground">
                Tell us about your organization to get personalized AI readiness insights.
              </p>
            </div>
            <form
              className="space-y-5"
              onSubmit={async e => {
                e.preventDefault();
                setLoading(true);
                setError(null);
                try {
                  // Always trim industry value before sending
                  const cleanBusinessInfo = {
                    ...businessInfo,
                    industry: businessInfo.industry.trim(),
                  };
                  const res = await startAssessment(cleanBusinessInfo);
                  if (!res.success || !res.assessment_id) {
                    setError(res.error || "Failed to start assessment");
                    setLoading(false);
                    return;
                  }
                  setAssessmentId(res.assessment_id);
                  setShowQuestions(true);
                  // Fetch first question
                  const q = await getNextQuestion(res.assessment_id);
                  if ('completed' in q && q.completed) {
                    setQuestionData(null);
                  } else {
                    setQuestionData(q as QuestionData);
                  }
                  setCurrentQuestionIdx(0);
                } catch (err: unknown) {
                  const errorMessage = err instanceof Error ? err.message : "Failed to start assessment";
                  setError(errorMessage);
                } finally {
                  setLoading(false);
                }
              }}
            >
              <div className="space-y-2">
                <label className="block text-sm font-medium text-foreground">
                  Organization Name
                </label>
                <input
                  className="w-full border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all bg-background"
                  value={businessInfo.name}
                  onChange={e => setBusinessInfo({ ...businessInfo, name: e.target.value })}
                  placeholder="Enter your organization name"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-foreground">
                  Industry
                </label>
                <Select value={businessInfo.industry} onValueChange={val => setBusinessInfo({ ...businessInfo, industry: val })} required>
                  <SelectTrigger className="w-full border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all bg-background">
                    <SelectValue placeholder="Select your industry" />
                  </SelectTrigger>
                  <SelectContent
                    position="item-aligned"
                    className="bg-background border border-border shadow-xl"
                  >
                    <SelectItem value="Agriculture">🌾 Agriculture</SelectItem>
                    <SelectItem value="Manufacturing">🏭 Manufacturing</SelectItem>
                    <SelectItem value="Technology">💻 Technology</SelectItem>
                    <SelectItem value="Finance">💰 Finance</SelectItem>
                    <SelectItem value="Healthcare">🏥 Healthcare</SelectItem>
                    <SelectItem value="Education">🎓 Education</SelectItem>
                    <SelectItem value="Retail">🛍️ Retail</SelectItem>
                    <SelectItem value="Transportation">🚚 Transportation</SelectItem>
                    <SelectItem value="Construction">🏗️ Construction</SelectItem>
                    <SelectItem value="Tourism">✈️ Tourism</SelectItem>
                    <SelectItem value="Energy">⚡ Energy</SelectItem>
                    <SelectItem value="Telecommunications">📡 Telecommunications</SelectItem>
                    <SelectItem value="Other">📋 Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-foreground">
                  Organization Size
                </label>
                <Select value={businessInfo.size} onValueChange={val => setBusinessInfo({ ...businessInfo, size: val })} required>
                  <SelectTrigger className="w-full border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all bg-background">
                    <SelectValue placeholder="Select organization size" />
                  </SelectTrigger>
                  <SelectContent className="bg-background border border-border shadow-xl">
                    <SelectItem value="Small (1-50 employees)">Small (1-50 employees)</SelectItem>
                    <SelectItem value="Medium (51-250 employees)">Medium (51-250 employees)</SelectItem>
                    <SelectItem value="Large (250+ employees)">Large (250+ employees)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-foreground">
                  Location
                </label>
                <Select value={businessInfo.location} onValueChange={val => setBusinessInfo({ ...businessInfo, location: val })} required>
                  <SelectTrigger className="w-full border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all bg-background">
                    <SelectValue placeholder="Select your location" />
                  </SelectTrigger>
                  <SelectContent className="bg-background border border-border shadow-xl">
                    <SelectItem value="Nairobi">🇰🇪 Nairobi</SelectItem>
                    <SelectItem value="Mombasa">🇰🇪 Mombasa</SelectItem>
                    <SelectItem value="Kisumu">🇰🇪 Kisumu</SelectItem>
                    <SelectItem value="Nakuru">🇰🇪 Nakuru</SelectItem>
                    <SelectItem value="Eldoret">🇰🇪 Eldoret</SelectItem>
                    <SelectItem value="Thika">🇰🇪 Thika</SelectItem>
                    <SelectItem value="Malindi">🇰🇪 Malindi</SelectItem>
                    <SelectItem value="Kitale">🇰🇪 Kitale</SelectItem>
                    <SelectItem value="Garissa">🇰🇪 Garissa</SelectItem>
                    <SelectItem value="Kakamega">🇰🇪 Kakamega</SelectItem>
                    <SelectItem value="Other">🌍 Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-primary to-primary/90 text-white py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Starting Assessment...
                  </div>
                ) : (
                  "🚀 Start AI Readiness Assessment"
                )}
              </button>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg text-sm"
                >
                  {error}
                </motion.div>
              )}
            </form>
          </motion.div>
        </aside>
        {/* Center Column: Assessment Questions */}
        <main className="w-full md:w-1/2 flex flex-col gap-6">
          {showQuestions && questionData ? (
            <div className="w-full max-w-4xl">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="mb-6"
              >
                <h2 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
                  AI Readiness Assessment
                </h2>
                <p className="text-muted-foreground mt-2">
                  Question {currentQuestionIdx + 1} • {questionData.section_name}
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="bg-gradient-to-br from-card to-card/50 rounded-2xl shadow-xl border p-8 mb-6"
              >
                <div className="mb-6">
                  <h3 className="text-xl font-semibold text-foreground mb-3 leading-relaxed">
                    {questionData.question}
                  </h3>
                  {questionData.description && (
                    <p className="text-muted-foreground text-sm italic">
                      {questionData.description}
                    </p>
                  )}
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-4">
                    Select your current level:
                  </h4>
                  <div className="grid gap-3">
                    {questionData.scoring_rubric &&
                      Object.entries(questionData.scoring_rubric)
                        .sort(([a], [b]) => parseInt(a) - parseInt(b))
                        .map(([score, description]) => (
                          <motion.button
                            key={score}
                            disabled={answerLoading}
                            onClick={async () => {
                              if (!assessmentId || !questionData) return;
                              setAnswerLoading(true);
                              try {
                                const res = await submitAnswer(assessmentId, {
                                  section_id: questionData.section_id,
                                  question_id: questionData.question_id,
                                  score: parseInt(score),
                                });
                                if (res.success) {
                                  // After successful submission, get the next question
                                  const nextQ = await getNextQuestion(assessmentId);
                                  if ('completed' in nextQ && nextQ.completed) {
                                    setQuestionData(null);
                                  } else if ('question' in nextQ) {
                                    setQuestionData(nextQ as QuestionData);
                                    setCurrentQuestionIdx(idx => idx + 1);
                                  } else {
                                    console.error('Unexpected response from get_next_question:', nextQ);
                                  }
                                } else {
                                  console.error('Failed to submit answer:', res.error);
                                }
                              } catch (err) {
                                console.error('Error submitting answer:', err);
                              } finally {
                                setAnswerLoading(false);
                              }
                            }}
                            className="group relative w-full text-left p-4 rounded-xl border-2 border-border hover:border-primary/50 hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <div className="flex items-start gap-4">
                              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary/20 flex items-center justify-center group-hover:border-primary/40 transition-colors">
                                <span className="text-lg font-bold text-primary">
                                  {score}
                                </span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="text-sm font-medium text-primary">
                                    Level {score}
                                  </span>
                                  <div className="flex-1 h-px bg-gradient-to-r from-primary/20 to-transparent"></div>
                                </div>
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                  {String(description)}
                                </p>
                              </div>
                            </div>
                            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
                          </motion.button>
                        ))}
                  </div>
                </div>

                {answerLoading && (
                  <div className="mt-6 flex items-center justify-center gap-2 text-muted-foreground">
                    <div className="w-4 h-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
                    <span className="text-sm">Submitting answer...</span>
                  </div>
                )}
              </motion.div>

              {/* Assessment Guide Chat */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="bg-gradient-to-br from-card to-card/50 rounded-2xl shadow-xl border p-6"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-foreground">AI Assessment Guide</h4>
                    <p className="text-xs text-muted-foreground">Get help with this question</p>
                  </div>
                </div>
                
                {/* Chat History */}
                <div className="space-y-3 mb-4 max-h-48 overflow-y-auto">
                  {(!chatHistories[currentQuestionIdx] || chatHistories[currentQuestionIdx].length === 0) ? (
                    <div className="bg-muted/50 rounded-lg p-3">
                      <p className="text-sm text-muted-foreground">
                        💡 <strong>Need clarification?</strong> Ask me about this question or get personalized guidance for your industry.
                      </p>
                    </div>
                  ) : (
                    chatHistories[currentQuestionIdx].map((message, index) => (
                      <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        {message.role === 'assistant' && (
                          <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                            <span className="text-xs">🤖</span>
                          </div>
                        )}
                        <div className={`max-w-[80%] rounded-lg p-3 ${
                          message.role === 'user'
                            ? 'bg-primary text-white'
                            : 'bg-muted/50 text-foreground'
                        }`}>
                          {message.role === 'user' ? (
                            <div className="text-sm whitespace-pre-line">
                              {message.content}
                            </div>
                          ) : (
                            <div className="markdown-content">
                              <ReactMarkdown
                                components={{
                                  strong: ({ children }) => (
                                    <strong className="font-semibold text-primary">{children}</strong>
                                  ),
                                  ul: ({ children }) => (
                                    <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>
                                  ),
                                  ol: ({ children }) => (
                                    <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>
                                  ),
                                  li: ({ children }) => (
                                    <li className="ml-4">{children}</li>
                                  ),
                                  p: ({ children }) => (
                                    <p className="mb-2 last:mb-0">{children}</p>
                                  ),
                                }}
                              >
                                {message.content}
                              </ReactMarkdown>
                            </div>
                          )}
                        </div>
                        {message.role === 'user' && (
                          <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                            <span className="text-xs text-white">👤</span>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                  
                  {chatLoading && (
                    <div className="flex gap-3 justify-start">
                      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                        <span className="text-xs">🤖</span>
                      </div>
                      <div className="bg-muted/50 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
                    placeholder="Ask for help with this question..."
                    className="flex-1 text-sm border border-border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all bg-background"
                    disabled={chatLoading}
                  />
                  <button 
                    onClick={handleChatSubmit}
                    disabled={chatLoading || !chatMessage.trim()}
                    className="px-4 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {chatLoading ? (
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    ) : (
                      "Ask"
                    )}
                  </button>
                </div>
              </motion.div>
            </div>
          ) : null}
        </main>
        {/* Right Column: Categories Sidebar */}
        <aside className="hidden md:block w-1/4 pl-8">
          <motion.div
            className="rounded-2xl shadow-xl border bg-gradient-to-br from-card to-card/50 p-6 md:p-8 backdrop-blur-sm sticky top-8"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent mb-2">
                Assessment Categories
              </h2>
              <p className="text-sm text-muted-foreground">
                We&apos;ll evaluate your organization across these key areas of AI readiness.
              </p>
            </div>

            <div className="space-y-3">
              {categories.map((category, index) => {
                const isActive = questionData?.section_name === category;
                return (
                  <motion.div
                    key={category}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className={`relative p-4 rounded-xl border-2 transition-all duration-200 cursor-pointer ${
                      isActive
                        ? 'border-primary bg-primary/5 shadow-lg'
                        : 'border-border hover:border-primary/30 hover:shadow-md'
                    }`}
                    whileHover={{ scale: 1.02 }}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${
                        isActive ? 'bg-primary' : 'bg-muted-foreground/30'
                      }`}></div>
                      <span className={`text-sm font-medium ${
                        isActive ? 'text-primary' : 'text-muted-foreground'
                      }`}>
                        {category}
                      </span>
                    </div>
                    {isActive && (
                      <motion.div
                        className="absolute inset-0 bg-primary/5 rounded-xl"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.3 }}
                      />
                    )}
                  </motion.div>
                );
              })}
            </div>

            <div className="mt-8 p-4 bg-gradient-to-br from-primary/5 to-primary/10 rounded-xl border border-primary/20">
              <h3 className="text-sm font-semibold text-primary mb-2">💡 Pro Tip</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Answer honestly about your current capabilities. This assessment helps identify your AI readiness gaps and provides actionable recommendations.
              </p>
            </div>
          </motion.div>
        </aside>
      </div>
    </div>
  );
}
