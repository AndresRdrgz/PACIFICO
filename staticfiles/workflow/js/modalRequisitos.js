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
        console.log('📝 Llenando lista de requisitos con data:', data);

        const listaContainer = document.getElementById('listaRequisitosFaltantes');
        if (!listaContainer) return;

        listaContainer.innerHTML = '';

        // Separar requisitos obligatorios y opcionales
        const requisitosObligatorios = data.requisitos_obligatorios || [];
        const requisitosOpcionales = data.requisitos_opcionales || [];

        console.log('🔍 DEBUG: Análisis de requisitos recibidos:');
        console.log('  - Obligatorios:', requisitosObligatorios.length, requisitosObligatorios);
        console.log('  - Opcionales:', requisitosOpcionales.length, requisitosOpcionales);

        // Verificar el campo 'obligatorio' en cada requisito
        requisitosObligatorios.forEach((req, index) => {
            console.log(`  Obligatorio ${index + 1}: ID=${req.id}, nombre="${req.nombre}", obligatorio=${req.obligatorio}`);
        });

        requisitosOpcionales.forEach((req, index) => {
            console.log(`  Opcional ${index + 1}: ID=${req.id}, nombre="${req.nombre}", obligatorio=${req.obligatorio}`);
        });

        // Si no hay requisitos obligatorios ni opcionales
        if (requisitosObligatorios.length === 0 && requisitosOpcionales.length === 0) {
            listaContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    No hay requisitos para esta transición
                </div>
            `;
            return;
        }

        // Sección de requisitos obligatorios
        if (requisitosObligatorios.length > 0) {
            const obligatoriosCompletos = requisitosObligatorios.filter(req => req.esta_cumplido).length;

            listaContainer.insertAdjacentHTML('beforeend', `
                <div class="seccion-requisitos">
                    <div class="seccion-titulo obligatorio">
                        <div class="d-flex align-items-center justify-content-between">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-exclamation-triangle text-danger me-2"></i>
                                <h6 class="mb-0 fw-bold">Requisitos Obligatorios</h6>
                            </div>
                            <span class="badge badge-obligatorio">${obligatoriosCompletos}/${requisitosObligatorios.length}</span>
                        </div>
                        <small class="text-muted d-block mt-1">Estos documentos son necesarios para continuar</small>
                    </div>
                    <div id="requisitos-obligatorios-lista">
                        ${requisitosObligatorios.map(req => this.generarHtmlRequisito(req)).join('')}
                    </div>
                </div>
            `);
        }

        // Sección de requisitos opcionales
        if (requisitosOpcionales.length > 0) {
            const opcionalesCompletos = requisitosOpcionales.filter(req => req.esta_cumplido).length;

            listaContainer.insertAdjacentHTML('beforeend', `
                <div class="seccion-requisitos">
                    <div class="seccion-titulo opcional">
                        <div class="d-flex align-items-center justify-content-between">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-plus-circle text-secondary me-2"></i>
                                <h6 class="mb-0 fw-bold">Requisitos Opcionales</h6>
                            </div>
                            <span class="badge badge-opcional">${opcionalesCompletos}/${requisitosOpcionales.length}</span>
                        </div>
                        <small class="text-muted d-block mt-1">Documentos adicionales que pueden facilitar el proceso</small>
                    </div>
                    <div id="requisitos-opcionales-lista">
                        ${requisitosOpcionales.map(req => this.generarHtmlRequisito(req)).join('')}
                    </div>
                </div>
            `);
        }

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

        // Agregar clase 'opcional' si el requisito no es obligatorio
        const claseOpcional = !requisito.obligatorio ? ' opcional' : '';

        console.log(`🏗️ Generando HTML para requisito ID=${requisito.id}:`, {
            nombre: requisito.nombre,
            obligatorio: requisito.obligatorio,
            claseOpcional: claseOpcional,
            estado: estado,
            estadoClass: estadoClass
        });

        return `
            <div class="requisito-item ${estadoClass}${claseOpcional}" data-requisito-id="${requisito.id}">
                <div class="validation-status ${estadoClass}">
                    <i class="fas ${icono}"></i>
                </div>
                
                <div class="requisito-header">
                    <div class="requisito-status ${estadoClass}">
                        <i class="fas ${icono}"></i>
                    </div>
                    <div class="requisito-info">
                        <h6>${requisito.nombre} ${!requisito.obligatorio ? '<span class="badge bg-secondary ms-1" style="font-size: 0.7rem;">Opcional</span>' : ''}</h6>
                        ${requisito.descripcion ? `<p>${requisito.descripcion}</p>` : ''}
                    </div>
                    <div class="text-end">
                        <span class="badge ${this.obtenerClaseBadge(estado, requisito.obligatorio)}">${mensaje}</span>
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
    obtenerClaseBadge(estado, esObligatorio = true) {
        if (!esObligatorio) {
            // Para requisitos opcionales
            const clasesOpcionales = {
                'completado': 'bg-info',
                'pendiente': 'bg-secondary',
                'faltante': 'bg-secondary'
            };
            return clasesOpcionales[estado] || 'bg-secondary';
        }

        // Para requisitos obligatorios
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
        // Lógica especial para agenda de firma
        if (requisito.tipo_especial === 'agenda_firma') {
            return this.generarSeccionAgendaFirma(requisito, estado);
        }

        // Lógica normal para requisitos con archivos
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
            const esObligatorio = requisito.obligatorio;
            const marcadorObligatorio = esObligatorio ? '<span class="text-danger">*</span>' : '<span class="text-secondary">(opcional)</span>';

            return `
                <div class="upload-section" id="upload-section-${requisito.id}">
                    <div class="mb-3">
                        <label class="form-label">
                            ${estado === 'pendiente' ? 'Reemplazar archivo' : 'Subir archivo'} 
                            ${marcadorObligatorio}
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
     * Generar sección específica para agenda de firma
     */
    generarSeccionAgendaFirma(requisito, estado) {
        const agendaFirma = requisito.agenda_firma || {};

        if (estado === 'completado' && agendaFirma.tiene_cita) {
            // Mostrar información de la cita agendada
            return `
                <div class="alert alert-success mb-3" style="border-radius: 12px; border: none; background: linear-gradient(135deg, rgba(40, 167, 69, 0.1), rgba(25, 135, 84, 0.15));">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-calendar-check me-3 mt-1 text-success" style="font-size: 1.5rem;"></i>
                        <div class="flex-grow-1">
                            <h6 class="alert-heading mb-2 text-success fw-bold">
                                <i class="fas fa-check-circle me-2"></i>
                                Firma Agendada
                            </h6>
                            <div class="row g-2">
                                <div class="col-md-6">
                                    <strong>Fecha:</strong><br>
                                    <span class="text-success">${agendaFirma.fecha_formateada || 'No especificada'}</span>
                                </div>
                                <div class="col-md-6">
                                    <strong>Lugar:</strong><br>
                                    <span class="text-success">${agendaFirma.lugar_firma_display || 'No especificado'}</span>
                                </div>
                                ${agendaFirma.comentarios ? `
                                <div class="col-12 mt-2">
                                    <strong>Comentarios:</strong><br>
                                    <span class="text-muted">${agendaFirma.comentarios}</span>
                                </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Mostrar interfaz para agendar firma
            return `
                <div class="alert alert-warning mb-3" style="border-radius: 12px; border: none; background: linear-gradient(135deg, rgba(255, 193, 7, 0.1), rgba(253, 126, 20, 0.15));">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-calendar-plus me-3 mt-1 text-warning" style="font-size: 1.5rem;"></i>
                        <div class="flex-grow-1">
                            <h6 class="alert-heading mb-2 text-warning fw-bold">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                Agenda de Firma Pendiente
                            </h6>
                            <p class="mb-3 text-muted">
                                Es necesario agendar una cita de firma para continuar con el proceso.
                            </p>
                            <button type="button" class="btn btn-warning" onclick="modalRequisitos.abrirModalAgendaFirma(${requisito.id})">
                                <i class="fas fa-calendar-plus me-2"></i>
                                Agendar Firma
                            </button>
                        </div>
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
        // Usar solo los requisitos obligatorios para determinar el estado
        const totalObligatorios = data.total_requisitos_obligatorios || 0;
        const completosObligatorios = data.requisitos_obligatorios_completos || 0;
        const faltantesObligatorios = totalObligatorios - completosObligatorios;

        console.log('📊 actualizarEstadoModal - Estado de requisitos obligatorios:', {
            totalObligatorios,
            completosObligatorios,
            faltantesObligatorios,
            'data.total_requisitos': data.total_requisitos,
            'data.requisitos_completos': data.requisitos_completos
        });

        console.log('📋 actualizarEstadoModal - Data completa recibida:', data);

        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (!btnValidar) {
            console.log('❌ btnValidarYContinuar not found!');
            return;
        }

        if (faltantesObligatorios === 0) {
            // Todos los requisitos obligatorios están completos
            console.log('✅ actualizarEstadoModal: Todos los requisitos obligatorios completos, llamando actualizarModalCompleto()');
            this.actualizarModalCompleto();
        } else {
            // Hay requisitos obligatorios faltantes
            console.log('❌ actualizarEstadoModal: Faltan requisitos obligatorios, llamando actualizarModalFaltantes()');
            this.actualizarModalFaltantes(faltantesObligatorios, totalObligatorios);
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
        if (title) title.textContent = 'Requisitos Obligatorios Completos';
        if (subtitle) subtitle.textContent = 'Puedes continuar a la siguiente etapa';

        // Mostrar mensaje de éxito
        this.mostrarMensajeInfo('success', 'Requisitos Obligatorios Completos', 'Todos los requisitos obligatorios están completos y listos para continuar.');

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
    actualizarModalFaltantes(faltantesObligatorios, totalObligatorios) {
        // Mantener header rojo
        const header = document.getElementById('modalHeader');
        const icon = document.getElementById('modalIcon');
        const title = document.getElementById('modalTitle');
        const subtitle = document.getElementById('modalSubtitle');

        if (header) header.style.background = 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)';
        if (icon) icon.className = 'fas fa-exclamation-triangle me-2';
        if (title) title.textContent = 'Requisitos Faltantes';
        if (subtitle) subtitle.textContent = `Faltan ${faltantesObligatorios} de ${totalObligatorios} requisitos obligatorios`;

        // Mostrar mensaje de advertencia
        this.mostrarMensajeInfo('warning', 'Requisitos Obligatorios Pendientes', `Debes completar ${faltantesObligatorios} requisitos obligatorios antes de continuar.`);

        // Actualizar botón
        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (btnValidar) {
            btnValidar.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Validar y Continuar (${totalObligatorios - faltantesObligatorios}/${totalObligatorios})`;
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
        // Contar SOLO los requisitos obligatorios
        const requisitosObligatorios = document.querySelectorAll('.requisito-item:not(.opcional)');
        const totalRequisitosObligatorios = requisitosObligatorios.length;
        const requisitosObligatoriosCompletos = document.querySelectorAll('.requisito-item:not(.opcional).completado').length;

        // Debug: mostrar elementos encontrados
        console.log('🔍 DEBUG verificarEstadoRequisitos:');
        console.log('  - Todos los requisito-item:', document.querySelectorAll('.requisito-item').length);
        console.log('  - Requisitos con clase opcional:', document.querySelectorAll('.requisito-item.opcional').length);
        console.log('  - Requisitos SIN clase opcional (obligatorios):', totalRequisitosObligatorios);
        console.log('  - Requisitos obligatorios completos:', requisitosObligatoriosCompletos);

        // Mostrar detalles de cada elemento
        document.querySelectorAll('.requisito-item').forEach((item, index) => {
            const isOpcional = item.classList.contains('opcional');
            const isCompletado = item.classList.contains('completado');
            const requisitoId = item.getAttribute('data-requisito-id');
            console.log(`    Requisito ${index + 1}: ID=${requisitoId}, opcional=${isOpcional}, completado=${isCompletado}, classes=[${item.className}]`);
        });

        // Contar archivos seleccionados para requisitos obligatorios pendientes
        let archivosObligatoriosSeleccionados = 0;
        requisitosObligatorios.forEach(item => {
            if (!item.classList.contains('completado')) {
                const fileInput = item.querySelector('.requisito-file-input[type="file"]');
                if (fileInput && fileInput.files && fileInput.files.length > 0) {
                    archivosObligatoriosSeleccionados++;
                }
            }
        });

        console.log('🔍 Estado de requisitos obligatorios:', {
            totalRequisitosObligatorios,
            requisitosObligatoriosCompletos,
            archivosObligatoriosSeleccionados
        });

        const btnValidar = document.getElementById('btnValidarYContinuar');
        if (!btnValidar) return;

        if (totalRequisitosObligatorios === 0) {
            // No hay requisitos obligatorios, puede continuar
            btnValidar.innerHTML = '<i class="fas fa-check me-2"></i>Continuar';
            btnValidar.className = 'btn btn-success';
            btnValidar.disabled = false;
        } else if (totalRequisitosObligatorios === requisitosObligatoriosCompletos) {
            // Todos los requisitos obligatorios están completos
            btnValidar.innerHTML = '<i class="fas fa-check me-2"></i>Requisitos Obligatorios Completos - Continuar';
            btnValidar.className = 'btn btn-success';
            btnValidar.disabled = false;
        } else if (archivosObligatoriosSeleccionados > 0) {
            // Hay archivos seleccionados para requisitos obligatorios pendientes
            btnValidar.innerHTML = `<i class="fas fa-upload me-2"></i>Validar y Continuar (${requisitosObligatoriosCompletos}/${totalRequisitosObligatorios})`;
            btnValidar.className = 'btn btn-primary';
            btnValidar.disabled = false;
        } else {
            // Faltan requisitos obligatorios
            btnValidar.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Validar y Continuar (${requisitosObligatoriosCompletos}/${totalRequisitosObligatorios})`;
            btnValidar.className = 'btn btn-warning';
            btnValidar.disabled = true;
        }
    }    /**
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
        console.log('🔍 Validando requisitos obligatorios en el backend...');

        this.mostrarEstadoValidacion('Validando requisitos obligatorios...', 50);
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

        // Solo verificar requisitos obligatorios faltantes
        const faltantesObligatorios = data.requisitos_obligatorios_faltantes || [];
        if (faltantesObligatorios.length > 0) {
            throw new Error(`Aún faltan ${faltantesObligatorios.length} requisitos obligatorios: ${faltantesObligatorios.map(r => r.nombre).join(', ')}`);
        }

        this.mostrarEstadoValidacion('Validación completada', 100);
        console.log('✅ Validación de requisitos obligatorios completada exitosamente');
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

    /**
     * Abrir modal para agendar firma
     */
    async abrirModalAgendaFirma(requisitoId) {
        try {
            console.log('📅 Abriendo modal para agendar firma, requisito ID:', requisitoId);

            // Obtener información de la solicitud actual
            const solicitudId = this.solicitudId;
            if (!solicitudId) {
                console.error('❌ No se encontró ID de solicitud');
                this.showToast('Error: No se pudo identificar la solicitud', 'error');
                return;
            }

            // Crear modal dinámico para agendar firma
            const modalHtml = `
                <div class="modal fade" id="modalAgendaFirma" tabindex="-1" aria-labelledby="modalAgendaFirmaLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content" style="border-radius: 16px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);">
                            <!-- Header -->
                            <div class="modal-header" style="background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); border: none; padding: 24px 32px 20px 32px;">
                                <h5 class="modal-title text-white fw-bold" id="modalAgendaFirmaLabel">
                                    <i class="fas fa-calendar-plus me-2"></i>
                                    Agendar Cita de Firma
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            
                            <!-- Body -->
                            <div class="modal-body" style="padding: 32px;">
                                <form id="formAgendaFirma">
                                    <div class="row g-3">
                                        <div class="col-md-6">
                                            <label for="fechaFirma" class="form-label fw-semibold">
                                                <i class="fas fa-calendar me-2 text-primary"></i>
                                                Fecha de la Cita *
                                            </label>
                                            <input type="date" class="form-control" id="fechaFirma" name="fecha" required>
                                        </div>
                                        <div class="col-md-6">
                                            <label for="horaFirma" class="form-label fw-semibold">
                                                <i class="fas fa-clock me-2 text-primary"></i>
                                                Hora de la Cita *
                                            </label>
                                            <input type="time" class="form-control" id="horaFirma" name="hora" required>
                                        </div>
                                        <div class="col-12">
                                            <label for="lugarFirma" class="form-label fw-semibold">
                                                <i class="fas fa-map-marker-alt me-2 text-primary"></i>
                                                Lugar de la Firma *
                                            </label>
                                            <select class="form-select" id="lugarFirma" name="lugar_firma" required>
                                                <option value="">Seleccionar lugar...</option>
                                                <option value="delivery">Delivery</option>
                                                <option value="apoyo">Apoyo</option>
                                                <option value="casa_matriz">Casa Matriz</option>
                                            </select>
                                        </div>
                                        <div class="col-12">
                                            <label for="comentariosFirma" class="form-label fw-semibold">
                                                <i class="fas fa-comment me-2 text-secondary"></i>
                                                Comentarios
                                            </label>
                                            <textarea class="form-control" id="comentariosFirma" name="comentarios" rows="3" placeholder="Comentarios adicionales sobre la cita..."></textarea>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            
                            <!-- Footer -->
                            <div class="modal-footer" style="padding: 24px 32px; border: none; background: #f8f9fa;">
                                <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                    <i class="fas fa-times me-2"></i>Cancelar
                                </button>
                                <button type="button" class="btn btn-primary" id="btnGuardarCitaFirma">
                                    <i class="fas fa-save me-2"></i>Agendar Cita
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remover modal existente si existe
            const existingModal = document.getElementById('modalAgendaFirma');
            if (existingModal) {
                existingModal.remove();
            }

            // Agregar modal al DOM
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Configurar event listener para guardar
            document.getElementById('btnGuardarCitaFirma').addEventListener('click', async () => {
                await this.guardarCitaFirma(solicitudId, requisitoId);
            });

            // Mostrar modal
            const modal = new bootstrap.Modal(document.getElementById('modalAgendaFirma'));
            modal.show();

            // Limpiar modal del DOM cuando se cierre
            document.getElementById('modalAgendaFirma').addEventListener('hidden.bs.modal', () => {
                document.getElementById('modalAgendaFirma').remove();
            });

        } catch (error) {
            console.error('❌ Error al abrir modal de agenda de firma:', error);
            this.showToast('Error al abrir el formulario de agenda', 'error');
        }
    }

    /**
     * Guardar cita de firma
     */
    async guardarCitaFirma(solicitudId, requisitoId) {
        try {
            const form = document.getElementById('formAgendaFirma');
            const formData = new FormData(form);

            // Validar campos requeridos
            const fecha = formData.get('fecha');
            const hora = formData.get('hora');
            const lugarFirma = formData.get('lugar_firma');

            if (!fecha || !hora || !lugarFirma) {
                this.showToast('Por favor completa todos los campos obligatorios', 'warning');
                return;
            }

            // Combinar fecha y hora
            const fechaHora = `${fecha}T${hora}:00`;

            const data = {
                solicitud_id: solicitudId,
                fecha_hora: fechaHora,
                lugar_firma: lugarFirma,
                comentarios: formData.get('comentarios') || ''
            };

            // Deshabilitar botón mientras se procesa
            const btnGuardar = document.getElementById('btnGuardarCitaFirma');
            const textoOriginal = btnGuardar.innerHTML;
            btnGuardar.disabled = true;
            btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';

            // Enviar solicitud
            const response = await fetch('/workflow/api/agenda-firma/crear-cita/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                this.showToast('Cita de firma agendada exitosamente', 'success');

                // Cerrar modal de agenda
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalAgendaFirma'));
                modal.hide();

                // Recargar requisitos para actualizar el estado
                await this.cargarRequisitos();

            } else {
                throw new Error(result.error || 'Error desconocido al agendar la cita');
            }

        } catch (error) {
            console.error('❌ Error al guardar cita de firma:', error);
            this.showToast('Error al agendar la cita: ' + error.message, 'error');
        } finally {
            // Restaurar botón
            const btnGuardar = document.getElementById('btnGuardarCitaFirma');
            if (btnGuardar) {
                btnGuardar.disabled = false;
                btnGuardar.innerHTML = textoOriginal;
            }
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
window.mostrarModalRequisitosFaltantes = function (solicitudId, nuevaEtapaId, nombreEtapa, callbackExito, callbackCancelacion) {
    if (window.modalRequisitos) {
        window.modalRequisitos.mostrarModal(solicitudId, nuevaEtapaId, nombreEtapa, callbackExito, callbackCancelacion);
    } else {
        console.error('❌ ModalRequisitos no está inicializado');
    }
};

window.cerrarModalRequisitos = function () {
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
window.testModalRequisitos = function () {
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