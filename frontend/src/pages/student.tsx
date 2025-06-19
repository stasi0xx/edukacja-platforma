import { useEffect, useState } from "react";
import TaskCard from "@/components/TaskCard"; // zakładam, że TaskCard znajduje się w src/components

export default function StudentDashboard() {
    const [tasks, setTasks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedFiles, setSelectedFiles] = useState<Record<number, File | null>>({});
    const [uploading, setUploading] = useState<Record<number, boolean>>({});
    const [uploaded, setUploaded] = useState<Record<number, boolean>>({});
    const [commentText, setCommentText] = useState<Record<number, string>>({});


    useEffect(() => {
        const fetchTasks = async () => {
            const token = localStorage.getItem("access_token");
            if (!token) return;

            try {
                const res = await fetch("http://localhost:8000/api/my-tasks/", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                    },
                });

                if (!res.ok) throw new Error("Nie udało się pobrać zadań");
                const data = await res.json();
                setTasks(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchTasks();
    }, []);

    const handleFileChange = (taskId: number, file: File) => {
        setSelectedFiles(prev => ({ ...prev, [taskId]: file }));
    };

    const handleSubmit = async (taskId: number) => {
        const token = localStorage.getItem("access_token");
        const file = selectedFiles[taskId];
        if (!token || !file) return;

        setUploading(prev => ({ ...prev, [taskId]: true }));

        const formData = new FormData();
        formData.append("file", file);
        formData.append("task", taskId.toString());

        try {
            const res = await fetch("http://localhost:8000/api/submit-task/", {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                body: formData,
            });

            if (!res.ok) throw new Error("Błąd przy przesyłaniu");
            setUploaded(prev => ({ ...prev, [taskId]: true }));
        } catch (err) {
            console.error(err);
        } finally {
            setUploading(prev => ({ ...prev, [taskId]: false }));
        }
    };



    return (
        <div className="min-h-screen bg-gray-100 py-10 px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-center mb-10">
                <span className="text-4xl mr-2">📚</span>Twoje zadania
            </h1>

            {loading ? (
                <p className="text-center text-gray-500">Trwa ładowanie...</p>
            ) : tasks.length === 0 ? (
                <p className="text-center text-gray-600">Brak przydzielonych zadań</p>
            ) : (
                <div className="space-y-6 max-w-3xl mx-auto">
                    {tasks.map(task => (
                        <TaskCard
                            key={task.id}
                            task={task}
                            file={selectedFiles[task.id] || null}
                            onFileChange={(file) => handleFileChange(task.id, file)}
                            onSubmit={() => handleSubmit(task.id)}
                            isUploading={uploading[task.id] || false}
                            isUploaded={uploaded[task.id] || false}
                            commentText={commentText}
                            setCommentText={setCommentText}

                        />
                    ))}
                </div>
            )}
        </div>
    );
}
