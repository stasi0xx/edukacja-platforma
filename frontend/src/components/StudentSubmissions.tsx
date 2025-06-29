import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import CommentSection from './CommentSection';
const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface Submission {
    id: number;
    student: number;
    task: {
        id: number;
        name: string;
        description: string;
        file: string;
    };
    grade: number | null;
    file: string;
    status: string;
    submitted_at: string;
}

const StudentSubmissions: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const studentId = id ? parseInt(id) : null;
    const [submissions, setSubmissions] = useState<Submission[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showComments, setShowComments] = useState<Record<number, boolean>>({});
    const [expandedSubId, setExpandedSubId] = useState<number | null>(null);
    const [selectedImage, setSelectedImage] = useState<string | null>(null);

    useEffect(() => {
        if (!studentId) return;
        const token = localStorage.getItem('access_token');
        axios
            .get(`${API_URL}/api/submissions/?student=${studentId}`, {
                headers: { Authorization: `Bearer ${token}` },
            })
            .then((res) => {
                console.log("RESPONSE DATA", res.data);
                setSubmissions(res.data);
            })
            .catch(() => setError('Failed to fetch submissions'))
            .finally(() => setLoading(false));
    }, [studentId]);


    const handleApprove = (submissionId: number) => {
        const token = localStorage.getItem('access_token');

        axios
            .patch(
                `${API_URL}/api/submissions/${submissionId}/`,
                { status: 'approved' },
                { headers: { Authorization: `Bearer ${token}` } }
            )
            .then((res) => {
                // lokalna aktualizacja stanu
                setSubmissions((prev) =>
                    prev.map((s) =>
                        s.id === submissionId ? { ...s, status: 'approved' } : s
                    )
                );
            })
            .catch((err) => {
                console.error('Approval error', err);
            });
    };

    const handleGrade = async (submissionId: number, grade: number) => {
        const token = localStorage.getItem("access_token");

        await axios.patch(
            `${API_URL}/api/submissions/${submissionId}/set_grade/`,
            { grade },
            {
                headers: { Authorization: `Bearer ${token}` },
            }
        );
    };

    const toggleDetails = (id: number) => {
        setExpandedSubId(expandedSubId === id ? null : id);
    };

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
                                    <h3
                                        className="font-semibold cursor-pointer hover:underline"
                                        onClick={() => toggleDetails(sub.id)}
                                    >
                                        {sub.task.name}
                                    </h3>
                                    {expandedSubId === sub.id && (
                                        <div className="mt-2 space-y-2 bg-gray-50 p-3 rounded shadow-inner">
                                            {/* Załącznik */}
                                            {sub.file ? (
                                                <img
                                                    src={sub.file}
                                                    alt="Submission File"
                                                    className="max-w-xs border rounded"
                                                    onClick={() => setSelectedImage(sub.file!)}
                                                />
                                            ) : (
                                                <p>No file uploaded</p>
                                            )}

                                            {/* Przycisk Zatwierdzenia */}

                                            <div>
                                                <strong>Ocena:</strong>{" "}
                                                {sub.grade !== null && sub.grade !== undefined
                                                    ? `${sub.grade} pkt`
                                                    : "Brak oceny"}
                                            </div>

                                            <select
                                                onChange={(e) => handleGrade(sub.id, parseInt(e.target.value))}
                                                value={sub.grade ?? ''}
                                            >
                                                <option value="">– wybierz ocenę –</option>
                                                {[0, 1, 2, 3, 4, 5, 6].map((g) => (
                                                    <option key={g} value={g}>
                                                        {g} pkt
                                                    </option>
                                                ))}
                                            </select>
                                            <button
                                                onClick={() => handleApprove(sub.id)}
                                                className="bg-green-600 text-white px-4 py-1 rounded"
                                            >
                                                Zatwierdź zadanie
                                            </button>
                                        </div>
                                    )}
                                    <p className="text-sm text-gray-600">
                                        Status:{' '}
                                        {sub.status === "submitted" ? (
                                            <span className="text-red-600 font-semibold">Do zatwierdzenia</span>
                                        ) : sub.status === "approved" ? (
                                            <span className="text-blue-600 font-semibold">🟦 Zatwierdzone</span>
                                        ) : (
                                            <span className="text-gray-400">Nieoddane</span>
                                        )}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                        Submitted:{' '}
                                        {sub.submitted_at ? new Date(sub.submitted_at).toLocaleDateString() : 'not submitted'}
                                    </p>
                                </div>
                                <button
                                    onClick={() => toggleComments(sub.id)}
                                    className="bg-blue-600 text-white px-3 py-1 rounded h-fit"
                                >
                                    {showComments[sub.id] ? 'Zwiń komentarze' : 'Pokaż komentarze'}
                                </button>
                            </div>

                            {showComments[sub.id] && <CommentSection key={sub.id} submissionId={sub.id} />}
                        </div>
                    ))}
                </div>
            )}
            {selectedImage && (
                <div className="fixed inset-0 bg-black bg-opacity-80 z-50 flex justify-center items-center" onClick={() => setSelectedImage(null)}>
                    <img src={selectedImage} alt="Full Preview" className="max-h-[90%] max-w-[90%] rounded shadow-lg" />
                </div>
            )}
        </div>
    );
};

export default StudentSubmissions;
