import React, { useState } from 'react';
import axios from 'axios';

const AddTaskForm: React.FC = () => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [deadline, setDeadline] = useState('');
    const [group, setGroup] = useState('');
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = localStorage.getItem('access_token');
        try {
            await axios.post(
                '/api/teacher/tasks/create/',
                { name, description, deadline, group },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setName('');
            setDescription('');
            setDeadline('');
            setGroup('');
            setSuccess('Task created successfully');
            setTimeout(() => setSuccess(''), 3000);
        } catch {
            setError('Failed to create task');
            setTimeout(() => setError(''), 3000);
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
                <input
                    type="date"
                    value={deadline}
                    onChange={(e) => setDeadline(e.target.value)}
                    className="w-full border rounded p-2"
                    required
                />
                <input
                    value={group}
                    onChange={(e) => setGroup(e.target.value)}
                    placeholder="Group"
                    className="w-full border rounded p-2"
                    required
                />
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
