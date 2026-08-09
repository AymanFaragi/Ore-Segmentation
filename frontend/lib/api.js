import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchSieveDimensions() {
    const response = await axios.get(`${API_BASE_URL}/dimensions/`);
    return response.data.dimensions;
}

export async function saveSieveDimensions(widthCm, heightCm) {
    const params = new URLSearchParams();
    params.append("sieve_width_cm", widthCm);
    params.append("sieve_height_cm", heightCm);

    const response = await axios.post(`${API_BASE_URL}/update_dimensions/`, params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    if (response.data.status === "error") {
        throw new Error(response.data.message ?? "Erreur lors de la mise à jour des dimensions.");
    }

    return response.data.dimensions;
}