export async function fetchCurrentUser(token: string) {
    const res = await fetch("http://localhost:8000/api/me/", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    if (!res.ok) {
        throw new Error("Failed to fetch user info");
    }
    return res.json();
}
