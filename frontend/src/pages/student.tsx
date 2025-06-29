import { useEffect, useState } from "react";
import TaskCard from "@/components/TaskCard"; // zakładam, że TaskCard znajduje się w src/components

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

interface RankingEntry {
    student_id?: number;      // Dodaj to pole!
    student_name?: string;
    name?: string;
    score?: number;
    points?: number;
    student?: number;         // Jeśli gdzieś używasz r.student
}
interface MyPosition {
    rank: number;
    data: RankingEntry;
  }
  
  interface RankingResponse {
    top: RankingEntry[];
    my_position: MyPosition | null;
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
    const [rankingData, setRankingData] = useState<RankingResponse | null>(null);
    const [user, setUser] = useState(null);


    useEffect(() => {
        const token = localStorage.getItem("access_token");
            if (!token) return;
        
            const fetchUserAndRanking = async () => {
                try {
                    // 1. Pobierz użytkownika
                    const resUser = await fetch(`${API_URL}/api/my`, {
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    const userData = await resUser.json();
                    setUser(userData);
        
                    // 2. Pobierz ranking po groupId
                    setRankingLoading(true);
                    const resRanking = await fetch(`${API_URL}/api/ranking/group/${userData.group_id}`, {
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    if (!resRanking.ok) {
                        const text = await resRanking.text();
                        throw new Error(`Błąd API: ${resRanking.status} ${text}`);
                    }
                    const rankingData = await resRanking.json();
                    setRankingData(rankingData);
                } catch (err) {
                    console.error("Błąd przy pobieraniu danych", err);
                } finally {
                    setRankingLoading(false);
                }
            };
        
            const fetchTasks = async () => {
                try {
                    const res = await fetch(`${API_URL}/api/my-tasks/`, {
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
                    console.log("Task w student:", tasks);
                }
            };
        
            fetchUserAndRanking();
            fetchTasks();
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
        formData.append("status", "submitted");

        try {
            const res = await fetch(`${API_URL}/api/submit-task/`, {
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
                <span className="text-4xl mr-2">📚</span>
                Twoje zadania
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
                    {(showAll ? tasks : tasks.filter(task => task.id !== undefined && task.id !== null).slice(0, 3)).map((task) => {
                        console.log("TASK przekazywany do TaskCard:", task);
                        return (
                            <TaskCard
                                key={task.id}
                                task={task}
                                onFileChange={handleFileChange}
                                onSubmit={() => handleSubmit(task.id)}
                                uploading={uploading[task.id] || false}
                                uploaded={uploaded[task.id] || false}
                            />
                        );
                    })}
                </div>
            )}

            <section className="max-w-3xl mx-auto mt-12">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                    <span className="text-yellow-400 text-3xl">🏆</span>
                    Ranking uczniów
                </h2>

                {rankingLoading ? (
                    <p className="text-gray-500">Ładowanie...</p>
                ) : (
                    <>
                        {/* TOP 3 */}
                        <ol className="space-y-2">
                            {rankingData?.top.map((r, idx) => {
                                let bg, icon;
                                if (idx === 0) {
                                    bg = "bg-yellow-200 border-yellow-400";
                                    icon = "🥇";
                                } else if (idx === 1) {
                                    bg = "bg-gray-200 border-gray-400";
                                    icon = "🥈";
                                } else if (idx === 2) {
                                    bg = "bg-orange-200 border-orange-400";
                                    icon = "🥉";
                                } else {
                                    bg = "bg-white";
                                    icon = "";
                                }
                                return (
                                    <li
                                        key={r.student_id}
                                        className={`flex items-center justify-between rounded-lg border-l-8 ${bg} px-4 py-2 shadow-sm`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">{icon}</span>
                                            <span className="font-bold text-lg">{idx + 1}.</span>
                                            <span className="font-semibold">{r.student_name}</span>
                                        </div>
                                        <span className="text-lg font-mono text-gray-700">{r.points} pkt</span>
                                    </li>
                                );
                            })}
                        </ol>

                        {/* Separator */}
                        {rankingData?.my_position?.data &&
                            !rankingData.top.some(
                                (t) => t.student === rankingData.my_position!.data!.student
                            ) && (
                            <div className="mt-6">
                                <div className="border-t border-gray-300 my-4"></div>
                                <div
                                    className="flex items-center justify-between rounded-lg border-l-8 border-blue-400 bg-blue-100 px-4 py-2 shadow"
                                    style={{ animation: "pulse 1.5s infinite" }}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl text-blue-500">⭐</span>
                                        <span className="font-bold text-lg">
                                            {rankingData.my_position.rank}.
                                        </span>
                                        <span className="font-semibold">
                                            {rankingData.my_position.data.student_name}
                                        </span>
                                        <span className="ml-2 text-xs bg-blue-200 text-blue-800 px-2 py-0.5 rounded-full">
                                            Ty
                                        </span>
                                    </div>
                                    <span className="text-lg font-mono text-blue-700">
                                        {rankingData.my_position.data.points} pkt
                                    </span>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </section>
        </div>
    );
}
