import React, { useState, useRef } from 'react';
import axios from 'axios';
import SelectGroup from './SelectGroup';
const API_URL = process.env.NEXT_PUBLIC_API_URL;

const AddTaskForm: React.FC = () => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [deadline, setDeadline] = useState('');
    const [group_id, setGroup] = useState('');
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');
    const [file, setFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = localStorage.getItem("access_token");
        const formData = new FormData();

        formData.append("name", name);
        formData.append("description", description);
        formData.append("deadline", deadline);
        console.log("group_id before submit", group_id);
        formData.append("group", group_id);
        if (file) formData.append("file", file);

        try {
            await axios.post(`${API_URL}/api/teacher/tasks/create/`, formData, {
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "multipart/form-data",
                },
            });

            setName("");
            setDescription("");
            setFile(null); // nie ustawiaj value na input, tylko wyczyść input przez ref (opcjonalnie)
            setDeadline("");
            setGroup("");
            setSuccess("Task created successfully");
            setTimeout(() => setSuccess(""), 3000);
        } catch (err) {
            setError("Failed to create task");
            setTimeout(() => setError(""), 3000);
        }
    };

    return (
        <div>
            <h1 className="text-2xl font-bold mb-4">➕ Add Task</h1>
            <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
                <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Task name"
                    className="w-full border rounded p-2"
                    required
                />
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Description"
                    className="w-full border rounded p-2"
                    rows={4}
                    required
                />
                <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} ref={fileInputRef} />
                <input
                    type="date"
                    value={deadline}
                    onChange={(e) => setDeadline(e.target.value)}
                    className="w-full border rounded p-2"
                    required
                />
                <SelectGroup onChange={(id: string) => setGroup(id)} />
                {success && <p className="text-green-600 text-sm">{success}</p>}
                {error && <p className="text-red-600 text-sm">{error}</p>}
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
                    Create Task
                </button>
            </form>
        </div>
    );
};

export default AddTaskForm;
