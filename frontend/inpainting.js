
// ========================================
// ARTSCOPE - MODULO DE INPAINTING
// ========================================

window.ArtScopeInpainting = (function () {

    // ========================================
    // 1. CREACION DEL CONTROLADOR
    // ========================================

    function create(config) {

        const originalFrame = config.originalFrame;
        const brushSizeInput = config.brushSizeInput;
        const brushSizeValue = config.brushSizeValue;
        const clearButton = config.clearButton;

        let wrapper = null;
        let image = null;

        let visibleCanvas = null;
        let maskCanvas = null;

        let visibleContext = null;
        let maskContext = null;

        let drawing = false;
        let lastPosition = null;
        let hasSelection = false;

        let onSelectionChange = function () {};

        // ========================================
        // 2. PREPARAR EL LIENZO
        // ========================================

        function enable() {

            image = originalFrame.querySelector("img");

            if (!image) {
                throw new Error(
                    "Primero debe cargarse una imagen original."
                );
            }

            if (wrapper) {
                return;
            }

            wrapper = document.createElement("div");
            wrapper.className = "restoration-image-wrapper";

            image.replaceWith(wrapper);
            wrapper.appendChild(image);

            // Canvas visible: muestra el trazo rojo.
            visibleCanvas = document.createElement("canvas");
            visibleCanvas.className = "restoration-mask-canvas";

            // Canvas de datos: almacena la máscara real.
            maskCanvas = document.createElement("canvas");
            maskCanvas.className = "restoration-mask-data-canvas";
            maskCanvas.style.display = "none";
            maskCanvas.setAttribute("aria-hidden", "true");

            visibleContext = visibleCanvas.getContext("2d");
            maskContext = maskCanvas.getContext("2d");

            wrapper.appendChild(visibleCanvas);

            // IMPORTANTE: agregar también el canvas de máscara.
            wrapper.appendChild(maskCanvas);

            if (image.complete && image.naturalWidth > 0) {
                configureCanvases();
            } else {
                image.addEventListener(
                    "load",
                    configureCanvases,
                    { once: true }
                );
            }

            addDrawingEvents();
        }


        // ========================================
        // 3. CONFIGURAR LOS LIENZOS
        // ========================================

        function configureCanvases() {

            if (!image || !visibleCanvas || !maskCanvas) {
                return;
            }

            const width = image.naturalWidth;
            const height = image.naturalHeight;

            visibleCanvas.width = width;
            visibleCanvas.height = height;

            maskCanvas.width = width;
            maskCanvas.height = height;

            visibleContext.lineCap = "round";
            visibleContext.lineJoin = "round";

            maskContext.lineCap = "round";
            maskContext.lineJoin = "round";

            // La máscara comienza completamente negra.
            maskContext.fillStyle = "#000000";
            maskContext.fillRect(0, 0, width, height);
        }


        // ========================================
        // 4. POSICION DEL PINCEL
        // ========================================

        function getCanvasPosition(event) {

            const rectangle =
                visibleCanvas.getBoundingClientRect();

            const scaleX =
                visibleCanvas.width / rectangle.width;

            const scaleY =
                visibleCanvas.height / rectangle.height;

            return {
                x: (event.clientX - rectangle.left) * scaleX,
                y: (event.clientY - rectangle.top) * scaleY
            };
        }


        // ========================================
        // 5. TAMANO DEL PINCEL
        // ========================================

        function getBrushSize() {

            const displayedSize =
                Number(brushSizeInput.value);

            const rectangle =
                visibleCanvas.getBoundingClientRect();

            const scale =
                visibleCanvas.width / rectangle.width;

            return displayedSize * scale;
        }


        // ========================================
        // 6. DIBUJAR PUNTOS
        // ========================================

        function drawPoint(position) {

            const brushSize = getBrushSize();

            // Selección visible en rojo.
            visibleContext.fillStyle =
                "rgba(255, 60, 60, 0.45)";

            visibleContext.beginPath();

            visibleContext.arc(
                position.x,
                position.y,
                brushSize / 2,
                0,
                Math.PI * 2
            );

            visibleContext.fill();

            // Máscara real en blanco.
            maskContext.fillStyle = "#FFFFFF";

            maskContext.beginPath();

            maskContext.arc(
                position.x,
                position.y,
                brushSize / 2,
                0,
                Math.PI * 2
            );

            maskContext.fill();

            hasSelection = true;
            onSelectionChange(true);
        }


        // ========================================
        // 7. DIBUJAR TRAZOS
        // ========================================

        function drawLine(start, end) {

            const brushSize = getBrushSize();

            visibleContext.strokeStyle =
                "rgba(255, 60, 60, 0.45)";

            visibleContext.lineWidth = brushSize;

            visibleContext.beginPath();
            visibleContext.moveTo(start.x, start.y);
            visibleContext.lineTo(end.x, end.y);
            visibleContext.stroke();

            maskContext.strokeStyle = "#FFFFFF";
            maskContext.lineWidth = brushSize;

            maskContext.beginPath();
            maskContext.moveTo(start.x, start.y);
            maskContext.lineTo(end.x, end.y);
            maskContext.stroke();

            hasSelection = true;
            onSelectionChange(true);
        }


        // ========================================
        // 8. EVENTOS DEL PINCEL
        // ========================================

        function startDrawing(event) {

            if (!visibleCanvas || visibleCanvas.width === 0) {
                return;
            }

            event.preventDefault();

            drawing = true;

            visibleCanvas.setPointerCapture(event.pointerId);

            lastPosition = getCanvasPosition(event);

            drawPoint(lastPosition);
        }


        function continueDrawing(event) {

            if (!drawing) {
                return;
            }

            const position = getCanvasPosition(event);

            drawLine(lastPosition, position);

            lastPosition = position;
        }


        function stopDrawing() {

            drawing = false;
            lastPosition = null;
        }


        function addDrawingEvents() {

            visibleCanvas.addEventListener(
                "pointerdown",
                startDrawing
            );

            visibleCanvas.addEventListener(
                "pointermove",
                continueDrawing
            );

            visibleCanvas.addEventListener(
                "pointerup",
                stopDrawing
            );

            visibleCanvas.addEventListener(
                "pointercancel",
                stopDrawing
            );

            visibleCanvas.addEventListener(
                "lostpointercapture",
                stopDrawing
            );
        }


        // ========================================
        // 9. LIMPIAR LA SELECCION
        // ========================================

        function clear() {

            if (!visibleContext || !maskContext) {
                return;
            }

            visibleContext.clearRect(
                0,
                0,
                visibleCanvas.width,
                visibleCanvas.height
            );

            // Restablecer la máscara completamente a negro.
            maskContext.fillStyle = "#000000";

            maskContext.fillRect(
                0,
                0,
                maskCanvas.width,
                maskCanvas.height
            );

            hasSelection = false;

            onSelectionChange(false);
        }


        // ========================================
        // 10. EXPORTAR LA MASCARA
        // ========================================

        function getMaskBase64() {

            if (!hasSelection || !maskCanvas) {
                throw new Error(
                    "Primero seleccioná una zona para reconstruir."
                );
            }

            const dataUrl =
                maskCanvas.toDataURL("image/png");

            return dataUrl.split(",")[1];
        }


        // ========================================
        // 11. CONSULTAR LA SELECCION
        // ========================================

        function hasMaskSelection() {
            return hasSelection;
        }


        function setSelectionCallback(callback) {

            if (typeof callback === "function") {
                onSelectionChange = callback;
            }
        }


        // ========================================
        // 12. ACTUALIZAR EL TAMANO DEL PINCEL
        // ========================================

        function updateBrushLabel() {

            if (brushSizeInput && brushSizeValue) {

                brushSizeValue.textContent =
                    `${brushSizeInput.value} px`;
            }
        }


        if (brushSizeInput) {

            brushSizeInput.addEventListener(
                "input",
                updateBrushLabel
            );

            updateBrushLabel();
        }


        // ========================================
        // 13. BOTON PARA LIMPIAR
        // ========================================

        if (clearButton) {

            clearButton.addEventListener(
                "click",
                clear
            );
        }


        // ========================================
        // 14. DESACTIVAR EL PINCEL
        // ========================================

        function disable() {

            if (!wrapper) {
                return;
            }

            drawing = false;
            lastPosition = null;

            // Devolver la imagen a su contenedor original.
            wrapper.replaceWith(image);

            wrapper = null;
            visibleCanvas = null;
            maskCanvas = null;

            visibleContext = null;
            maskContext = null;

            hasSelection = false;

            onSelectionChange(false);
        }


        // ========================================
        // 15. DEVOLVER FUNCIONES DEL MODULO
        // ========================================

        return {
            enable,
            disable,
            clear,
            getMaskBase64,
            hasMaskSelection,
            setSelectionCallback
        };
    }


    return {
        create
    };

})();
