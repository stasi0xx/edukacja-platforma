import React, { useState } from "react";

interface Task {
    id: number;
    name: string;
    description: string;
    deadline: string;
    status: string;
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
    const [expanded, setExpanded] = useState(false);
    const [commentText, setCommentText] = useState("");
    const [comments, setComments] = useState<Comment[]>([]);
    const [loadingComments, setLoadingComments] = useState(false);

    const fetchComments = async () => {
        const token = localStorage.getItem("access_token");
        if (!token) return;
        setLoadingComments(true);
        try {
            const res = await fetch(
                `http://localhost:8000/api/submissions/${task.id}/comments/`,
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
            const res = await fetch(`http://localhost:8000/api/submissions/${task.id}/add_comment/`, {
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
            <h2 className="text-xl font-bold text-gray-800 mb-1">{task.name}</h2>
            <p className="text-gray-600 mb-2">{task.description}</p>

            <div className="text-sm text-gray-500 space-y-1">
                <p>
                    <span className="font-medium text-gray-700">Deadline:</span> {task.deadline}
                </p>
                <p>
                    <span className="font-medium text-gray-700">Status:</span>{" "}
                    {task.status === "oddane" ? (
                        <span className="text-green-600 font-semibold">✅ Oddane</span>
                    ) : (
                        <span className="text-red-500 font-semibold">❌ Do zrobienia</span>
                    )}
                </p>
            </div>

            <div
                onClick={(e) => e.stopPropagation()}
                className={`overflow-hidden transition-all duration-300 ${expanded ? "max-h-[1000px] mt-4" : "max-h-0"}`}
            >
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
        </div>
    );
};

export default TaskCard;
