import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface Student {
    id: number;
    full_name: string;
    email: string;
}

const StudentList: React.FC = () => {
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        axios
            .get(`${API_URL}/api/teacher/my-students/`, {
                headers: { Authorization: `Bearer ${token}` },
            })
            .then((res) => setStudents(res.data))
            .catch(() => setError('Failed to load students'))
            .finally(() => setLoading(false));

    }, []);

    if (loading) return <p>Loading...</p>;
    if (error) return <p className="text-red-500">{error}</p>;

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">📄 Student List</h1>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-white shadow rounded">
                    <thead>
                        <tr className="bg-gray-100 text-left text-sm">
                            <th className="p-2">Full Name</th>
                            <th className="p-2">Email</th>
                            <th className="p-2"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {students.map((s) => (
                            <tr key={s.id} className="border-t">
                                <td className="p-2">{s.full_name}</td>
                                <td className="p-2">{s.email}</td>
                                <td className="p-2 text-right">
                                    <Link
                                        to={`/students/${s.id}`}
                                        className="bg-blue-600 text-white px-3 py-1 rounded"
                                    >
                                        View Submissions
                                    </Link>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StudentList;
