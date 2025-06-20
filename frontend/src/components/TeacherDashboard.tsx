import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import StudentList from './StudentList';
import StudentSubmissions from './StudentSubmissions';
import AddTaskForm from './AddTaskForm';

const TeacherDashboard: React.FC = () => {
    return (
        <BrowserRouter>
            <div className="min-h-screen flex bg-gray-100">
                <nav className="w-48 bg-gray-800 text-white p-4 space-y-2">
                    <Link to="/" className="block py-2 px-3 rounded hover:bg-gray-700">Student List</Link>
                    <Link to="/add-task" className="block py-2 px-3 rounded hover:bg-gray-700">Add Task</Link>
                </nav>
                <main className="flex-1 p-6">
                    <Routes>
                        <Route path="/" element={<StudentList />} />
                        <Route path="/students/:id" element={<StudentSubmissions />} />
                        <Route path="/add-task" element={<AddTaskForm />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
};

export default TeacherDashboard;
