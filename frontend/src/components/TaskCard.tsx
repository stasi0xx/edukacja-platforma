import React from "react";

interface Task {
    id: number;
    name: string;
    description: string;
    deadline: string;
    status: string;
}

interface Props {
    task: Task;
    onFileChange: (id: number, file: File) => void;
    onSubmit: (id: number) => void;
    uploading: boolean;
    uploaded: boolean;
    commentText: Record<number, string>;
    setCommentText: React.Dispatch<React.SetStateAction<Record<number, string>>>;
}

const TaskCard = ({
    task,
    onFileChange,
    onSubmit,
    uploading,
    uploaded,
    commentText,
    setCommentText,
}: Props) => {
    const handleCommentSubmit = async () => {
        const token = localStorage.getItem("access_token");
        const comment = commentText[task.id];
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
        <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
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

            {task.status !== "oddane" && (
                <div className="mt-4">
                    <input
                        type="file"
                        onChange={(e) => onFileChange(task.id, e.target.files?.[0] || null)}
                        className="mb-2 block text-sm text-gray-700"
                    />
                    <button
                        onClick={() => onSubmit(task.id)}
                        disabled={uploading}
                        className="px-4 py-2 bg-brand-blue text-white rounded-md hover:bg-brand-light transition disabled:opacity-60"
                    >
                        {uploading ? "Wysyłanie..." : "Wyślij plik"}
                    </button>
                    {uploaded && <p className="text-green-500 mt-2">✔️ Wysłano</p>}
                </div>
            )}

            <div className="mt-4">
                <textarea
                    placeholder="Dodaj komentarz do nauczyciela..."
                    className="w-full border rounded-md p-2 mb-2"
                    rows={3}
                    value={commentText[task.id] || ""}
                    onChange={(e) =>
                        setCommentText((prev) => ({
                            ...prev,
                            [task.id]: e.target.value,
                        }))
                    }
                />
                <button
                    onClick={handleCommentSubmit}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
                >
                    Zapisz komentarz
                </button>
            </div>
        </div>
    );
};

export default TaskCard;
