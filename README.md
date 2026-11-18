# ArtScope – Digital Art Lab

## Datos académicos

- **Materia:** Procesamiento de Imágenes
- **Año y cuatrimestre:** 2026 – Segundo cuatrimestre
- **Alumno:** Lucas Mateo Suárez Ramos
- **Docente:** Juan Ignacio Bonini

## Descripción del proyecto

ArtScope es una aplicación web destinada al análisis, procesamiento y restauración digital de pinturas. Permite importar imágenes de obras artísticas, aplicar distintas operaciones de procesamiento y experimentar con técnicas de reconstrucción de sectores deteriorados.

La plataforma cuenta con una interfaz que permite visualizar la imagen original y comparar los resultados obtenidos después de aplicar las herramientas disponibles.

## Motivación

La motivación para desarrollar ArtScope surgió del interés por aplicar los conocimientos de procesamiento digital de imágenes a un contexto relacionado con el arte y la conservación del patrimonio visual.

El objetivo fue crear una herramienta que permitiera experimentar con distintas técnicas de procesamiento y restauración digital, facilitando la observación de los cambios producidos sobre una pintura.

Además, el proyecto permitió integrar conocimientos de programación, procesamiento de imágenes e inteligencia artificial en una aplicación web funcional.

## Problemáticas encontradas y soluciones implementadas

Durante el desarrollo del proyecto se presentaron distintos desafíos técnicos:

### 1. Procesamiento y conservación de las imágenes

Fue necesario implementar operaciones que permitieran modificar las imágenes manteniendo el control sobre sus dimensiones, colores y características visuales.

**Solución:** se utilizaron OpenCV y NumPy para realizar las operaciones de procesamiento y controlar las transformaciones aplicadas.

### 2. Reconstrucción de sectores dañados

Uno de los desafíos principales fue desarrollar mecanismos para reconstruir partes de una pintura seleccionadas mediante máscaras.

**Solución:** se implementaron técnicas de inpainting de OpenCV, como Telea, y se integró el modelo de inteligencia artificial LaMa mediante ONNX. También se trabajó en el redimensionamiento proporcional y la adaptación de las máscaras.

### 3. Integración entre frontend y backend

Fue necesario conectar la interfaz web con los servicios encargados de procesar las imágenes, gestionar las solicitudes y devolver los resultados.

**Solución:** se utilizó FastAPI para desarrollar la API del backend y JavaScript para gestionar las interacciones de la interfaz y la comunicación con el servidor.

### 4. Despliegue y comunicación entre servicios

Durante la publicación de la aplicación surgieron dificultades relacionadas con la configuración de los servicios y la comunicación entre el frontend y el backend.

**Solución:** se realizaron ajustes en la configuración CORS y en los despliegues de Vercel y Render para permitir la comunicación entre ambos entornos.

### 5. Limitaciones de memoria en la reconstrucción con inteligencia artificial

El modelo LaMa requiere una cantidad considerable de memoria durante su ejecución. En el plan gratuito de Render, cuyo límite es de 512 MB, su inferencia supera la memoria disponible y provoca el reinicio del servicio.

**Solución:** se realizaron optimizaciones en la implementación para reducir el consumo de recursos. La reconstrucción con LaMa funciona en el entorno local, pero su ejecución en producción está limitada por la infraestructura disponible. Por este motivo, se conserva como funcionalidad experimental y se prioriza la estabilidad de las demás herramientas publicadas.

## Tecnologías utilizadas

- **Python:** lenguaje principal del backend.
- **FastAPI:** desarrollo de la API.
- **OpenCV:** procesamiento y restauración de imágenes.
- **NumPy:** manipulación de matrices y datos de imágenes.
- **ONNX:** integración del modelo de inteligencia artificial LaMa.
- **HTML:** estructura de la interfaz.
- **CSS:** diseño y estilos visuales.
- **JavaScript:** interactividad y comunicación con el backend.
- **Render:** alojamiento del backend.
- **Vercel:** publicación del frontend.

## Enlaces del proyecto

- **Repositorio GitHub:** https://github.com/Lukit4as/Proyecto_ArtScope
- **Aplicación web:** https://proyectoartscope-frontend.vercel.app/

