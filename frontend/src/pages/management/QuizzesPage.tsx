import React, { useEffect, useState } from 'react';
import { apiListQuizzes, apiCreateQuiz, apiListQuizSubmissions, apiAddNote } from '../../api/api';
import { useAuthStore } from '../../store/authStore';
import { Plus, BookOpen, Clock, CheckCircle, Users, MessageSquare } from 'lucide-react';
import Modal from '../../components/Modal';

export default function QuizzesPage() {
  const { user } = useAuthStore();
  const [quizzes, setQuizzes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Submissions state
  const [selectedQuiz, setSelectedQuiz] = useState<any | null>(null);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [isSubmissionsOpen, setIsSubmissionsOpen] = useState(false);

  // Note state
  const [noteContent, setNoteContent] = useState('');
  const [activeSubmissionId, setActiveSubmissionId] = useState<number | null>(null);

  // Quiz Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [questions, setQuestions] = useState<any[]>([{ question_text: '', options: ['', '', '', ''], correct_option: 0 }]);

  const fetchQuizzes = async () => {
    try {
      const data = await apiListQuizzes();
      setQuizzes(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const handleAddQuestion = () => {
    setQuestions([...questions, { question_text: '', options: ['', '', '', ''], correct_option: 0 }]);
  };

  const handleQuestionChange = (index: number, field: string, value: any) => {
    const updated = [...questions];
    updated[index] = { ...updated[index], [field]: value };
    setQuestions(updated);
  };

  const handleOptionChange = (qIndex: number, oIndex: number, value: string) => {
    const updated = [...questions];
    updated[qIndex].options[oIndex] = value;
    setQuestions(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        title,
        description,
        questions: questions.map(q => ({
          ...q,
          options: JSON.stringify(q.options)
        }))
      };
      await apiCreateQuiz(payload);
      setIsModalOpen(false);
      fetchQuizzes();
      // Reset
      setTitle('');
      setDescription('');
      setQuestions([{ question_text: '', options: ['', '', '', ''], correct_option: 0 }]);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleViewSubmissions = async (quiz: any) => {
    setSelectedQuiz(quiz);
    try {
      const data = await apiListQuizSubmissions(quiz.id);
      setSubmissions(data);
      setIsSubmissionsOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddNote = async (studentId: number, submissionId: number) => {
    if (!noteContent.trim()) return;
    try {
      await apiAddNote({
        student_id: studentId,
        submission_id: submissionId,
        content: noteContent
      });
      setNoteContent('');
      setActiveSubmissionId(null);
      // Refresh submissions
      const data = await apiListQuizSubmissions(selectedQuiz.id);
      setSubmissions(data);
      alert("Note added successfully!");
    } catch (err: any) {
      alert(err.message);
    }
  };

  const isDoctor = user?.role === 'lab_admin' || user?.role === 'university_admin';

  if (loading) return <div className="p-8">Loading quizzes...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Quiz Management</h1>
        {isDoctor && (
          <button onClick={() => setIsModalOpen(true)} className="btn-primary flex items-center gap-2">
            <Plus size={18} />
            Create Quiz
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {quizzes.map((quiz) => (
          <div key={quiz.id} className="card p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                <BookOpen size={24} />
              </div>
              <span className="text-xs font-medium text-slate-500 flex items-center gap-1">
                <Clock size={14} />
                {new Date(quiz.created_at).toLocaleDateString()}
              </span>
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-lg">{quiz.title}</h3>
              <p className="text-sm text-slate-500 line-clamp-2">{quiz.description}</p>
            </div>
            <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-sm font-medium text-slate-600">
                {quiz.questions?.length || 0} Questions
              </span>
              <button
                onClick={() => handleViewSubmissions(quiz)}
                className="text-primary-600 text-sm font-bold hover:underline flex items-center gap-1"
              >
                <Users size={14} /> Submissions
              </button>
            </div>
          </div>
        ))}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Quiz"
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Quiz Title</label>
              <input
                type="text"
                required
                className="input-field"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Introduction to Audiometry"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1">Description</label>
              <textarea
                className="input-field min-h-[80px]"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Briefly describe what this quiz covers..."
              />
            </div>
          </div>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900">Questions</h3>
              <button
                type="button"
                onClick={handleAddQuestion}
                className="text-primary-600 text-sm font-bold flex items-center gap-1"
              >
                <Plus size={16} /> Add Question
              </button>
            </div>

            {questions.map((q, qIndex) => (
              <div key={qIndex} className="p-4 bg-slate-50 rounded-xl space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase mb-1">
                    Question {qIndex + 1}
                  </label>
                  <input
                    type="text"
                    required
                    className="input-field"
                    value={q.question_text}
                    onChange={(e) => handleQuestionChange(qIndex, 'question_text', e.target.value)}
                    placeholder="Enter question text..."
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {q.options.map((opt: string, oIndex: number) => (
                    <div key={oIndex} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name={`correct-${qIndex}`}
                        checked={q.correct_option === oIndex}
                        onChange={() => handleQuestionChange(qIndex, 'correct_option', oIndex)}
                      />
                      <input
                        type="text"
                        required
                        className="input-field text-sm py-1.5"
                        value={opt}
                        onChange={(e) => handleOptionChange(qIndex, oIndex, e.target.value)}
                        placeholder={`Option ${oIndex + 1}`}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <button type="button" onClick={() => setIsModalOpen(false)} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary px-8">
              Create Quiz
            </button>
          </div>
        </form>
      </Modal>

      {/* Submissions Modal */}
      <Modal
        isOpen={isSubmissionsOpen}
        onClose={() => setIsSubmissionsOpen(false)}
        title={`Submissions: ${selectedQuiz?.title}`}
      >
        <div className="space-y-6">
          <div className="overflow-hidden border rounded-xl">
             <table className="w-full text-left">
               <thead className="bg-slate-50 border-b">
                 <tr>
                   <th className="px-4 py-3 text-xs font-bold text-slate-500 uppercase">Student ID</th>
                   <th className="px-4 py-3 text-xs font-bold text-slate-500 uppercase text-center">Score</th>
                   <th className="px-4 py-3 text-xs font-bold text-slate-500 uppercase text-right">Actions</th>
                 </tr>
               </thead>
               <tbody className="divide-y">
                 {submissions.map((sub) => (
                   <React.Fragment key={sub.id}>
                    <tr className="hover:bg-slate-50/50">
                      <td className="px-4 py-4 font-medium text-slate-900">User #{sub.user_id}</td>
                      <td className="px-4 py-4 text-center">
                        <span className={`font-bold ${sub.score >= 70 ? 'text-emerald-600' : 'text-rose-600'}`}>
                          {sub.score}%
                        </span>
                      </td>
                      <td className="px-4 py-4 text-right">
                        <button
                          onClick={() => setActiveSubmissionId(activeSubmissionId === sub.id ? null : sub.id)}
                          className="text-primary-600 text-sm font-bold hover:underline flex items-center gap-1 ml-auto"
                        >
                          <MessageSquare size={14} /> Note
                        </button>
                      </td>
                    </tr>
                    {activeSubmissionId === sub.id && (
                      <tr>
                        <td colSpan={3} className="px-4 py-4 bg-slate-50">
                           <div className="space-y-3">
                             {sub.notes?.map((n: any) => (
                               <div key={n.id} className="text-xs bg-white p-2 rounded border text-slate-600">
                                 {n.content}
                               </div>
                             ))}
                             <div className="flex gap-2">
                               <input
                                 type="text"
                                 className="input-field py-1.5 text-sm"
                                 placeholder="Add feedback note..."
                                 value={noteContent}
                                 onChange={(e) => setNoteContent(e.target.value)}
                               />
                               <button
                                 onClick={() => handleAddNote(sub.user_id, sub.id)}
                                 className="btn-primary py-1.5 px-4 text-sm"
                               >
                                 Add
                               </button>
                             </div>
                           </div>
                        </td>
                      </tr>
                    )}
                   </React.Fragment>
                 ))}
                 {submissions.length === 0 && (
                   <tr>
                     <td colSpan={3} className="px-4 py-8 text-center text-slate-400 italic">
                       No submissions yet.
                     </td>
                   </tr>
                 )}
               </tbody>
             </table>
          </div>
        </div>
      </Modal>
    </div>
  );
}
