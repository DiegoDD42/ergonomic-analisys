const API_URL = "http://localhost:8000";

export async function inferImage(file) {
    const formData = new FormData();
    formData.append("arquivo", file);

    const response = await fetch(`${API_URL}/infer`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error("Erro ao processar imagem");
    }

    return response.json();
}

export async function getHistorico() {
    const response = await fetch(`${API_URL}/historico`);
    return response.json();
}

export async function resetHistorico() {
    const response = await fetch(`${API_URL}/historico/reiniciar`, {
        method: "POST",
    });

    return response.json();
}