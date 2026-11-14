
// ========================================
// ARTSCOPE - DIGITAL ART LAB
// ========================================

// Dirección base del backend FastAPI
const API_BASE_URL = "https://jubilant-doodle-q7jqrx65774ph67wg-8000.app.github.dev";


// ========================================
// ELEMENTOS DEL HTML
// ========================================

// Estado del servidor
const serverStatus = document.getElementById("server-status");
const statusText = document.getElementById("status-text");

// Elementos de carga
const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const imageInformation = document.getElementById("image-information");

// Áreas de visualización
const originalFrame = document.getElementById("original-frame");
const resultFrame = document.getElementById("result-frame");

// Botones
const btnProcess = document.getElementById("btn-process");
const btnAnalysis = document.getElementById("btn-analysis");
const btnEdges = document.getElementById("btn-edges");
const btnRestore = document.getElementById("btn-restore");

// Acciones sobre las imágenes
const imageActions = document.getElementById("image-actions");
const btnReset = document.getElementById("btn-reset");
const btnDownload = document.getElementById("btn-download");

// Notificaciones
const notifications = document.getElementById("notifications");


// ========================================
// ESTADO DE LA APLICACIÓN
// ========================================

let currentImage = null;
let currentResult = null;

let currentFileName = null;


// ========================================
// VERIFICAR CONEXIÓN CON EL BACKEND
// ========================================

async function checkServerStatus() {

    try {

        const response = await fetch(`${API_BASE_URL}/health`);

        if (!response.ok) {
            throw new Error("El servidor respondió con un error.");
        }

        const data = await response.json();

        serverStatus.querySelector(".status-dot").classList.add("online");
        statusText.textContent = "Servidor conectado";

        console.log("Estado del servidor:", data);

    } catch (error) {

        serverStatus.querySelector(".status-dot").classList.remove("online");
        statusText.textContent = "Servidor desconectado";

        console.error("Error de conexión:", error);

    }

}


// ========================================
// INICIAR APLICACIÓN
// ========================================

checkServerStatus();



// ========================================
// CARGA DE IMÁGENES
// ========================================

async function uploadImage(file) {

    // Validar que exista un archivo
    if (!file) {
        return;
    }

    // Validar formato
    const allowedTypes = [
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/bmp"
    ];

    if (!allowedTypes.includes(file.type)) {
        showNotification("Formato de imagen no permitido.", "error");
        return;
    }

    // Validar tamaño máximo: 10 MB
    if (file.size > 10 * 1024 * 1024) {
        showNotification("La imagen supera el límite de 10 MB.", "error");
        return;
    }

    try {

        showNotification("Subiendo imagen...", "success");

        // Crear el formulario que enviará el archivo
        const formData = new FormData();
        formData.append("file", file);

        // Enviar imagen al backend
        const response = await fetch(`${API_BASE_URL}/images`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "No se pudo cargar la imagen."
            );
        }

        // Convertir respuesta JSON
        const data = await response.json();

        // Guardar información de la imagen
        currentFileName = data.stored_image.file_name;
        currentImage = data;

        // Construir dirección de la imagen almacenada
        const imageUrl = `${API_BASE_URL}${data.stored_image.url}`;

        // Mostrar imagen original
        displayImage(originalFrame, imageUrl, "Imagen original");

        // Limpiar resultado anterior
        resultFrame.replaceChildren();

        const placeholder = document.createElement("span");
        placeholder.textContent =
            "Aplicá una operación para ver el resultado.";

        resultFrame.appendChild(placeholder);

        currentResult = null;

        // Mostrar información técnica
        imageInformation.innerHTML = `
            <p><strong>Archivo:</strong> ${file.name}</p>
            <p><strong>Formato:</strong> ${data.image_info.format}</p>
            <p><strong>Dimensiones:</strong>
                ${data.image_info.width} × ${data.image_info.height}
            </p>
            <p><strong>Tamaño:</strong>
                ${(file.size / 1024).toFixed(2)} KB
            </p>
        `;

        // Habilitar herramientas
        btnProcess.disabled = false;
        btnAnalysis.disabled = false;
        btnEdges.disabled = false;

        imageActions.hidden = true;

        showNotification(
            "Imagen cargada correctamente.",
            "success"
        );

        console.log("Imagen cargada:", data);

    } catch (error) {

        console.error("Error al cargar imagen:", error);

        showNotification(error.message, "error");

    }

}


// ========================================
// MOSTRAR IMÁGENES EN LA INTERFAZ
// ========================================

function displayImage(container, imageUrl, altText) {

    const image = document.createElement("img");

    image.src = imageUrl;
    image.alt = altText;

    container.replaceChildren(image);

}


// ========================================
// SISTEMA DE NOTIFICACIONES
// ========================================

function showNotification(message, type = "success") {

    const notification = document.createElement("div");

    notification.className = `notification ${type}`;
    notification.textContent = message;

    notifications.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 4000);

}


// ========================================
// EVENTO DE SELECCIÓN DE ARCHIVO
// ========================================

fileInput.addEventListener("change", (event) => {

    const file = event.target.files[0];

    uploadImage(file);

});
