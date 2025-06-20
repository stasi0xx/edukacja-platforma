import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import CommentSection from './CommentSection';

interface Submission {
    id: number;
    task_name: string;
    status: string;
    submitted_at?: string | null;
    file_url?: string | null;
}

const StudentSubmissions: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const studentId = id ? parseInt(id) : null;
    const [submissions, setSubmissions] = useState<Submission[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showComments, setShowComments] = useState<Record<number, boolean>>({});

    useEffect(() => {
        if (!studentId) return;
        const token = localStorage.getItem('access_token');
        axios
            .get(`/api/teacher/student/${studentId}/submissions/`, {
                headers: { Authorization: `Bearer ${token}` },
            })
            .then((res) => setSubmissions(res.data))
            .catch(() => setError('Failed to fetch submissions'))
            .finally(() => setLoading(false));
    }, [studentId]);

    const toggleComments = (subId: number) => {
        setShowComments((p) => ({ ...p, [subId]: !p[subId] }));
    };

    if (loading) return <p>Loading...</p>;
    if (error) return <p className="text-red-500">{error}</p>;

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">📥 Student Submissions</h1>
            {submissions.length === 0 ? (
                <p>No submissions found</p>
            ) : (
                <div className="space-y-4">
                    {submissions.map((sub) => (
                        <div key={sub.id} className="p-4 border rounded shadow-sm bg-white">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="font-semibold">{sub.task_name}</h3>
                                    <p className="text-sm text-gray-600">
                                        Status:{' '}
                                        <span
                                            className={`px-2 py-0.5 rounded ${sub.status === 'submitted' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}
                                        >
                                            {sub.status}
                                        </span>
                                    </p>
                                    <p className="text-sm text-gray-500">
                                        Submitted:{' '}
                                        {sub.submitted_at ? new Date(sub.submitted_at).toLocaleDateString() : 'not submitted'}
                                    </p>
                                    {sub.file_url && (
                                        <a
                                            href={sub.file_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-blue-600 text-sm underline"
                                        >
                                            File
                                        </a>
                                    )}
                                </div>
                                <button
                                    onClick={() => toggleComments(sub.id)}
                                    className="bg-blue-600 text-white px-3 py-1 rounded h-fit"
                                >
                                    {showComments[sub.id] ? 'Hide Comments' : 'See Comments'}
                                </button>
                            </div>
                            {showComments[sub.id] && <CommentSection submissionId={sub.id} />}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default StudentSubmissions;
