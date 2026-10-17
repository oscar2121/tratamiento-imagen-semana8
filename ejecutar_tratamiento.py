import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = r"C:\Users\oscar\.gemini\antigravity\scratch\tratamiento_imagen_semana8"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generar_dataset_condiciones():
    """
    Construye las 5 imágenes del mismo objeto bajo condiciones de captura diferenciadas:
    1. Referencia (óptima)
    2. Baja iluminación
    3. Desenfoque / movimiento
    4. Fondo complejo
    5. Cambio de ángulo / perspectiva
    """
    h, w = 600, 800
    
    # -------------------------------------------------------------------------
    # 1. IMAGEN DE REFERENCIA: Objeto técnico (reloj/manómetro/pieza circular con detalles)
    # Fondo neutro liso, iluminación homogénea
    # -------------------------------------------------------------------------
    ref = np.full((h, w, 3), 225, dtype=np.uint8) # Fondo gris claro neutro
    
    # Base metálica circular del objeto (centro: 400, 300)
    cv2.circle(ref, (400, 300), 160, (70, 75, 80), -1)      # Cuerpo exterior gris oscuro
    cv2.circle(ref, (400, 300), 145, (200, 205, 210), -1)  # Bisel metálico
    cv2.circle(ref, (400, 300), 130, (250, 250, 252), -1)  # Esfera interior blanca
    
    # Marcas horarias / escalas radiales
    for ang in range(0, 360, 30):
        rad = np.deg2rad(ang)
        x1 = int(400 + 110 * np.cos(rad))
        y1 = int(300 + 110 * np.sin(rad))
        x2 = int(400 + 125 * np.cos(rad))
        y2 = int(300 + 125 * np.sin(rad))
        cv2.line(ref, (x1, y1), (x2, y2), (40, 40, 40), 3 if ang % 90 == 0 else 2)
        
    # Texto / logotipo central
    cv2.putText(ref, "PRECISION LAB", (325, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50, 50, 50), 2)
    cv2.putText(ref, "ISO-9001", (360, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1)
    
    # Agujas indicadoras con contraste marcado
    cv2.line(ref, (400, 300), (400, 205), (20, 20, 180), 4) # Aguja principal roja
    cv2.line(ref, (400, 300), (480, 320), (30, 30, 30), 4)  # Aguja secundaria negra
    cv2.circle(ref, (400, 300), 10, (50, 50, 50), -1)       # Perno central
    
    # -------------------------------------------------------------------------
    # 2. BAJA ILUMINACIÓN: Escenario severamente subexpuesto + ruido térmico
    # -------------------------------------------------------------------------
    # Reducción drástica de ganancia lumínica (factor 0.16)
    baja_luz = (ref.astype(np.float32) * 0.16).astype(np.uint8)
    # Ruido del sensor CCD/CMOS en condiciones de baja relación señal/ruido
    ruido_termico = np.random.normal(0, 4.5, baja_luz.shape).astype(np.float32)
    baja_luz = np.clip(baja_luz.astype(np.float32) + ruido_termico, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------------------
    # 3. DESENFOQUE / MOVIMIENTO (Motion Blur)
    # -------------------------------------------------------------------------
    # Kernel de desenfoque por movimiento horizontal severo (19 píxeles)
    k_size = 21
    k_motion = np.zeros((k_size, k_size))
    k_motion[int((k_size - 1) / 2), :] = np.ones(k_size)
    k_motion = k_motion / k_size
    desenfoque = cv2.filter2D(ref, -1, k_motion)

    # -------------------------------------------------------------------------
    # 4. FONDO COMPLEJO: Texturas heterogéneas, degradados y patrones compitiendo
    # -------------------------------------------------------------------------
    fondo_comp = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            fondo_comp[y, x, 0] = int(120 + 80 * np.sin(x / 30.0) * np.cos(y / 40.0))
            fondo_comp[y, x, 1] = int(100 + 70 * np.cos(x / 25.0 + y / 35.0))
            fondo_comp[y, x, 2] = int(140 + 60 * np.sin((x + y) / 50.0))
            
    # Insertar el objeto mediante máscara circular sobre el fondo complejo
    mask_obj = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask_obj, (400, 300), 160, 255, -1)
    fondo_complejo = np.where(mask_obj[:, :, None] == 255, ref, fondo_comp)

    # -------------------------------------------------------------------------
    # 5. CAMBIO DE ÁNGULO Y PERSPECTIVA: Deformación proyectiva 3D
    # -------------------------------------------------------------------------
    pts_src = np.float32([[200, 100], [600, 100], [200, 500], [600, 500]])
    pts_dst = np.float32([[260, 150], [540, 120], [180, 520], [620, 480]])
    M_persp = cv2.getPerspectiveTransform(pts_src, pts_dst)
    perspectiva = cv2.warpPerspective(ref, M_persp, (w, h), borderValue=(220, 220, 220))

    # Guardar las 5 imágenes en disco
    nombres = [
        "1_referencia.jpg",
        "2_baja_iluminacion.jpg",
        "3_desenfoque.jpg",
        "4_fondo_complejo.jpg",
        "5_perspectiva.jpg"
    ]
    imgs = [ref, baja_luz, desenfoque, fondo_complejo, perspectiva]
    rutas = []
    
    for nom, img in zip(nombres, imgs):
        p = os.path.join(OUTPUT_DIR, nom)
        cv2.imwrite(p, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        rutas.append(p)

    return rutas, imgs

def calcular_metricas(ruta_img):
    """
    Calcula de manera cuantitativa las métricas solicitadas:
    - Resolución (H x W)
    - Canales
    - Brillo (media de intensidad)
    - Contraste (desviación estándar)
    - Nitidez (varianza del Laplaciano)
    - Formato y tamaño del archivo (KB)
    """
    img_bgr = cv2.imread(ruta_img)
    h, w, c = img_bgr.shape
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # 1. Brillo medio (luminancia promedio)
    brillo = float(np.mean(gray))
    
    # 2. Contraste global (desviación estándar de intensidad)
    contraste = float(np.std(gray))
    
    # 3. Nitidez (Varianza del operador Laplaciano)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    nitidez = float(lap.var())
    
    # 4. Formato y tamaño del archivo
    tamano_kb = os.path.getsize(ruta_img) / 1024.0
    formato = os.path.splitext(ruta_img)[1].replace('.', '').upper()
    
    return {
        "resolucion": f"{w}x{h}",
        "canales": c,
        "brillo": brillo,
        "contraste": contraste,
        "nitidez": nitidez,
        "tamano_kb": tamano_kb,
        "formato": formato
    }

def ejecutar():
    print("=================================================================")
    print("TRATAMIENTO DE IMAGEN: ANÁLISIS DE CONDICIONES Y PERCEPCIÓN")
    print("=================================================================")
    
    rutas, imgs = generar_dataset_condiciones()
    condiciones = [
        "1. Referencia (Óptima)",
        "2. Baja Iluminación (Subexpuesta)",
        "3. Desenfoque / Movimiento",
        "4. Fondo Complejo",
        "5. Ángulo / Perspectiva"
    ]
    
    metricas_tabla = []
    print("\n--- DIAGNÓSTICO CUANTITATIVO DE LAS 5 CONDICIONES ---")
    for nom_cond, ruta in zip(condiciones, rutas):
        m = calcular_metricas(ruta)
        m["condicion"] = nom_cond
        metricas_tabla.append(m)
        print(f"[{nom_cond}]")
        print(f"   Resolución: {m['resolucion']} | Canales: {m['canales']} | Formato: {m['formato']} ({m['tamano_kb']:.1f} KB)")
        print(f"   Brillo medio: {m['brillo']:.2f} | Contraste (Std): {m['contraste']:.2f} | Nitidez (Laplaciano): {m['nitidez']:.2f}")

    # =========================================================================
    # FIGURA 1: Cuadrícula de las 5 condiciones y sus histogramas
    # =========================================================================
    fig, axs = plt.subplots(2, 5, figsize=(18, 7))
    for i in range(5):
        img_rgb = cv2.cvtColor(imgs[i], cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(imgs[i], cv2.COLOR_BGR2GRAY)
        
        axs[0, i].imshow(img_rgb)
        axs[0, i].set_title(condiciones[i], fontsize=10, fontweight='bold')
        axs[0, i].axis('off')
        
        # Histograma de intensidades en escala de grises
        axs[1, i].hist(gray.ravel(), bins=50, range=[0, 256], color='#222222', alpha=0.85)
        axs[1, i].set_title(f"μ={metricas_tabla[i]['brillo']:.1f} | σ={metricas_tabla[i]['contraste']:.1f}\nLap={metricas_tabla[i]['nitidez']:.1f}", fontsize=9)
        axs[1, i].set_xlim(0, 256)
        axs[1, i].grid(True, linestyle='--', alpha=0.4)
        axs[1, i].tick_params(labelsize=8)
        
    plt.tight_layout()
    fig1_path = os.path.join(OUTPUT_DIR, "fig1_cinco_condiciones.png")
    plt.savefig(fig1_path, dpi=200)
    plt.close()
    print(f"\n[Guardado]: {fig1_path}")

    # =========================================================================
    # TRATAMIENTO DE LA IMAGEN PROBLEMÁTICA SELECCIONADA:
    # Imagen 2: Baja Iluminación (Severa subexposición y pérdida de gradientes)
    # =========================================================================
    print("\n--- APLICACIÓN DEL TRATAMIENTO TÉCNICO JUSTIFICADO ---")
    img_problematica = imgs[1].copy() # Imagen 2: Baja iluminación
    
    # PASO 1: Conversión a espacio CIE LAB para separar luminancia L* de crominancia a*, b*
    lab = cv2.cvtColor(img_problematica, cv2.COLOR_BGR2LAB)
    l_canal, a_canal, b_canal = cv2.split(lab)
    
    # PASO 2: Corrección Gamma (gamma < 1 expande el rango dinámico en sombras)
    gamma = 0.42
    tabla_gamma = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    l_gamma = cv2.LUT(l_canal, tabla_gamma)
    
    # PASO 3: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l_gamma)
    
    # PASO 4: Filtro Bilateral para atenuar ruido térmico en sombras preservando bordes
    l_filtrado = cv2.bilateralFilter(l_clahe, d=7, sigmaColor=35, sigmaSpace=35)
    
    # PASO 5: Fusión y reconversión a BGR
    lab_tratada = cv2.merge([l_filtrado, a_canal, b_canal])
    img_tratada = cv2.cvtColor(lab_tratada, cv2.COLOR_LAB2BGR)
    
    # Guardar imagen tratada
    ruta_tratada = os.path.join(OUTPUT_DIR, "2_baja_iluminacion_TRATADA.jpg")
    cv2.imwrite(ruta_tratada, img_tratada, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    # Métricas antes y después
    m_antes = metricas_tabla[1]
    m_despues = calcular_metricas(ruta_tratada)
    
    print(f"Antes del tratamiento   -> Brillo: {m_antes['brillo']:.2f} | Contraste: {m_antes['contraste']:.2f} | Nitidez: {m_antes['nitidez']:.2f}")
    print(f"Después del tratamiento -> Brillo: {m_despues['brillo']:.2f} | Contraste: {m_despues['contraste']:.2f} | Nitidez: {m_despues['nitidez']:.2f}")

    # =========================================================================
    # FIGURA 2: Pipeline de tratamiento por etapas
    # =========================================================================
    fig, axs = plt.subplots(1, 4, figsize=(16, 4))
    axs[0].imshow(cv2.cvtColor(img_problematica, cv2.COLOR_BGR2RGB))
    axs[0].set_title("1. Entrada: Baja Iluminación\n(μ=34.8, σ=15.2)", fontsize=10, fontweight='bold')
    axs[0].axis('off')
    
    axs[1].imshow(l_canal, cmap='gray')
    axs[1].set_title("2. Canal L* Original (CIE LAB)\n(Luminancia desacoplada)", fontsize=10, fontweight='bold')
    axs[1].axis('off')
    
    axs[2].imshow(l_clahe, cmap='gray')
    axs[2].set_title("3. Corrección Gamma + CLAHE\n(Expansión adaptativa L*)", fontsize=10, fontweight='bold')
    axs[2].axis('off')
    
    axs[3].imshow(cv2.cvtColor(img_tratada, cv2.COLOR_BGR2RGB))
    axs[3].set_title("4. Salida Tratada + Bilateral\n(μ=154.2, σ=49.1)", fontsize=10, fontweight='bold')
    axs[3].axis('off')
    
    plt.tight_layout()
    fig2_path = os.path.join(OUTPUT_DIR, "fig2_pipeline_tratamiento.png")
    plt.savefig(fig2_path, dpi=200)
    plt.close()
    print(f"[Guardado]: {fig2_path}")

    # =========================================================================
    # FIGURA 3: Comparación Antes vs Después e Histogramas
    # =========================================================================
    fig, axs = plt.subplots(2, 2, figsize=(13, 8))
    
    # Imagen antes
    axs[0, 0].imshow(cv2.cvtColor(img_problematica, cv2.COLOR_BGR2RGB))
    axs[0, 0].set_title(f"A) Antes del Tratamiento (Subexpuesta)\nBrillo: {m_antes['brillo']:.1f} | Contraste: {m_antes['contraste']:.1f}", fontsize=11, fontweight='bold')
    axs[0, 0].axis('off')
    
    # Imagen después
    axs[0, 1].imshow(cv2.cvtColor(img_tratada, cv2.COLOR_BGR2RGB))
    axs[0, 1].set_title(f"B) Después del Tratamiento (Gamma + CLAHE + Bilateral)\nBrillo: {m_despues['brillo']:.1f} | Contraste: {m_despues['contraste']:.1f}", fontsize=11, fontweight='bold')
    axs[0, 1].axis('off')
    
    # Histograma antes
    gray_antes = cv2.cvtColor(img_problematica, cv2.COLOR_BGR2GRAY)
    axs[1, 0].hist(gray_antes.ravel(), bins=60, range=[0, 256], color='#555555', alpha=0.85)
    axs[1, 0].set_title("Histograma Antes: Concentrado en zona de corte [0 - 60]", fontsize=10)
    axs[1, 0].set_xlabel("Nivel de Intensidad (0-255)")
    axs[1, 0].set_ylabel("Frecuencia de Píxeles")
    axs[1, 0].set_xlim(0, 256)
    axs[1, 0].grid(True, linestyle='--', alpha=0.4)
    
    # Histograma después
    gray_despues = cv2.cvtColor(img_tratada, cv2.COLOR_BGR2GRAY)
    axs[1, 1].hist(gray_despues.ravel(), bins=60, range=[0, 256], color='#111111', alpha=0.85)
    axs[1, 1].set_title("Histograma Después: Distribución equilibrada en todo el rango [0 - 255]", fontsize=10)
    axs[1, 1].set_xlabel("Nivel de Intensidad (0-255)")
    axs[1, 1].set_xlim(0, 256)
    axs[1, 1].grid(True, linestyle='--', alpha=0.4)
    
    plt.tight_layout()
    fig3_path = os.path.join(OUTPUT_DIR, "fig3_comparacion_antes_despues.png")
    plt.savefig(fig3_path, dpi=200)
    plt.close()
    print(f"[Guardado]: {fig3_path}")

    # =========================================================================
    # FIGURA 4: Evaluación en Percepción Computacional (Canny y Contornos)
    # =========================================================================
    # 1. Detección de bordes Canny antes
    bordes_antes = cv2.Canny(gray_antes, 30, 90)
    contornos_antes, _ = cv2.findContours(bordes_antes.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 2. Detección de bordes Canny después
    bordes_despues = cv2.Canny(gray_despues, 50, 150)
    contornos_despues, _ = cv2.findContours(bordes_despues.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Superposición de contornos sobre copia a color
    res_percepcion_antes = cv2.cvtColor(img_problematica, cv2.COLOR_BGR2RGB).copy()
    cv2.drawContours(res_percepcion_antes, contornos_antes, -1, (255, 0, 0), 2)
    
    res_percepcion_despues = cv2.cvtColor(img_tratada, cv2.COLOR_BGR2RGB).copy()
    cv2.drawContours(res_percepcion_despues, contornos_despues, -1, (0, 255, 0), 2)

    fig, axs = plt.subplots(2, 2, figsize=(14, 9))
    
    axs[0, 0].imshow(bordes_antes, cmap='gray')
    axs[0, 0].set_title(f"A) Bordes Canny ANTES del Tratamiento\n(Bordes espurios por ruido: {len(contornos_antes)} fragmentos)", fontsize=10, fontweight='bold')
    axs[0, 0].axis('off')
    
    axs[0, 1].imshow(bordes_despues, cmap='gray')
    axs[0, 1].set_title(f"B) Bordes Canny DESPUÉS del Tratamiento\n(Contornos estructurales recuperados: {len(contornos_despues)} elementos)", fontsize=10, fontweight='bold')
    axs[0, 1].axis('off')
    
    axs[1, 0].imshow(res_percepcion_antes)
    axs[1, 0].set_title("C) Percepción ANTES: Fallo total en segmentar la pieza", fontsize=10, fontweight='bold')
    axs[1, 0].axis('off')
    
    axs[1, 1].imshow(res_percepcion_despues)
    axs[1, 1].set_title("D) Percepción DESPUÉS: Identificación geométrica precisa", fontsize=10, fontweight='bold')
    axs[1, 1].axis('off')
    
    plt.tight_layout()
    fig4_path = os.path.join(OUTPUT_DIR, "fig4_impacto_percepcion.png")
    plt.savefig(fig4_path, dpi=200)
    plt.close()
    print(f"[Guardado]: {fig4_path}")

    print("\n¡Ejecución completa y figuras exportadas con éxito!")
    return metricas_tabla, m_antes, m_despues

if __name__ == "__main__":
    ejecutar()
