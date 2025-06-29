import { useEffect, useState } from "react";
import axios from "axios";
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function SelectGroup({ onChange }) {
    const [groups, setGroups] = useState([]);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) return;
        axios.get(`${API_URL}/api/teacher/my-groups/`, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }).then((res) => {
            setGroups(res.data);
        });
    }, []);

    return (
        <select onChange={(e) => onChange(e.target.value)} required className="w-full border rounded p-2">
            <option value="">---Wybierz grupę---</option>
            {groups.map((group) => (
                <option key={group.id} value={group.id}>
                    {group.name}
                </option>
            ))}
        </select>
    );
}