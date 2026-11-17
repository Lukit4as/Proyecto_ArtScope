
// ========================================
// ARTSCOPE - DIGITAL ART LAB
// ========================================

// Dirección del backend
// Local: utiliza el servidor de desarrollo.
// Producción: utiliza el backend publicado en Render.
const API_BASE_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : "https://proyecto-artscope.onrender.com";


// ========================================
// 1. ELEMENTOS DEL HTML
// ========================================

// Servidor
const serverStatus = document.getElementById("server-status");
const statusText = document.getElementById("status-text");

// Carga de imágenes
const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const imageInformation = document.getElementById("image-information");

// Visualización
const originalFrame = document.getElementById("original-frame");
const resultFrame = document.getElementById("result-frame");

// Botones
const btnProcess = document.getElementById("btn-process");
const btnAnalysis = document.getElementById("btn-analysis");
const btnEdges = document.getElementById("btn-edges");
const btnRestore = document.getElementById("btn-restore");

const btnReset = document.getElementById("btn-reset");
const btnDownload = document.getElementById("btn-download");
const imageActions = document.getElementById("image-actions");

// Procesamiento
const operationSelect = document.getElementById("operation-select");
const operationParameters = document.getElementById("operation-parameters");

// Restauración
const restorationSelect = document.getElementById("restoration-select");
const restorationParameters = document.getElementById("restoration-parameters");

// Controles de Inpainting
const inpaintingControls = document.getElementById("inpainting-controls");
const brushSizeInput = document.getElementById("brush-size");
const brushSizeValue = document.getElementById("brush-size-value");
const clearMaskButton = document.getElementById("btn-clear-mask");

// Análisis
const colorHistogram = document.getElementById("color-histogram");
const grayscaleHistogram = document.getElementById("grayscale-histogram");
const imageStatistics = document.getElementById("image-statistics");

// Detección de bordes
const threshold1Input = document.getElementById("threshold1");
const threshold2Input = document.getElementById("threshold2");
const threshold1Value = document.getElementById("threshold1-value");
const threshold2Value = document.getElementById("threshold2-value");

// Notificaciones
const notifications = document.getElementById("notifications");


// ========================================
// 2. ESTADO DE LA APLICACIÓN
// ========================================

let currentImage = null;
let currentResult = null;
let currentFileName = null;

// Controlador independiente del pincel de Inpainting.
const inpaintingTool =
    window.ArtScopeInpainting &&
    originalFrame &&
    brushSizeInput &&
    brushSizeValue &&
    clearMaskButton
        ? window.ArtScopeInpainting.create({
            originalFrame,
            brushSizeInput,
            brushSizeValue,
            clearButton: clearMaskButton
        })
        : null;

if (!inpaintingTool) {
    console.error(
        "No se pudo inicializar Inpainting. Revisá inpainting.js y los controles del HTML."
    );
} else {
    // El módulo avisa cuando el usuario dibuja o limpia la máscara.
    inpaintingTool.setSelectionCallback((hasSelection) => {
        btnRestore.disabled =
            !currentFileName ||
            restorationSelect.value !== "inpainting" ||
            !hasSelection;
    });
}


// ========================================
// 3. CONEXIÓN CON EL BACKEND
// ========================================

async function checkServerStatus() {

    try {

        const response = await fetch(`${API_BASE_URL}/health`);

        if (!response.ok) {
            throw new Error("Error de conexión con el servidor.");
        }

        const data = await response.json();

        serverStatus.querySelector(".status-dot").classList.add("online");
        statusText.textContent = "Servidor conectado";

        console.log("Servidor:", data);

    } catch (error) {

        serverStatus.querySelector(".status-dot").classList.remove("online");
        statusText.textContent = "Servidor desconectado";

        console.error("Error de conexión:", error);

    }
}


// ========================================
// 4. NOTIFICACIONES
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
// 5. VISUALIZACIÓN DE IMÁGENES
// ========================================

function displayImage(container, imageUrl, altText) {

    const image = document.createElement("img");

    image.src = imageUrl;
    image.alt = altText;

    container.replaceChildren(image);

}


// ========================================
// 6. CARGA DE IMÁGENES
// ========================================

async function uploadImage(file) {

    if (!file) return;

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

    if (file.size > 10 * 1024 * 1024) {
        showNotification("La imagen supera el límite de 10 MB.", "error");
        return;
    }

    // Evitar conservar una máscara asociada a la imagen anterior.
    if (inpaintingTool) {
        inpaintingTool.disable();
    }

    if (inpaintingControls) {
        inpaintingControls.hidden = true;
    }

    try {

        showNotification("Subiendo imagen...", "success");

        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE_URL}/images`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "No se pudo cargar la imagen.");
        }

        currentImage = data;
        currentFileName = data.stored_image.file_name;
        currentResult = null;

        const imageUrl = `${API_BASE_URL}${data.stored_image.url}`;

        // Mostrar original
        displayImage(
            originalFrame,
            imageUrl,
            "Imagen original"
        );

        // Limpiar resultado anterior
        resultFrame.innerHTML =
            "<span>Aplicá una operación para ver el resultado.</span>";

        // Información técnica
        imageInformation.innerHTML = `
            <p><strong>Archivo:</strong> ${file.name}</p>

            <p><strong>Formato:</strong>
                ${data.image_info.format}
            </p>

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

        // Actualizar controles
        renderOperationParameters();
        renderRestorationParameters();

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
// 7. PROCESAMIENTO DE IMÁGENES
// ========================================

function renderOperationParameters() {

    const operation = operationSelect.value;
    let html = "";

    switch (operation) {

        case "brightness":

            html = `
                <label for="beta">Nivel de brillo</label>
                <input type="number" id="beta"
                    min="-100" max="100" value="30">
            `;
            break;

        case "contrast":

            html = `
                <label for="alpha">Nivel de contraste</label>
                <input type="number" id="alpha"
                    min="0" max="3" step="0.1" value="1.5">
            `;
            break;

        case "blur":

            html = `
                <label for="kernel-size">Tamaño del desenfoque</label>
                <input type="number" id="kernel-size"
                    min="1" max="31" step="2" value="5">
                <small>Utilizá un número impar.</small>
            `;
            break;

        case "sharpen":

            html = `
                <p>Se aplicará un filtro para resaltar los detalles.</p>
            `;
            break;

        case "rotation":

            html = `
                <label for="angle">Ángulo de rotación</label>
                <input type="number" id="angle" value="90">
            `;
            break;

        case "resize":

            const width = currentImage
                ? currentImage.image_info.width : 800;

            const height = currentImage
                ? currentImage.image_info.height : 600;

            html = `
                <label for="width">Ancho (px)</label>
                <input type="number" id="width" min="1" value="${width}">

                <label for="height">Alto (px)</label>
                <input type="number" id="height" min="1" value="${height}">

                <label for="interpolation">Interpolación</label>

                <select id="interpolation">
                    <option value="linear">Lineal</option>
                    <option value="nearest">Vecino más cercano</option>
                    <option value="cubic">Cúbica</option>
                </select>

                <label>
                    <input type="checkbox" id="keep-aspect-ratio">
                    Mantener proporción
                </label>
            `;
            break;

    }

    operationParameters.innerHTML = html;

}


function getOperationParameters() {

    switch (operationSelect.value) {

        case "brightness":
            return {
                beta: Number(document.getElementById("beta").value)
            };

        case "contrast":
            return {
                alpha: Number(document.getElementById("alpha").value)
            };

        case "blur":
            return {
                kernel_size: Number(
                    document.getElementById("kernel-size").value
                )
            };

        case "sharpen":
            return {};

        case "rotation":
            return {
                angle: Number(document.getElementById("angle").value)
            };

        case "resize":
            return {
                width: Number(document.getElementById("width").value),
                height: Number(document.getElementById("height").value),
                interpolation: document.getElementById("interpolation").value,
                keep_aspect_ratio:
                    document.getElementById("keep-aspect-ratio").checked
            };

        default:
            return {};

    }

}


async function processImage() {

    if (!currentFileName) {
        showNotification("Primero cargá una imagen.", "error");
        return;
    }

    try {

        btnProcess.disabled = true;

        const operation = operationSelect.value;
        const parameters = getOperationParameters();

        showNotification("Procesando imagen...", "success");

        const response = await fetch(
            `${API_BASE_URL}/images/${encodeURIComponent(currentFileName)}/operations`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    operation,
                    parameters
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Error al procesar la imagen.");
        }

        currentResult = data;

        const resultUrl = `${API_BASE_URL}${data.url}`;

        displayImage(
            resultFrame,
            resultUrl,
            "Imagen procesada"
        );

        btnDownload.href = resultUrl;
        btnDownload.download = data.file_name;

        imageActions.hidden = false;

        showNotification(
            "Procesamiento completado.",
            "success"
        );

        console.log("Resultado del procesamiento:", data);

    } catch (error) {

        console.error("Error de procesamiento:", error);
        showNotification(error.message, "error");

    } finally {

        btnProcess.disabled = !currentFileName;

    }

}


// ========================================
// 8. ANÁLISIS DE IMÁGENES
// ========================================

function drawHistogram(canvas, datasets, colors) {

    const context = canvas.getContext("2d");

    const width = canvas.clientWidth || 500;
    const height = 220;
    const ratio = window.devicePixelRatio || 1;

    canvas.width = width * ratio;
    canvas.height = height * ratio;

    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

    const padding = 30;
    const graphWidth = width - padding * 2;
    const graphHeight = height - padding * 2;

    const maximum = Math.max(
        1,
        ...datasets.flatMap(dataset => dataset)
    );

    // Ejes
    context.strokeStyle = "#888";
    context.lineWidth = 1;

    context.beginPath();
    context.moveTo(padding, padding);
    context.lineTo(padding, height - padding);
    context.lineTo(width - padding, height - padding);
    context.stroke();

    // Curvas
    datasets.forEach((dataset, index) => {

        context.beginPath();
        context.strokeStyle = colors[index];
        context.lineWidth = 1.5;

        dataset.forEach((value, position) => {

            const x = padding +
                (position / (dataset.length - 1)) * graphWidth;

            const y = height - padding -
                (value / maximum) * graphHeight;

            if (position === 0) {
                context.moveTo(x, y);
            } else {
                context.lineTo(x, y);
            }

        });

        context.stroke();

    });

}


async function analyzeImage() {

    if (!currentFileName) {
        showNotification("Primero cargá una imagen.", "error");
        return;
    }

    try {

        btnAnalysis.disabled = true;

        showNotification("Analizando imagen...", "success");

        const response = await fetch(
            `${API_BASE_URL}/images/${encodeURIComponent(currentFileName)}/analysis`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Error al analizar la imagen.");
        }

        // Histograma RGB
        drawHistogram(
            colorHistogram,
            [
                data.color_histograms.red,
                data.color_histograms.green,
                data.color_histograms.blue
            ],
            ["#e05252", "#45b878", "#548de5"]
        );

        // Histograma de luminosidad
        drawHistogram(
            grayscaleHistogram,
            [data.grayscale.histogram],
            ["#d5d5d5"]
        );

        // Estadísticas
        imageStatistics.innerHTML = `
            <p><strong>Mínimo:</strong>
                ${data.grayscale.minimum}
            </p>

            <p><strong>Máximo:</strong>
                ${data.grayscale.maximum}
            </p>

            <p><strong>Media:</strong>
                ${Number(data.grayscale.mean).toFixed(2)}
            </p>
        `;

        showNotification(
            "Análisis completado correctamente.",
            "success"
        );

        console.log("Análisis:", data);

    } catch (error) {

        console.error("Error de análisis:", error);
        showNotification(error.message, "error");

    } finally {

        btnAnalysis.disabled = !currentFileName;

    }

}


// ========================================
// 9. DETECCIÓN DE BORDES
// ========================================

// Actualización de los valores de los controles
threshold1Input.addEventListener("input", () => {
    threshold1Value.textContent = threshold1Input.value;
});

threshold2Input.addEventListener("input", () => {
    threshold2Value.textContent = threshold2Input.value;
});


async function detectImageEdges() {

    if (!currentFileName) {
        showNotification("Primero cargá una imagen.", "error");
        return;
    }

    const threshold1 = Number(threshold1Input.value);
    const threshold2 = Number(threshold2Input.value);

    if (threshold1 >= threshold2) {
        showNotification(
            "El umbral inferior debe ser menor que el superior.",
            "error"
        );
        return;
    }

    try {

        btnEdges.disabled = true;

        showNotification("Detectando bordes...", "success");

        const parameters = new URLSearchParams({
            threshold1,
            threshold2
        });

        const response = await fetch(
            `${API_BASE_URL}/images/${encodeURIComponent(currentFileName)}/edges?${parameters}`,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Error al detectar bordes.");
        }

        currentResult = data;

        const resultUrl = `${API_BASE_URL}${data.url}`;

        displayImage(
            resultFrame,
            resultUrl,
            "Bordes detectados"
        );

        btnDownload.href = resultUrl;
        btnDownload.download = data.file_name;

        imageActions.hidden = false;

        showNotification(
            "Detección de bordes completada.",
            "success"
        );

        console.log("Bordes:", data);

    } catch (error) {

        console.error("Error de detección:", error);
        showNotification(error.message, "error");

    } finally {

        btnEdges.disabled = !currentFileName;

    }

}


// ========================================
// 10. RESTAURACIÓN DE PINTURAS
// ========================================

function renderRestorationParameters() {

    const technique = restorationSelect.value;
    let html = "";

    switch (technique) {

        case "denoise":

            html = `
                <label for="denoise-diameter">
                    Intensidad espacial
                </label>

                <input
                    type="number"
                    id="denoise-diameter"
                    min="1"
                    max="15"
                    step="2"
                    value="5"
                >

                <label for="denoise-color">
                    Preservación de color
                </label>

                <input
                    type="number"
                    id="denoise-color"
                    min="1"
                    max="100"
                    value="20"
                >

                <label for="denoise-space">
                    Preservación espacial
                </label>

                <input
                    type="number"
                    id="denoise-space"
                    min="1"
                    max="100"
                    value="20"
                >
            `;

            break;


        case "color-correction":

            html = `
                <label for="color-clip">
                    Intensidad de contraste local
                </label>

                <input
                    type="number"
                    id="color-clip"
                    min="0.1"
                    max="5"
                    step="0.1"
                    value="1.2"
                >

                <label for="color-grid">
                    Tamaño de la cuadrícula
                </label>

                <input
                    type="number"
                    id="color-grid"
                    min="2"
                    max="16"
                    value="8"
                >
            `;

            break;


        case "detail-enhancement":

            html = `
                <label for="detail-strength">
                    Intensidad de detalle
                </label>

                <input
                    type="number"
                    id="detail-strength"
                    min="0"
                    max="1"
                    step="0.05"
                    value="0.35"
                >

                <label for="detail-sigma">
                    Radio de suavizado
                </label>

                <input
                    type="number"
                    id="detail-sigma"
                    min="0.1"
                    max="5"
                    step="0.1"
                    value="1"
                >
            `;

            break;


        case "inpainting":

            html = `
                <p>
                    Seleccioná con el pincel las zonas dañadas de la pintura.
                    La región marcada será reconstruida utilizando los píxeles
                    de su entorno.
                </p>
            `;

            break;

    }

    restorationParameters.innerHTML = html;

    const isInpainting = technique === "inpainting";

    // Los controles del pincel solo se muestran para Inpainting.
    if (inpaintingControls) {
        inpaintingControls.hidden = !isInpainting;
    }

    // Activar el pincel cuando existe una imagen cargada.
    if (isInpainting && currentFileName && inpaintingTool) {

        try {
            inpaintingTool.enable();
        } catch (error) {
            console.error("No se pudo activar Inpainting:", error);
            showNotification(error.message, "error");
        }

    } else if (inpaintingTool) {

        // Al cambiar de técnica se descarta la máscara anterior.
        inpaintingTool.disable();
    }

    // Restaurar solo se habilita cuando hay imagen y selección válida.
    btnRestore.disabled =
        !currentFileName ||
        (isInpainting && (
            !inpaintingTool || !inpaintingTool.hasMaskSelection()
        ));

}


function getRestorationParameters() {

    switch (restorationSelect.value) {

        case "denoise":

            return {
                diameter: Number(
                    document.getElementById("denoise-diameter").value
                ),

                sigma_color: Number(
                    document.getElementById("denoise-color").value
                ),

                sigma_space: Number(
                    document.getElementById("denoise-space").value
                )
            };


        case "color-correction":

            return {
                clip_limit: Number(
                    document.getElementById("color-clip").value
                ),

                tile_grid_size: Number(
                    document.getElementById("color-grid").value
                )
            };


        case "detail-enhancement":

            return {
                strength: Number(
                    document.getElementById("detail-strength").value
                ),

                sigma: Number(
                    document.getElementById("detail-sigma").value
                )
            };


        default:
            return {};

    }

}


async function restoreImage() {

    if (!currentFileName) {
        showNotification("Primero cargá una imagen.", "error");
        return;
    }

    const technique = restorationSelect.value;

    if (
        technique === "inpainting" &&
        (!inpaintingTool || !inpaintingTool.hasMaskSelection())
    ) {
        showNotification(
            "Primero seleccioná con el pincel una zona para reconstruir.",
            "error"
        );
        return;
    }

    try {

        btnRestore.disabled = true;

        // Inpainting necesita la máscara dibujada por el usuario.
        // Las otras técnicas conservan sus parámetros habituales.
        const parameters = technique === "inpainting"
            ? {
                mask_base64: inpaintingTool.getMaskBase64(),
                radius: 3,
                method: "telea"
            }
            : getRestorationParameters();

        showNotification("Restaurando pintura...", "success");

        const response = await fetch(
            `${API_BASE_URL}/images/${encodeURIComponent(currentFileName)}/restore`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    operation: technique,
                    parameters
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "No se pudo restaurar la imagen.");
        }

        currentResult = data;

        const resultUrl = `${API_BASE_URL}${data.url}`;

        displayImage(
            resultFrame,
            resultUrl,
            "Pintura restaurada"
        );

        btnDownload.href = resultUrl;
        btnDownload.download = data.file_name;

        imageActions.hidden = false;

        showNotification(
            "Restauración completada correctamente.",
            "success"
        );

        console.log("Restauración:", data);

    } catch (error) {

        console.error("Error de restauración:", error);
        showNotification(error.message, "error");

    } finally {

        btnRestore.disabled =
            !currentFileName ||
            (
                restorationSelect.value === "inpainting" &&
                (!inpaintingTool || !inpaintingTool.hasMaskSelection())
            );

    }

}


// ========================================
// 11. RESTABLECER VISTA ORIGINAL
// ========================================

function resetImageView() {

    if (!currentImage) return;

    // Desmontar el canvas antes de reemplazar la imagen original.
    // Esto descarta la máscara y evita referencias a elementos antiguos.
    if (inpaintingTool) {
        inpaintingTool.disable();
    }

    const originalUrl =
        `${API_BASE_URL}${currentImage.stored_image.url}`;

    displayImage(
        originalFrame,
        originalUrl,
        "Imagen original"
    );

    // Si Inpainting sigue seleccionado, volver a activar el pincel
    // sobre la imagen original, ahora sin ninguna selección.
    const isInpainting = restorationSelect.value === "inpainting";

    if (inpaintingControls) {
        inpaintingControls.hidden = !isInpainting;
    }

    if (isInpainting && inpaintingTool) {
        try {
            inpaintingTool.enable();
        } catch (error) {
            console.error("No se pudo reactivar Inpainting:", error);
            showNotification(error.message, "error");
        }
    }

    btnRestore.disabled = !currentFileName || isInpainting;

    resultFrame.innerHTML =
        "<span>El resultado aparecerá aquí.</span>";

    currentResult = null;

    imageActions.hidden = true;

    showNotification(
        "Vista original recuperada.",
        "success"
    );

}


// ========================================
// 12. EVENTOS DE LA APLICACIÓN
// ========================================

// Selección de archivo
fileInput.addEventListener("change", (event) => {
    uploadImage(event.target.files[0]);
});

// Cambio de operación
operationSelect.addEventListener("change", renderOperationParameters);

// Cambio de técnica de restauración
restorationSelect.addEventListener(
    "change",
    renderRestorationParameters
);

// Botones principales
btnProcess.addEventListener("click", processImage);
btnAnalysis.addEventListener("click", analyzeImage);
btnEdges.addEventListener("click", detectImageEdges);
btnRestore.addEventListener("click", restoreImage);
btnReset.addEventListener("click", resetImageView);


// ========================================
// 13. INICIALIZACIÓN
// ========================================

renderOperationParameters();
renderRestorationParameters();

checkServerStatus();
