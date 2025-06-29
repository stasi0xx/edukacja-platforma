import React, { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface Submission {
    id: number;
    student: number;
    task: Task;
    grade: number | null;
    file: string | null;
    status: string;
    submitted_at: string;
}

interface Task {
    id: number;
    name: string;
    description: string;
    deadline: string;
    file: string;
    created_at: string;
    status: boolean | string;
    submission_id: number | null;
    submission: Submission | null;
}

interface Comment {
    id: number;
    user: string;
    text: string;
}

interface Props {
    task: Task;
    onFileChange: (id: number, file: File | null) => void;
    onSubmit: (id: number) => void;
    uploading: boolean;
    uploaded: boolean;
}

const TaskCard = ({
    task,
    onFileChange,
    onSubmit,
    uploading,
    uploaded,
}: Props) => {
    console.log("Task w TaskCard:", task);
    const [expanded, setExpanded] = useState(false);
    const [commentText, setCommentText] = useState("");
    const [comments, setComments] = useState<Comment[]>([]);
    const [loadingComments, setLoadingComments] = useState(false);
    const [selectedImage, setSelectedImage] = useState<string | null>(null);

    const fetchComments = async () => {
        if (!task.id) {
            console.warn("Brak task.id, nie pobieram komentarzy");
            return;
        }
        const token = localStorage.getItem("access_token");
        console.log("taskID: ", task.id );
        if (!token) return;
        setLoadingComments(true);
        try {
            const res = await fetch(
                `${API_URL}/api/submissions/${task.id}/comments/`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );
            if (res.ok) {
                const data = await res.json();
                setComments(data);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoadingComments(false);
        }
    };

    const handleDownload = () => {
        if(selectedImage){    
            fetch(selectedImage, {
                mode: 'cors',
            })
                .then((res) => res.blob())
                .then((blob) => {
                    const link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = selectedImage?.split('/').pop() || 'plik.jpg';
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        }
    };

    const toggle = () => {
        if (!expanded && comments.length === 0) {
            fetchComments();
        }
        setExpanded((prev) => !prev);
    };

    const handleCommentSubmit = async (e?: React.MouseEvent) => {
        e?.stopPropagation();
        const token = localStorage.getItem("access_token");
        const comment = commentText;
        if (!comment) return;

        try {
            const res = await fetch(`${API_URL}/api/submissions/${task.id}/add_comment/`, {
                method: "PATCH",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ comment }),
            });

            if (!res.ok) throw new Error("Nie udało się zapisać komentarza");
            alert("Komentarz zapisany");
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div
            onClick={toggle}
            className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition cursor-pointer"
        >
            <h2 className="text-xl font-bold text-gray-800 mb-1">{task.name} {task.id}</h2>


            <div className="text-sm text-gray-500 space-y-1">
                <p>
                    <span className="font-medium text-gray-700">Deadline:</span> {task.deadline}
                </p>

                {task.submission?.grade !== null && (
                    <p className="text-sm text-gray-700">
                        Ocena: <span className="font-bold">{task.submission?.grade}/6</span>
                    </p>
                )}


                <p>
                    <span className="font-medium text-gray-700">Status:</span>{" "}
                    {task.submission?.status === "submitted" ? (
                        <span className="text-green-600 font-semibold">✅ Oddane</span>
                    ) : task.submission?.status === "approved" ? (
                        <span className="text-blue-600 font-semibold">🟦 Zatwierdzone</span>
                    ) : (
                        <span className="text-red-500 font-semibold">❌ Do zrobienia</span>
                    )}
                </p>
            </div>

            <div
                onClick={(e) => e.stopPropagation()}
                className={`overflow-hidden transition-all duration-300 ${expanded ? "max-h-[1000px] mt-4" : "max-h-0"}`}
            >
                <p className="text-gray-600 mb-2">{task.description}</p>
                {task.file ? (
                    <img
                        src={task.file}
                        alt="Submission File"
                        className="max-w-xs border rounded"
                        onClick={() => setSelectedImage(task.file!)}
                    />
                ) : (
                    <p>No file uploaded</p>
                )}
                {task.status !== "oddane" && (
                    <div className="mb-4">
                        <input
                            type="file"
                            onChange={(e) => onFileChange(task.id, e.target.files?.[0] || null)}
                            className="mb-2 block text-sm text-gray-700"
                        />
                        <button
                            onClick={() => onSubmit(task.id)}
                            disabled={uploading}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-60"
                        >
                            {uploading ? "Wysyłanie..." : "Wyślij plik"}
                        </button>
                        {uploaded && <p className="text-green-500 mt-2">✔️ Wysłano</p>}
                    </div>
                )}

                <div className="mb-4">
                    <textarea
                        placeholder="Dodaj komentarz do nauczyciela..."
                        className="w-full border rounded-md p-2 mb-2"
                        rows={3}
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                    />
                    <button
                        onClick={handleCommentSubmit}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                    >
                        Zapisz komentarz
                    </button>
                </div>

                <div className="space-y-2">
                    {loadingComments ? (
                        <p className="text-sm text-gray-500">Ładowanie komentarzy...</p>
                    ) : (
                        comments.map((c) => (
                            <div key={c.id} className="text-sm border-b pb-1">
                                <span className="font-semibold mr-1">{c.user}:</span>
                                {c.text}
                            </div>
                        ))
                    )}
                </div>
            </div>
            {selectedImage && (
                <div className="fixed inset-0 bg-black bg-opacity-80 z-50 flex justify-center items-center" onClick={() => setSelectedImage(null)}>
                    <button
                        onClick={handleDownload}
                        className="absolute top-6 right-6 bg-white p-2 rounded-full shadow-lg hover:bg-gray-100 transition"
                        title="Pobierz zdjęcie"
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-6 w-6 text-gray-800"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth={2}
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" />
                        </svg>
                    </button>

                    <img src={selectedImage} alt="Full Preview" className="max-h-[90%] max-w-[90%] rounded shadow-lg" />
                </div>
            )}
        </div>
    );
};

export default TaskCard;
