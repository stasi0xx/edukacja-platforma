const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchCurrentUser(token: string) {
    const res = await fetch(`${API_URL}/api/me/`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    if (!res.ok) {
        throw new Error("Failed to fetch user info");
    }
    return res.json();
}
