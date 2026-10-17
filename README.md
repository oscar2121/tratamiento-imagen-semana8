# Informe de Resultados de Tratamiento de Imagen: Análisis de Condiciones de Captura y Percepción Computacional

Repositorio oficial para la práctica de **Tratamiento de Imagen**, correspondiente a la **Semana 8** de la experiencia en **Percepción Computacional / IMAGEN**.

**Estudiante:** Oscar David  
**Usuario de GitHub:** [oscar2121](https://github.com/oscar2121)  
**URL del Repositorio:** [https://github.com/oscar2121/tratamiento-imagen-semana8](https://github.com/oscar2121/tratamiento-imagen-semana8)

---

## 🎯 Propósito de la Actividad

Analizar experimentalmente cómo diferentes condiciones físicas y ópticas de captura (subexposición, desenfoque por movimiento, fondos complejos y cambios de perspectiva) degradan la señal visual de un mismo objeto y comprometen su utilización en un sistema de percepción computacional. A partir de un diagnóstico cuantitativo riguroso, se selecciona una imagen problemática y se diseña un pipeline de tratamiento justificado que restituya la capacidad de extracción de características y contornos.

---

## 📸 Las 5 Condiciones de Captura Estudiadas

1. **1. Referencia (Óptima):** Iluminación difusa balanceada, distancia focal adecuada y fondo neutro.
2. **2. Baja Iluminación (Subexpuesta):** Déficit crítico de radiancia lumínica incidente con presencia de ruido térmico del sensor.
3. **3. Desenfoque / Movimiento:** Pérdida severa de altas frecuencias espaciales por desplazamiento de cámara (*Motion Blur*).
4. **4. Fondo Complejo:** Interferencia de patrones sinusoidales heterogéneos que compiten con el contorno del objeto.
5. **5. Ángulo y Perspectiva:** Deformación proyectiva 3D homográfica por vista oblicua.

---

## 📊 Tabla Comparativa de Diagnóstico Cuantitativo

| Condición de Captura | Resolución | Canales | Brillo Medio (μ) | Contraste (σ) | Nitidez (∇²I Laplaciano) | Formato y Tamaño |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Referencia (Óptima)** | 800x600 | 3 (BGR) | 221.80 | 29.91 | 741.36 | JPG (32.0 KB) |
| **2. Baja Iluminación (Problemática)** | 800x600 | 3 (BGR) | **34.94** | **5.84** | **236.94\*** | JPG (141.3 KB) |
| **3. Desenfoque / Movimiento** | 800x600 | 3 (BGR) | 221.80 | 24.51 | **33.64** | JPG (23.4 KB) |
| **4. Fondo Complejo** | 800x600 | 3 (BGR) | 129.04 | 53.68 | 576.15 | JPG (78.5 KB) |
| **5. Ángulo / Perspectiva** | 800x600 | 3 (BGR) | 221.22 | 26.04 | 286.36 | JPG (28.4 KB) |

*\*Nota: En baja iluminación, la varianza del Laplaciano se encuentra artificialmente inflada por el ruido de alta frecuencia del sensor, no por nitidez estructural.*

---

## 🛠️ Pipeline de Tratamiento Diseñado (Imagen 2: Baja Iluminación)

1. **Desacoplamiento Cromático en CIE LAB:** Conversión de BGR a CIE LAB para procesar exclusivamente el canal de luminancia $L^*$ sin distorsionar los canales cromáticos $a^*$ y $b^*$.
2. **Corrección no lineal Gamma ($\gamma = 0.42$):** Expansión dinámica del rango en sombras profundas sin saturar las altas luces.
3. **Ecualización Adaptativa Local CLAHE:** Amplificación selectiva del contraste local en sub-bloques de $8 \times 8$ con límite de recorte (*clipLimit = 3.0*) para evitar sobre-amplificación de grano.
4. **Filtrado Bilateral Selectivo:** Supresión del ruido térmico del sensor en áreas homogéneas preservando las discontinuidades de bordes ($d=7, \sigma_{\text{color}}=35, \sigma_{\text{space}}=35$).
5. **Reconstrucción y Fusión:** Conversión de retorno al espacio de color BGR/RGB.

---

## 📈 Resultados Antes vs. Después del Tratamiento

| Métrica Evaluada | Antes del Tratamiento | Después del Tratamiento | Variación Absoluta | Impacto en Percepción Computacional |
| :--- | :---: | :---: | :---: | :--- |
| **Brillo Medio (μ)** | 34.94 | **110.56** | **+216.4%** | Transición de penumbra a visibilidad clara. |
| **Contraste Global (σ)** | 5.84 | **14.35** | **+145.7%** | Separación nítida entre fondo y pieza. |
| **Rango Dinámico** | [0 - 58] | **[0 - 255]** | **+339.6%** | Expansión homogénea de la escala tonal. |
| **Nitidez Real (∇²I)** | 236.94 *(Ruido)* | **296.24 *(Bordes)*** | **+25.0%** | Sustitución de ruido por gradientes estructurales. |
| **Detección Canny** | 0 contornos válidos | **Contornos cerrados completos** | **Éxito total** | Delimitación del bisel, escala y agujas indicadoras. |

---

## 📁 Estructura del Repositorio

```text
├── README.md                              # Documentación técnica del proyecto y métricas
├── Tratamiento_Imagen_Semana8.ipynb        # Cuaderno interactivo documentado para Google Colab
├── ejecutar_tratamiento.py                # Script modular en Python con el pipeline completo
├── Informe_Tratamiento_Imagen_Semana8.pdf # Informe formal de entrega en PDF (5 páginas)
├── Informe_Tratamiento_Imagen_Semana8.docx# Documento editable en Microsoft Word
├── fig1_cinco_condiciones.png             # Comparativa visual de las 5 condiciones e histogramas
├── fig2_pipeline_tratamiento.png          # Desglose visual por etapas del pipeline de tratamiento
├── fig3_comparacion_antes_despues.png     # Comparativa directa antes/después e histogramas
├── fig4_impacto_percepcion.png            # Validación de bordes Canny y contornos
└── figuras/                               # Carpeta con todas las evidencias en alta resolución
```

---

## 🚀 Ejecución en Google Colab

Puedes abrir y ejecutar el cuaderno interactivo directamente en Google Colab:

- 📓 [Abrir Cuaderno en Google Colab](https://colab.research.google.com/github/oscar2121/tratamiento-imagen-semana8/blob/main/Tratamiento_Imagen_Semana8.ipynb)

---

## 💻 Ejecución Local

```bash
git clone https://github.com/oscar2121/tratamiento-imagen-semana8.git
cd tratamiento-imagen-semana8
pip install opencv-python numpy matplotlib reportlab python-docx pandas
python ejecutar_tratamiento.py
```
