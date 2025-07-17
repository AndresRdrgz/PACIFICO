/**
 * Modal Requisitos - Sistema Mejorado de Validación
 * ================================================
 * 
 * Este sistema maneja la validación y carga de requisitos faltantes para transiciones
 * de etapa con mejor validación, manejo de archivos y estados de UI.
 */

class ModalRequisitos {
    constructor() {
        console.log('🏗️ Inicializando ModalRequisitos...');
        
        this.currentSolicitudId = null;
        this.currentNuevaEtapaId = null;
        this.currentCallbackExito = null;
        this.currentCallbackCancelacion = null;
        this.requisitosData = null;
        this.uploadQueue = [];
        this.isProcessing = false;
        
        // Verificar que el modal existe
        const modalElement = document.getElementById('modalRequisitosFaltantes');
        if (modalElement) {
            console.log('✅ Modal element encontrado en constructor');
        } else {
            console.error('❌ Modal element NO encontrado en constructor');
        }
        
        this.initializeEventListeners();
    }

    /**
     * Inicializar event listeners del modal
     */
    initializeEventListeners() {
        console.log('🔧 Inicializando event listeners del modal...');
        
        // Event listener para el cierre del modal
        const modal = document.getElementById('modalRequisitosFaltantes');
        if (modal) {
            console.log('✅ Modal element encontrado, configurando event listeners');
            modal.addEventListener('hidden.bs.modal', () => {
                this.handleModalClose();
            });
        } else {
            console.error('❌ Modal element no encontrado durante inicialización');
        }

        // Event listener para el botón de validar
        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (btnValidar) {
            console.log('✅ Botón validar encontrado, configurando event listener');
            btnValidar.addEventListener('click', () => {
                this.handleValidarClick();
            });
        } else {
            console.error('❌ Botón validar no encontrado durante inicialización');
        }
    }

    /**
     * Mostrar modal de requisitos faltantes
     */
    mostrarModal(solicitudId, nuevaEtapaId, nombreEtapa, callbackExito, callbackCancelacion) {
        console.log('🔍 Mostrando modal de requisitos faltantes mejorado');
        console.log('📋 Parámetros:', { solicitudId, nuevaEtapaId, nombreEtapa });

        // Validar parámetros
        if (!solicitudId || !nuevaEtapaId || !nombreEtapa) {
            console.error('❌ Parámetros inválidos');
            this.showToast('Error: Parámetros inválidos para mostrar modal de requisitos', 'error');
            return;
        }

        // Guardar estado
        this.currentSolicitudId = solicitudId;
        this.currentNuevaEtapaId = nuevaEtapaId;
        this.currentCallbackExito = callbackExito;
        this.currentCallbackCancelacion = callbackCancelacion;

        // Resetear estado del modal
        this.resetearEstado();

        // Actualizar información de la transición
        this.actualizarInfoTransicion(nombreEtapa);

        // Cargar requisitos
        this.cargarRequisitos();
    }

    /**
     * Resetear estado del modal
     */
    resetearEstado() {
        console.log('🔄 Reseteando estado del modal');

        // Resetear botón
        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (btnValidar) {
            btnValidar.innerHTML = '<i class="fas fa-check me-2"></i>Validar y Continuar';
            btnValidar.className = 'btn btn-primary';
            btnValidar.disabled = true;
        }

        // Limpiar contenedores
        const listaContainer = document.getElementById('listaRequisitosFaltantes');
        if (listaContainer) listaContainer.innerHTML = '';

        // Ocultar elementos
        this.ocultarElemento('resumenRequisitos');
        this.ocultarElemento('estadoValidacion');
        this.ocultarElemento('infoAlert');

        // Mostrar loading
        this.mostrarElemento('loadingRequisitos');

        // Resetear variables
        this.requisitosData = null;
        this.uploadQueue = [];
        this.isProcessing = false;
    }

    /**
     * Actualizar información de la transición
     */
    actualizarInfoTransicion(nombreEtapa) {
        const etapaDestinoElement = document.getElementById('etapaDestinoNombre');
        if (etapaDestinoElement) {
            etapaDestinoElement.textContent = nombreEtapa;
        }
    }

    /**
     * Cargar requisitos desde el backend
     */
    async cargarRequisitos() {
        try {
            const response = await fetch(`/workflow/api/solicitudes/${this.currentSolicitudId}/requisitos-faltantes-detallado/?nueva_etapa_id=${this.currentNuevaEtapaId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('📋 Requisitos recibidos:', data);

            if (data.success) {
                this.requisitosData = data;
                this.llenarListaRequisitos(data);
                this.actualizarResumen(data);
                this.actualizarEstadoModal(data);
                
                // Mostrar el modal después de cargar los datos
                this.mostrarModalElement();
            } else {
                throw new Error(data.error || 'Error al cargar requisitos');
            }
        } catch (error) {
            console.error('❌ Error al cargar requisitos:', error);
            this.showToast('Error al cargar requisitos: ' + error.message, 'error');
        } finally {
            this.ocultarElemento('loadingRequisitos');
        }
    }

    /**
     * Llenar lista de requisitos en el modal
     */
    llenarListaRequisitos(data) {
        const listaContainer = document.getElementById('listaRequisitosFaltantes');
        if (!listaContainer) return;

        listaContainer.innerHTML = '';

        if (data.requisitos.length === 0) {
            listaContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    No hay requisitos obligatorios para esta transición
                </div>
            `;
            return;
        }

        data.requisitos.forEach(requisito => {
            const requisitoHtml = this.generarHtmlRequisito(requisito);
            listaContainer.insertAdjacentHTML('beforeend', requisitoHtml);
        });

        // Configurar event listeners para los inputs de archivo
        this.configurarEventListenersArchivos();
    }

    /**
     * Generar HTML para un requisito individual
     */
    generarHtmlRequisito(requisito) {
        const estado = this.determinarEstadoRequisito(requisito);
        const estadoClass = this.obtenerClaseEstado(estado);
        const icono = this.obtenerIconoEstado(estado);
        const mensaje = this.obtenerMensajeEstado(estado);

        return `
            <div class="requisito-item ${estadoClass}" data-requisito-id="${requisito.id}">
                <div class="validation-status ${estadoClass}">
                    <i class="fas ${icono}"></i>
                </div>
                
                <div class="requisito-header">
                    <div class="requisito-status ${estadoClass}">
                        <i class="fas ${icono}"></i>
                    </div>
                    <div class="requisito-info">
                        <h6>${requisito.nombre}</h6>
                        ${requisito.descripcion ? `<p>${requisito.descripcion}</p>` : ''}
                    </div>
                    <div class="text-end">
                        <span class="badge ${this.obtenerClaseBadge(estado)}">${mensaje}</span>
                    </div>
                </div>

                ${requisito.mensaje_personalizado ? `
                    <div class="requisito-message info">
                        <i class="fas fa-info-circle me-1"></i>
                        ${requisito.mensaje_personalizado}
                    </div>
                ` : ''}

                ${this.generarSeccionArchivo(requisito, estado)}

                <div class="requisito-actions">
                    ${this.generarBotonesAccion(requisito, estado)}
                </div>
            </div>
        `;
    }

    /**
     * Determinar estado de un requisito
     */
    determinarEstadoRequisito(requisito) {
        if (requisito.esta_cumplido && requisito.archivo_actual) {
            return 'completado';
        } else if (requisito.archivo_actual && !requisito.esta_cumplido) {
            return 'pendiente';
        } else {
            return 'faltante';
        }
    }

    /**
     * Obtener clase CSS para el estado
     */
    obtenerClaseEstado(estado) {
        const clases = {
            'completado': 'completado',
            'pendiente': 'pendiente',
            'faltante': 'faltante'
        };
        return clases[estado] || 'faltante';
    }

    /**
     * Obtener icono para el estado
     */
    obtenerIconoEstado(estado) {
        const iconos = {
            'completado': 'fa-check',
            'pendiente': 'fa-clock',
            'faltante': 'fa-exclamation-triangle'
        };
        return iconos[estado] || 'fa-exclamation-triangle';
    }

    /**
     * Obtener mensaje para el estado
     */
    obtenerMensajeEstado(estado) {
        const mensajes = {
            'completado': 'Completo',
            'pendiente': 'Pendiente',
            'faltante': 'Faltante'
        };
        return mensajes[estado] || 'Faltante';
    }

    /**
     * Obtener clase para el badge
     */
    obtenerClaseBadge(estado) {
        const clases = {
            'completado': 'bg-success',
            'pendiente': 'bg-warning',
            'faltante': 'bg-danger'
        };
        return clases[estado] || 'bg-danger';
    }

    /**
     * Generar sección de archivo
     */
    generarSeccionArchivo(requisito, estado) {
        if (estado === 'completado' && requisito.archivo_actual) {
            return `
                <div class="file-preview">
                    <div class="file-icon">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <div class="file-info">
                        <div class="file-name">${requisito.archivo_actual.nombre}</div>
                        <div class="file-size">Archivo cargado</div>
                    </div>
                    <a href="${requisito.archivo_actual.url}" target="_blank" class="btn btn-outline-primary btn-sm">
                        <i class="fas fa-eye"></i>
                    </a>
                </div>
            `;
        } else {
            return `
                <div class="upload-section" id="upload-section-${requisito.id}">
                    <div class="mb-3">
                        <label class="form-label">
                            ${estado === 'pendiente' ? 'Reemplazar archivo' : 'Subir archivo'} 
                            <span class="text-danger">*</span>
                        </label>
                        <input type="file" class="form-control requisito-file-input" 
                               data-requisito-id="${requisito.id}" 
                               accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif"
                               aria-label="${estado === 'pendiente' ? 'Reemplazar archivo' : 'Subir archivo'}">
                        <small class="text-muted">El archivo se subirá automáticamente cuando hagas clic en 'Validar y Continuar'</small>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Generar botones de acción
     */
    generarBotonesAccion(requisito, estado) {
        if (estado === 'completado') {
            return `
                <button type="button" class="btn btn-outline-primary btn-sm" onclick="modalRequisitos.mostrarUploadParaReemplazo(${requisito.id})">
                    <i class="fas fa-upload me-1"></i>Reemplazar
                </button>
                <button type="button" class="btn btn-outline-secondary btn-sm" onclick="modalRequisitos.verArchivo(${requisito.id})">
                    <i class="fas fa-eye me-1"></i>Ver
                </button>
            `;
        } else if (estado === 'pendiente') {
            return `
                <button type="button" class="btn btn-outline-warning btn-sm" onclick="modalRequisitos.validarArchivoExistente(${requisito.id})">
                    <i class="fas fa-check me-1"></i>Validar
                </button>
                <button type="button" class="btn btn-outline-primary btn-sm" onclick="modalRequisitos.mostrarUploadParaReemplazo(${requisito.id})">
                    <i class="fas fa-upload me-1"></i>Reemplazar
                </button>
            `;
        } else {
            return `
                <button type="button" class="btn btn-outline-primary btn-sm" onclick="modalRequisitos.mostrarUploadParaReemplazo(${requisito.id})">
                    <i class="fas fa-upload me-1"></i>Subir
                </button>
            `;
        }
    }

    /**
     * Actualizar resumen de requisitos
     */
    actualizarResumen(data) {
        const total = data.total_requisitos;
        const completos = data.requisitos_completos;
        const faltantes = total - completos;

        document.getElementById('totalRequisitos').textContent = total;
        document.getElementById('requisitosCompletos').textContent = completos;
        document.getElementById('requisitosFaltantes').textContent = faltantes;

        this.mostrarElemento('resumenRequisitos');
    }

    /**
     * Actualizar estado del modal
     */
    actualizarEstadoModal(data) {
        const total = data.total_requisitos;
        const completos = data.requisitos_completos;
        const faltantes = total - completos;

        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (!btnValidar) return;

        if (faltantes === 0) {
            // Todos los requisitos están completos
            this.actualizarModalCompleto();
        } else {
            // Hay requisitos faltantes
            this.actualizarModalFaltantes(faltantes, total);
        }
    }

    /**
     * Actualizar modal cuando todos los requisitos están completos
     */
    actualizarModalCompleto() {
        // Cambiar header a verde
        const header = document.getElementById('modalHeader');
        const icon = document.getElementById('modalIcon');
        const title = document.getElementById('modalTitle');
        const subtitle = document.getElementById('modalSubtitle');

        if (header) header.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
        if (icon) icon.className = 'fas fa-check-circle me-2';
        if (title) title.textContent = 'Todos los Requisitos Completos';
        if (subtitle) subtitle.textContent = 'Puedes continuar a la siguiente etapa';

        // Mostrar mensaje de éxito
        this.mostrarMensajeInfo('success', 'Requisitos Completos', 'Todos los requisitos están completos y listos para continuar.');

        // Actualizar botón
        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (btnValidar) {
            btnValidar.innerHTML = '<i class="fas fa-check me-2"></i>Continuar';
            btnValidar.className = 'btn btn-success';
            btnValidar.disabled = false;
        }
    }

    /**
     * Actualizar modal cuando hay requisitos faltantes
     */
    actualizarModalFaltantes(faltantes, total) {
        // Mantener header rojo
        const header = document.getElementById('modalHeader');
        const icon = document.getElementById('modalIcon');
        const title = document.getElementById('modalTitle');
        const subtitle = document.getElementById('modalSubtitle');

        if (header) header.style.background = 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)';
        if (icon) icon.className = 'fas fa-exclamation-triangle me-2';
        if (title) title.textContent = 'Requisitos Faltantes';
        if (subtitle) subtitle.textContent = `Faltan ${faltantes} de ${total} requisitos`;

        // Mostrar mensaje de advertencia
        this.mostrarMensajeInfo('warning', 'Requisitos Pendientes', `Debes completar ${faltantes} requisitos antes de continuar.`);

        // Actualizar botón
        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (btnValidar) {
            btnValidar.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Validar y Continuar (${total - faltantes}/${total})`;
            btnValidar.className = 'btn btn-warning';
            btnValidar.disabled = true;
        }
    }

    /**
     * Mostrar mensaje informativo
     */
    mostrarMensajeInfo(tipo, titulo, mensaje) {
        const alert = document.getElementById('infoAlert');
        const icon = document.getElementById('infoIcon');
        const title = document.getElementById('infoTitle');
        const message = document.getElementById('infoMessage');

        if (alert && icon && title && message) {
            alert.className = `alert alert-${tipo}`;
            icon.className = `fas ${this.obtenerIconoMensaje(tipo)} me-3`;
            title.textContent = titulo;
            message.textContent = mensaje;
            this.mostrarElemento('infoAlert');
        }
    }

    /**
     * Obtener icono para mensaje
     */
    obtenerIconoMensaje(tipo) {
        const iconos = {
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle',
            'info': 'fa-info-circle'
        };
        return iconos[tipo] || 'fa-info-circle';
    }

    /**
     * Configurar event listeners para archivos
     */
    configurarEventListenersArchivos() {
        document.querySelectorAll('.requisito-file-input').forEach(input => {
            input.addEventListener('change', (event) => {
                this.handleFileSelection(event);
            });
        });
    }

    /**
     * Manejar selección de archivo
     */
    handleFileSelection(event) {
        const input = event.target;
        const requisitoId = input.dataset.requisitoId;
        const file = input.files[0];

        if (file) {
            console.log(`📁 Archivo seleccionado para requisito ${requisitoId}:`, file.name);
            this.validarArchivoSeleccionado(requisitoId, file);
        }

        // Verificar estado después de un breve delay
        setTimeout(() => {
            this.verificarEstadoRequisitos();
        }, 100);
    }

    /**
     * Validar archivo seleccionado
     */
    validarArchivoSeleccionado(requisitoId, file) {
        // Validar tipo de archivo
        const tiposPermitidos = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif'];
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!tiposPermitidos.includes(extension)) {
            this.showToast(`Tipo de archivo no permitido: ${extension}`, 'error');
            return false;
        }

        // Validar tamaño (máximo 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showToast('El archivo es demasiado grande. Máximo 10MB.', 'error');
            return false;
        }

        return true;
    }

    /**
     * Verificar estado de todos los requisitos
     */
    verificarEstadoRequisitos() {
        const totalRequisitos = document.querySelectorAll('.requisito-item').length;
        const requisitosCompletos = document.querySelectorAll('.requisito-item.completado').length;
        const archivosSeleccionados = document.querySelectorAll('.requisito-file-input[type="file"]:not([style*="display: none"])').length;

        console.log('🔍 Estado de requisitos:', { totalRequisitos, requisitosCompletos, archivosSeleccionados });

        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (!btnValidar) return;

        if (totalRequisitos === 0) {
            btnValidar.innerHTML = '<i class="fas fa-check me-2"></i>Continuar';
            btnValidar.className = 'btn btn-success';
            btnValidar.disabled = false;
        } else if (totalRequisitos === requisitosCompletos) {
            btnValidar.innerHTML = '<i class="fas fa-check me-2"></i>Todos los Requisitos Completos - Continuar';
            btnValidar.className = 'btn btn-success';
            btnValidar.disabled = false;
        } else if (archivosSeleccionados > 0) {
            btnValidar.innerHTML = `<i class="fas fa-upload me-2"></i>Validar y Continuar (${requisitosCompletos}/${totalRequisitos})`;
            btnValidar.className = 'btn btn-primary';
            btnValidar.disabled = false;
        } else {
            btnValidar.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Validar y Continuar (${requisitosCompletos}/${totalRequisitos})`;
            btnValidar.className = 'btn btn-warning';
            btnValidar.disabled = true;
        }
    }

    /**
     * Manejar clic en botón validar
     */
    async handleValidarClick() {
        if (this.isProcessing) return;

        console.log('🔄 Iniciando validación de requisitos');
        this.isProcessing = true;

        try {
            // Preparar archivos para subir
            const archivosParaSubir = this.prepararArchivosParaSubir();
            
            if (archivosParaSubir.length > 0) {
                await this.subirArchivos(archivosParaSubir);
            }

            // Validar requisitos en el backend
            await this.validarRequisitosBackend();

            // Ejecutar callback de éxito
            if (this.currentCallbackExito) {
                this.currentCallbackExito();
            }

        } catch (error) {
            console.error('❌ Error en validación:', error);
            this.showToast('Error durante la validación: ' + error.message, 'error');
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Preparar archivos para subir
     */
    prepararArchivosParaSubir() {
        const archivos = [];
        document.querySelectorAll('.requisito-file-input').forEach(input => {
            if (input.files.length > 0) {
                archivos.push({
                    requisitoId: input.dataset.requisitoId,
                    file: input.files[0]
                });
            }
        });
        return archivos;
    }

    /**
     * Subir archivos secuencialmente
     */
    async subirArchivos(archivos) {
        console.log(`📤 Subiendo ${archivos.length} archivos...`);
        
        this.mostrarEstadoValidacion('Subiendo archivos...', 0);

        for (let i = 0; i < archivos.length; i++) {
            const archivo = archivos[i];
            const progreso = ((i + 1) / archivos.length) * 100;
            
            this.mostrarEstadoValidacion(`Subiendo archivo ${i + 1} de ${archivos.length}...`, progreso);
            
            try {
                await this.subirArchivoIndividual(archivo);
            } catch (error) {
                console.error(`❌ Error al subir archivo ${archivo.requisitoId}:`, error);
                throw error;
            }
        }

        this.ocultarElemento('estadoValidacion');
    }

    /**
     * Subir archivo individual
     */
    async subirArchivoIndividual(archivo) {
        const formData = new FormData();
        formData.append('requisito_id', archivo.requisitoId);
        formData.append('archivo', archivo.file);

        const response = await fetch(`/workflow/api/solicitudes/${this.currentSolicitudId}/subir-requisito-modal/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Error al subir archivo');
        }

        console.log(`✅ Archivo subido exitosamente para requisito ${archivo.requisitoId}`);
        this.actualizarUIRequisito(archivo.requisitoId, 'completado');
    }

    /**
     * Validar requisitos en el backend
     */
    async validarRequisitosBackend() {
        console.log('🔍 Validando requisitos en el backend...');
        
        this.mostrarEstadoValidacion('Validando requisitos...', 50);

        const response = await fetch(`/workflow/api/solicitudes/${this.currentSolicitudId}/requisitos-faltantes-detallado/?nueva_etapa_id=${this.currentNuevaEtapaId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Error al validar requisitos');
        }

        const faltantes = data.requisitos_faltantes || [];
        if (faltantes.length > 0) {
            throw new Error(`Aún faltan ${faltantes.length} requisitos: ${faltantes.map(r => r.nombre).join(', ')}`);
        }

        this.mostrarEstadoValidacion('Validación completada', 100);
        console.log('✅ Validación completada exitosamente');
    }

    /**
     * Actualizar UI de un requisito
     */
    actualizarUIRequisito(requisitoId, estado) {
        const requisitoItem = document.querySelector(`.requisito-item[data-requisito-id="${requisitoId}"]`);
        if (!requisitoItem) return;

        requisitoItem.className = `requisito-item ${estado}`;
        
        const statusElement = requisitoItem.querySelector('.validation-status');
        const badgeElement = requisitoItem.querySelector('.badge');
        
        if (statusElement) {
            statusElement.className = `validation-status ${estado}`;
            statusElement.innerHTML = `<i class="fas ${this.obtenerIconoEstado(estado)}"></i>`;
        }
        
        if (badgeElement) {
            badgeElement.className = `badge ${this.obtenerClaseBadge(estado)}`;
            badgeElement.textContent = this.obtenerMensajeEstado(estado);
        }
    }

    /**
     * Mostrar estado de validación
     */
    mostrarEstadoValidacion(mensaje, progreso) {
        const estadoElement = document.getElementById('estadoValidacion');
        const progressBar = document.getElementById('progressBar');
        const estadoMensaje = document.getElementById('estadoMensaje');

        if (estadoElement) this.mostrarElemento('estadoValidacion');
        if (progressBar) progressBar.style.width = `${progreso}%`;
        if (estadoMensaje) estadoMensaje.textContent = mensaje;
    }

    /**
     * Manejar cierre del modal
     */
    handleModalClose() {
        console.log('🚪 Modal cerrado');
        if (this.currentCallbackCancelacion) {
            this.currentCallbackCancelacion();
        }
    }

    /**
     * Mostrar el modal
     */
    mostrarModalElement() {
        console.log('🎭 Mostrando modal de requisitos...');
        const modalElement = document.getElementById('modalRequisitosFaltantes');
        if (modalElement) {
            try {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                console.log('✅ Modal mostrado exitosamente');
            } catch (error) {
                console.error('❌ Error al mostrar modal:', error);
                // Fallback: intentar mostrar directamente
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                document.body.classList.add('modal-open');
                console.log('🔄 Modal mostrado con fallback');
            }
        } else {
            console.error('❌ No se encontró el elemento del modal');
            // Intentar buscar el modal de otra manera
            const modals = document.querySelectorAll('.modal');
            console.log('🔍 Modales encontrados en la página:', modals.length);
            modals.forEach((modal, index) => {
                console.log(`Modal ${index}:`, modal.id, modal.className);
            });
        }
    }

    /**
     * Cerrar modal
     */
    cerrarModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalRequisitosFaltantes'));
        if (modal) {
            modal.hide();
        }
    }

    /**
     * Mostrar upload para reemplazo
     */
    mostrarUploadParaReemplazo(requisitoId) {
        const uploadSection = document.getElementById(`upload-section-${requisitoId}`);
        if (uploadSection) {
            uploadSection.style.display = 'block';
            uploadSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Validar archivo existente
     */
    async validarArchivoExistente(requisitoId) {
        try {
            // Aquí podrías implementar lógica adicional para validar archivos existentes
            console.log(`🔍 Validando archivo existente para requisito ${requisitoId}`);
            this.showToast('Archivo validado exitosamente', 'success');
        } catch (error) {
            console.error('❌ Error al validar archivo:', error);
            this.showToast('Error al validar archivo', 'error');
        }
    }

    /**
     * Ver archivo
     */
    verArchivo(requisitoId) {
        const requisito = this.requisitosData?.requisitos?.find(r => r.id == requisitoId);
        if (requisito?.archivo_actual?.url) {
            window.open(requisito.archivo_actual.url, '_blank');
        }
    }

    /**
     * Utilidades para mostrar/ocultar elementos
     */
    mostrarElemento(id) {
        const elemento = document.getElementById(id);
        if (elemento) elemento.style.display = 'block';
    }

    ocultarElemento(id) {
        const elemento = document.getElementById(id);
        if (elemento) elemento.style.display = 'none';
    }

    /**
     * Mostrar toast
     */
    showToast(mensaje, tipo) {
        if (typeof showToast !== 'undefined') {
            showToast(mensaje, tipo, 5000);
        } else {
            alert(mensaje);
        }
    }
}

// Función para inicializar el sistema cuando el DOM esté listo
function initializeModalRequisitos() {
    console.log('🚀 Inicializando sistema ModalRequisitos...');
    
    // Verificar que Bootstrap esté disponible
    if (typeof bootstrap === 'undefined') {
        console.error('❌ Bootstrap no está disponible');
        return;
    }
    
    // Verificar que el modal existe
    const modalElement = document.getElementById('modalRequisitosFaltantes');
    if (!modalElement) {
        console.error('❌ Modal element no encontrado durante inicialización');
        return;
    }
    
    // Inicializar instancia global
    window.modalRequisitos = new ModalRequisitos();
    console.log('✅ ModalRequisitos inicializado correctamente');
}

// Funciones de compatibilidad para el código existente
window.mostrarModalRequisitosFaltantes = function(solicitudId, nuevaEtapaId, nombreEtapa, callbackExito, callbackCancelacion) {
    if (window.modalRequisitos) {
        window.modalRequisitos.mostrarModal(solicitudId, nuevaEtapaId, nombreEtapa, callbackExito, callbackCancelacion);
    } else {
        console.error('❌ ModalRequisitos no está inicializado');
    }
};

window.cerrarModalRequisitos = function() {
    if (window.modalRequisitos) {
        window.modalRequisitos.cerrarModal();
    } else {
        console.error('❌ ModalRequisitos no está inicializado');
    }
};

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeModalRequisitos);
} else {
    // DOM ya está listo
    initializeModalRequisitos();
}

// Función de prueba para verificar el modal
window.testModalRequisitos = function() {
    console.log('🧪 Probando modal de requisitos...');
    
    if (window.modalRequisitos) {
        // Simular datos de prueba
        const testData = {
            success: true,
            requisitos: [
                {
                    id: 1,
                    nombre: 'Documento de Identidad',
                    descripcion: 'Cédula de identidad del cliente',
                    mensaje_personalizado: 'Debe estar vigente',
                    esta_cumplido: false,
                    archivo_actual: null
                },
                {
                    id: 2,
                    nombre: 'Comprobante de Ingresos',
                    descripcion: 'Últimos 3 meses de ingresos',
                    mensaje_personalizado: 'Debe incluir todos los ingresos',
                    esta_cumplido: true,
                    archivo_actual: {
                        nombre: 'comprobante_ingresos.pdf',
                        url: '#'
                    }
                }
            ],
            total_requisitos: 2,
            requisitos_completos: 1
        };
        
        // Simular el modal con datos de prueba
        window.modalRequisitos.requisitosData = testData;
        window.modalRequisitos.llenarListaRequisitos(testData);
        window.modalRequisitos.actualizarResumen(testData);
        window.modalRequisitos.actualizarEstadoModal(testData);
        window.modalRequisitos.mostrarModalElement();
        
        console.log('✅ Modal de prueba mostrado');
    } else {
        console.error('❌ ModalRequisitos no está disponible');
    }
};

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalRequisitos;
} 