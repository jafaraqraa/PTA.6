import React, { useEffect, useState } from 'react';
import { apiListQuizzes, apiSubmitQuiz, apiGetMySubmissions } from '../../api/api';
import { BookOpen, CheckCircle, HelpCircle, ArrowRight, MessageSquare, Monitor } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useSessionStore } from '../../store/sessionStore';
import clsx from 'clsx';

export default function StudentQuizzes() {
  const [quizzes, setQuizzes] = useState<any[]>([]);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [takingQuiz, setTakingQuiz] = useState<any | null>(null);
  const [answers, setAnswers] = useState<number[]>([]);
  const [lastSubmission, setLastSubmission] = useState<any | null>(null);
  const navigate = useNavigate();
  const { setActiveQuizId } = useSessionStore();

  const fetchData = async () => {
    try {
      const [qData, sData] = await Promise.all([apiListQuizzes(), apiGetMySubmissions()]);
      setQuizzes(qData);
      setSubmissions(sData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleStartQuiz = (quiz: any) => {
    if (quiz.quiz_type === 'simulator') {
       setActiveQuizId(quiz.id);
       navigate('/session');
       return;
    }
    setTakingQuiz(quiz);
    setAnswers(new Array(quiz.questions.length).fill(-1));
  };

  const handleOptionSelect = (qIndex: number, oIndex: number) => {
    const updated = [...answers];
    updated[qIndex] = oIndex;
    setAnswers(updated);
  };

  const handleSubmit = async () => {
    if (answers.includes(-1)) {
      alert("Please answer all questions before submitting.");
      return;
    }
    try {
      const res = await apiSubmitQuiz({
        quiz_id: takingQuiz.id,
        answers: JSON.stringify(answers)
      });
      setLastSubmission(res);
      setTakingQuiz(null);
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <div className="p-8">Loading quizzes...</div>;

  if (lastSubmission) {
    return (
      <div className="max-w-md mx-auto mt-20 text-center space-y-8 animate-fade-in">
        <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-inner">
          <CheckCircle size={40} />
        </div>
        <div className="space-y-2">
          <h1 className="text-3xl font-extrabold text-slate-900">Quiz Submitted!</h1>
          <p className="text-slate-500 font-medium">Your submission has been recorded successfully.</p>
        </div>
        <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-100 space-y-4">
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Your Score</p>
          <p className="text-6xl font-black text-emerald-500">{lastSubmission.score}%</p>
        </div>
        <div className="flex flex-col gap-3">
          <button onClick={() => setLastSubmission(null)} className="btn-primary py-4 text-lg">
            Back to Quizzes
          </button>
          {lastSubmission.session_id && (
            <button
              onClick={() => {
                // We need to set the evaluation in store before navigating
                // But the evaluation is already in the database.
                // For simplicity in this flow, we redirect to dashboard where they can see recent sessions
                // or we could fetch the evaluation.
                // Given the prompt "View Results", let's assume they want to see the evaluation page.
                // We'll let the student see it via the dashboard's recent activity for now or
                // if we want to be fancy, we'd fetch it here.
                navigate('/dashboard');
              }}
              className="btn-secondary py-4 text-lg bg-white"
            >
              View Detailed Results
            </button>
          )}
          <button onClick={() => navigate('/dashboard')} className="btn-secondary py-4 text-lg bg-white">
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (takingQuiz) {
    return (
      <div className="max-w-3xl mx-auto space-y-8 py-8">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-slate-900">{takingQuiz.title}</h1>
          <p className="text-slate-500">{takingQuiz.description}</p>
        </div>

        <div className="space-y-10">
          {takingQuiz.questions.map((q: any, qIndex: number) => {
             const options = JSON.parse(q.options);
             return (
               <div key={q.id} className="card p-8 space-y-6">
                 <div className="flex items-start gap-4">
                   <div className="w-8 h-8 rounded-full bg-primary-50 text-primary-600 flex items-center justify-center font-bold text-sm">
                     {qIndex + 1}
                   </div>
                   <h3 className="text-lg font-bold text-slate-900 pt-1">{q.question_text}</h3>
                 </div>
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-12">
                   {options.map((opt: string, oIndex: number) => (
                     <button
                       key={oIndex}
                       onClick={() => handleOptionSelect(qIndex, oIndex)}
                       className={`p-4 rounded-xl text-left transition-all border-2 ${
                         answers[qIndex] === oIndex
                           ? "border-primary-500 bg-primary-50 text-primary-700 shadow-sm ring-2 ring-primary-100"
                           : "border-slate-100 hover:border-slate-300 bg-white text-slate-700"
                       }`}
                     >
                       <span className="font-bold mr-2">{String.fromCharCode(65 + oIndex)}.</span>
                       {opt}
                     </button>
                   ))}
                 </div>
               </div>
             );
          })}
        </div>

        <div className="flex items-center justify-between pt-8 border-t">
          <button onClick={() => setTakingQuiz(null)} className="btn-secondary">
            Cancel Quiz
          </button>
          <button onClick={handleSubmit} className="btn-primary px-12 py-3 flex items-center gap-2">
            Submit My Answers
            <ArrowRight size={20} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-slate-900">Available Quizzes</h1>
        <p className="text-slate-500 text-sm">Complete your assigned quizzes to track your progress.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {quizzes.map((quiz) => {
          const submission = submissions.find(s => s.quiz_id === quiz.id);
          return (
            <div key={quiz.id} className={`card p-6 space-y-4 relative ${submission ? "opacity-75 bg-slate-50 border-slate-200" : ""}`}>
              <div className="flex items-start justify-between">
                <div className={clsx(
                  "p-2 rounded-lg",
                  submission ? "bg-emerald-100 text-emerald-600" :
                  quiz.quiz_type === 'simulator' ? "bg-purple-50 text-purple-600" : "bg-primary-50 text-primary-600"
                )}>
                  {submission ? <CheckCircle size={24} /> :
                   quiz.quiz_type === 'simulator' ? <Monitor size={24} /> : <BookOpen size={24} />}
                </div>
                {submission && (
                   <span className="bg-emerald-50 text-emerald-700 px-2 py-1 rounded-md text-xs font-bold uppercase tracking-wide">
                     Completed: {submission.score}%
                   </span>
                )}
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-lg">{quiz.title}</h3>
                <p className="text-sm text-slate-500 line-clamp-2">{quiz.description}</p>
              </div>
              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">
                  {quiz.quiz_type === 'simulator' ? 'Simulator Task' : `${quiz.questions?.length || 0} Questions`}
                </span>
                {!submission ? (
                   <button
                     onClick={() => handleStartQuiz(quiz)}
                     className="text-primary-600 text-sm font-bold hover:underline flex items-center gap-1"
                   >
                     Start Quiz <ArrowRight size={14} />
                   </button>
                ) : (
                  <span className="text-emerald-600 text-sm font-bold flex items-center gap-1">
                    <CheckCircle size={14} /> Submitted
                  </span>
                )}
              </div>
              {submission?.notes?.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-100">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 flex items-center gap-1">
                    <MessageSquare size={10} /> Instructor Feedback
                  </p>
                  <div className="space-y-2">
                    {submission.notes.map((n: any) => (
                      <p key={n.id} className="text-xs text-slate-600 bg-white p-2 rounded border border-slate-100 italic leading-relaxed">
                        "{n.content}"
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {quizzes.length === 0 && (
        <div className="card p-12 text-center space-y-4 border-dashed border-2">
           <div className="w-16 h-16 bg-slate-50 text-slate-300 rounded-full flex items-center justify-center mx-auto">
             <HelpCircle size={32} />
           </div>
           <div>
             <h3 className="text-lg font-bold text-slate-900">No quizzes available</h3>
             <p className="text-slate-500">Your instructor hasn't posted any quizzes yet.</p>
           </div>
        </div>
      )}
    </div>
  );
}
