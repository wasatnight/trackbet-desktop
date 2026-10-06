import { API_URL } from "../config/api";

export async function obtenerApuestas(signal) {
  const respuesta = await fetch(`${API_URL}/apuestas`, {
    signal,
  });

  if (!respuesta.ok) {
    throw new Error(`La API respondió con el código ${respuesta.status}.`);
  }

  const datos = await respuesta.json();

  if (Array.isArray(datos)) {
    return datos;
  }

  if (Array.isArray(datos.apuestas)) {
    return datos.apuestas;
  }

  return [];
}
