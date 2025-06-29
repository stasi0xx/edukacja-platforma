import React, { useEffect, useState } from 'react';
import axios from 'axios';
const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface Comment {
    id: number;
    author_name: string;
    role: string;
    text: string;
    created_at: string;
}

interface Props {
    submissionId: number;
}

const CommentSection: React.FC<Props> = ({ submissionId }) => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [text, setText] = useState('');
    const [posting, setPosting] = useState(false);
    const [success, setSuccess] = useState('');

    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    const fetchComments = () => {
        if (!token) return;
        console.log("Submission ID:", submissionId);
        setLoading(true);
        axios
            .get(`${API_URL}api/teacher/submission/${submissionId}/comments/`, {
                headers: { Authorization: `Bearer ${token}` },
            })
            .then((res) => setComments(res.data))
            .catch(() => setError('Failed to load comments'))
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        if (submissionId && token) {
            fetchComments();
        }
    }, [submissionId, token]);

    const addComment = async () => {
        if (!token || !text) return;
        setPosting(true);
        setError('');
        try {
            await axios.post(
                `http://localhost:8000/api/teacher/submission/${submissionId}/add_comment/`,
                { text },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setText('');
            setSuccess('Comment added');
            fetchComments();
        } catch {
            setError('Error adding comment');
        } finally {
            setPosting(false);
            setTimeout(() => setSuccess(''), 2000);
        }
    };

    return (
        <div className="mt-2 border rounded p-4 bg-gray-50">
            {loading ? (
                <p>Loading comments...</p>
            ) : (
                <div className="max-h-60 overflow-y-auto space-y-2 mb-3">
                    {comments.map((c) => (
                        <div
                            key={c.id}
                            className={`p-2 rounded ${c.role === 'teacher' ? 'bg-blue-100' : 'bg-gray-100'}`}
                        >
                            <div className="text-sm font-semibold">
                                {c.author_name}{' '}
                                <span className="text-xs text-gray-500">({c.role})</span>
                            </div>
                            <div className="text-xs text-gray-500">
                                {new Date(c.created_at).toLocaleString()}
                            </div>
                            <p className="text-sm mt-1">{c.text}</p>
                        </div>
                    ))}
                    {comments.length === 0 && <p className="text-sm text-gray-500">No comments</p>}
                </div>
            )}
            {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
            {success && <p className="text-green-500 text-sm mb-2">{success}</p>}
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full border rounded p-2 mb-2"
                rows={3}
                placeholder="Write a comment..."
            />
            <button
                onClick={addComment}
                disabled={posting}
                className="bg-blue-600 text-white px-4 py-1 rounded disabled:opacity-60"
            >
                Post Comment
            </button>
        </div>
    );
};

export default CommentSection;
