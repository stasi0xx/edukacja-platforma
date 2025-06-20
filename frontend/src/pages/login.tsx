// src/pages/login.tsx
import { useState } from "react"
import { useRouter } from "next/router"
import { fetchCurrentUser } from "@/lib/api"

const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function LoginPage() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const router = useRouter()

    const handleLogin = async () => {
        try {
            const res = await fetch(`${API_URL}/api/token/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            })

            const data = await res.json()
            if (res.ok) {
                localStorage.setItem("access_token", data.access)
                localStorage.setItem("refresh_token", data.refresh)

                try {
                    const user = await fetchCurrentUser(data.access)
                    localStorage.setItem("user_role", user.role)
                    if (user.role === "student") {
                        router.push("/student")
                    } else if (user.role === "teacher") {
                        router.push("/teacher")
                    } else {
                        router.push("/")
                    }
                } catch (e) {
                    console.error(e)
                    router.push("/")
                }
            } else {
                setError(data.detail || "Błędne dane logowania")
            }
        } catch (err) {
            console.error(err)
            setError("Błąd połączenia z API")
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
            <div className="bg-gray-800 p-8 rounded shadow-md w-96">
                <h1 className="text-2xl font-bold mb-4">Logowanie</h1>
                <input
                    className="w-full p-2 mb-4 rounded bg-gray-700 text-white"
                    type="text"
                    placeholder="Nazwa użytkownika"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    className="w-full p-2 mb-4 rounded bg-gray-700 text-white"
                    type="password"
                    placeholder="Hasło"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                {error && <p className="text-red-400 mb-2">{error}</p>}
                <button
                    onClick={handleLogin}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
                >
                    Zaloguj się
                </button>
            </div>
        </div>
    )
}
