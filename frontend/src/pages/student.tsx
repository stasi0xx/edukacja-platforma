import { useEffect, useState } from "react";
import TaskCard from "@/components/TaskCard"; // zakładam, że TaskCard znajduje się w src/components

interface Task {
    id: number;
    name: string;
    description: string;
    deadline: string;
    status: string;
}

interface RankingEntry {
    student_name?: string;
    name?: string;
    score?: number;
    points?: number;
}

export default function StudentDashboard() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedFiles, setSelectedFiles] = useState<Record<number, File | null>>({});
    const [uploading, setUploading] = useState<Record<number, boolean>>({});
    const [uploaded, setUploaded] = useState<Record<number, boolean>>({});
    const [showAll, setShowAll] = useState(false);
    const [ranking, setRanking] = useState<RankingEntry[]>([]);
    const [rankingLoading, setRankingLoading] = useState(true);


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

        const fetchRanking = async () => {
            const token = localStorage.getItem("access_token");
            if (!token) return;

            try {
                const res = await fetch("http://localhost:8000/api/top-ranking/", {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (res.ok) {
                    const data = await res.json();
                    setRanking(data);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setRankingLoading(false);
            }
        };

        fetchTasks();
        fetchRanking();
    }, []);

    const handleFileChange = (taskId: number, file: File | null) => {
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
                    {tasks.length > 3 && (
                        <div className="flex justify-end">
                            <button
                                onClick={() => setShowAll((p) => !p)}
                                className="text-blue-600 text-sm hover:underline"
                            >
                                {showAll ? "Pokaż mniej" : "Zobacz wszystkie"}
                            </button>
                        </div>
                    )}
                    {(showAll ? tasks : tasks.slice(0, 3)).map((task) => (
                        <TaskCard
                            key={task.id}
                            task={task}
                            onFileChange={handleFileChange}
                            onSubmit={() => handleSubmit(task.id)}
                            uploading={uploading[task.id] || false}
                            uploaded={uploaded[task.id] || false}
                        />
                    ))}
                </div>
            )}

            <section className="max-w-3xl mx-auto mt-12">
                <h2 className="text-2xl font-bold mb-4">📊 Ranking uczniów</h2>
                {rankingLoading ? (
                    <p className="text-gray-500">Ładowanie...</p>
                ) : (
                    <ol className="space-y-1">
                        {ranking.map((r, idx) => (
                            <li key={idx}>
                                {idx + 1}. {r.student_name || r.name} – {r.score ?? r.points} zadań
                            </li>
                        ))}
                    </ol>
                )}
            </section>
        </div>
    );
}
