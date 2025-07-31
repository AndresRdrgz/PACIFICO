/**
 * Detalle Solicitud JavaScript
 * Maneja toda la funcionalidad del detalle de solicitudes
 */

class DetalleSolicitud {
    constructor(solicitudId) {
        this.solicitudId = solicitudId;
        this.solicitudData = null;
        this.comentarios = [];
        
        console.log('DetalleSolicitud initialized with ID:', solicitudId);
        this.init();
    }

    init() {
        console.log('🔄 init() called');
        this.setupEventListeners();
        console.log('✅ Event listeners setup completed');
        this.loadSolicitudData();
        console.log('✅ loadSolicitudData() called');
        this.initializeComponents();
        console.log('✅ initializeComponents() completed');
    }

    /**
     * Configura los event listeners
     */
    setupEventListeners() {
        // Botón Asignar
        const btnAsignar = document.getElementById('btnAsignar');
        if (btnAsignar) {
            btnAsignar.addEventListener('click', () => this.asignarSolicitud());
        }

        // Botón Devolver
        const btnDevolver = document.getElementById('btnDevolver');
        if (btnDevolver) {
            btnDevolver.addEventListener('click', () => this.devolverSolicitud());
        }

        // Botón Anular
        const btnAnular = document.getElementById('btnAnular');
        if (btnAnular) {
            btnAnular.addEventListener('click', () => this.anularSolicitud());
        }

        // Botón Cambiar Estado
        const btnCambiarEstado = document.getElementById('btnCambiarEstado');
        if (btnCambiarEstado) {
            btnCambiarEstado.addEventListener('click', () => this.mostrarModalCambiarEstado());
        }

        // Formulario de comentarios
        const comentarioForm = document.getElementById('comentarioForm');
        if (comentarioForm) {
            comentarioForm.addEventListener('submit', (e) => this.enviarComentario(e));
        }

        // Tabs de navegación
        this.setupTabListeners();
    }

    /**
     * Configura los listeners de las pestañas
     */
    setupTabListeners() {
        const tabs = document.querySelectorAll('#solicitudTabs .nav-link');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetId = e.target.getAttribute('data-bs-target');
                this.onTabChanged(targetId);
            });
        });
    }

    /**
     * Maneja el cambio de pestañas
     */
    onTabChanged(targetId) {
        switch (targetId) {
            case '#tabDatosPersonales':
                this.renderDatosPersonales();
                break;
            case '#tabResultadoConsulta':
                this.renderResultadoConsulta();
                break;
            case '#tabReferencias':
                this.renderReferencias();
                break;
            case '#tabDocumentos':
                this.renderDocumentos();
                break;
        }
    }

    /**
     * Inicializa componentes de Bootstrap y otros
     */
    initializeComponents() {
        // Inicializar tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Inicializar popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    /**
     * Carga los datos de la solicitud desde la API
     */
    async loadSolicitudData() {
        try {
            console.log('🔄 loadSolicitudData() called for ID:', this.solicitudId);
            console.log('🔗 Making API call to:', `/workflow/api/solicitudes/${this.solicitudId}/detalle/`);
            this.showLoadingOverlay();
            
            const response = await fetch(`/workflow/api/solicitudes/${this.solicitudId}/detalle/`);
            console.log('📡 API Response status:', response.status);
            console.log('📡 API Response headers:', response.headers);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('📊 Received solicitud data:', data);
            console.log('📋 Requisitos count:', data.requisitos ? data.requisitos.length : 'undefined');
            
            if (!data.success) {
                throw new Error(data.error || 'Error al cargar los datos');
            }
            
            this.solicitudData = data;
            console.log('💾 Stored solicitudData:', this.solicitudData);
            this.renderSolicitudData();
            
            // Cargar comentarios por separado
            await this.loadComentarios();
            
        } catch (error) {
            console.error('❌ Error loading solicitud data:', error);
            this.showError('Error al cargar los datos de la solicitud: ' + error.message);
        } finally {
            this.hideLoadingOverlay();
        }
    }

    /**
     * Carga los comentarios de la solicitud
     */
    async loadComentarios() {
        try {
            const response = await fetch(`/workflow/api/solicitudes/${this.solicitudId}/comentarios/`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.comentarios = data.comentarios;
                this.renderComentarios();
            }
            
        } catch (error) {
            console.error('Error loading comentarios:', error);
            this.renderComentarios([]); // Render empty comments on error
        }
    }

    /**
     * Renderiza todos los datos de la solicitud
     */
    renderSolicitudData() {
        console.log('🔄 renderSolicitudData called');
        console.log('📊 solicitudData:', this.solicitudData);
        
        console.log('🎨 Rendering header...');
        this.renderHeader();
        
        console.log('🎨 Rendering info cards...');
        this.renderInfoCards();
        
        console.log('🎨 Rendering historial...');
        this.renderHistorial();
        
        console.log('🎨 Rendering datos personales...');
        this.renderDatosPersonales();
        
        console.log('🎨 Rendering documentos...');
        this.renderDocumentos();
        
        console.log('🎨 Updating button states...');
        this.updateButtonStates();
        
        // Hide all loading states
        console.log('🎨 Hiding loading states...');
        this.hideAllLoadingStates();
        
        console.log('✅ renderSolicitudData completed');
    }

    /**
     * Hide all loading states
     */
    hideAllLoadingStates() {
        console.log('🔄 hideAllLoadingStates called');
        const loadingElements = [
            'documentosLoading',
            'comentariosAnalistaLoading',
            'resultadoConsultaLoading',
            'resultadoComiteLoading'
        ];
        
        loadingElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                console.log(`✅ Hiding loading element: ${id}`);
                element.style.display = 'none';
            } else {
                console.log(`❌ Loading element not found: ${id}`);
            }
        });
    }

    /**
     * Renderiza el header de la solicitud
     */
    renderHeader() {
        try {
            console.log('🎨 renderHeader: Starting...');
            const data = this.solicitudData;
            
            // Código de solicitud
            const codigoElement = document.getElementById('solicitudCodigo');
            if (codigoElement) {
                codigoElement.textContent = data.general?.codigo || 'N/A';
            }

            // Información del cliente
            const clienteElement = document.getElementById('solicitudCliente');
            if (clienteElement && data.cliente) {
                const nombre = data.cliente.nombre || 'N/A';
                const cedula = data.cliente.cedula || 'N/A';
                clienteElement.textContent = `${nombre} - CI: ${cedula}`;
            } else if (clienteElement && data.cotizacion) {
                const nombre = data.cotizacion.nombre_cliente || 'N/A';
                const cedula = data.cotizacion.cedula_cliente || 'N/A';
                clienteElement.textContent = `${nombre} - CI: ${cedula}`;
            }
            console.log('✅ renderHeader: Completed');
        } catch (error) {
            console.error('❌ renderHeader: Error:', error);
        }
    }

    /**
     * Renderiza las cards de información general
     */
    renderInfoCards() {
        try {
            console.log('🎨 renderInfoCards: Starting...');
            const data = this.solicitudData;
            
            // Etapa actual
            const etapaElement = document.getElementById('solicitudEtapa');
            if (etapaElement && data.general?.etapa_actual) {
                etapaElement.textContent = data.general.etapa_actual.nombre;
            }

            // Monto solicitado
            const montoElement = document.getElementById('solicitudMonto');
            if (montoElement && data.cotizacion) {
                const monto = data.cotizacion.monto_prestamo || 0;
                montoElement.textContent = this.formatCurrency(monto);
            }

            // Producto/Pipeline
            const productoElement = document.getElementById('solicitudProducto');
            if (productoElement && data.general?.pipeline) {
                productoElement.textContent = data.general.pipeline.nombre;
            }

            // Progreso
            this.renderProgreso(data.progreso || 0);

            // Propietario
            const propietarioElement = document.getElementById('solicitudPropietario');
            if (propietarioElement && data.general?.creada_por) {
                propietarioElement.textContent = data.general.creada_por.nombre_completo;
            }

            // Asignado a
            const asignadoElement = document.getElementById('solicitudAsignado');
            if (asignadoElement) {
                if (data.general?.asignada_a) {
                    asignadoElement.textContent = data.general.asignada_a.nombre_completo;
                } else {
                    asignadoElement.textContent = 'Sin asignar';
                    asignadoElement.classList.add('text-muted');
                }
            }

            // Fecha de inicio
            const fechaInicioElement = document.getElementById('solicitudFechaInicio');
            if (fechaInicioElement && data.general?.fecha_creacion) {
                const fecha = new Date(data.general.fecha_creacion);
                fechaInicioElement.textContent = this.formatDate(fecha);
            }

            // SLA
            const slaElement = document.getElementById('solicitudSLA');
            if (slaElement && data.general?.sla) {
                this.renderSLA(slaElement, data.general.sla);
            }
            console.log('✅ renderInfoCards: Completed');
        } catch (error) {
            console.error('❌ renderInfoCards: Error:', error);
        }
    }

    /**
     * Renderiza el progreso del pipeline
     */
    renderProgreso(progreso) {
        const progressBar = document.getElementById('solicitudProgreso');
        const progressText = document.getElementById('solicitudProgresoText');
        
        if (progressBar) {
            progressBar.style.width = `${progreso}%`;
            progressBar.setAttribute('aria-valuenow', progreso);
        }
        
        if (progressText) {
            progressText.textContent = `${progreso}%`;
        }
    }

    /**
     * Renderiza información del SLA
     */
    renderSLA(element, slaInfo) {
        if (slaInfo.estado === 'sin_sla') {
            element.textContent = 'Sin SLA';
            element.className = 'text-muted fw-semibold';
        } else if (slaInfo.estado === 'vencido') {
            element.textContent = 'Vencido';
            element.className = 'text-danger fw-semibold';
        } else if (slaInfo.estado === 'por_vencer') {
            element.textContent = slaInfo.tiempo_restante_formateado;
            element.className = 'text-warning fw-semibold';
        } else {
            element.textContent = slaInfo.tiempo_restante_formateado;
            element.className = 'text-success fw-semibold';
        }
    }

    /**
     * Renderiza el historial de actividades
     */
    renderHistorial() {
        try {
            console.log('🎨 renderHistorial: Starting...');
            const historialElement = document.getElementById('solicitudHistorial');
            if (!historialElement || !this.solicitudData.historial) {
                console.log('⚠️ renderHistorial: Element or data not found, skipping');
                return;
            }

            const historial = this.solicitudData.historial;
            
            if (historial.length === 0) {
                historialElement.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-history fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No hay actividades registradas</p>
                    </div>
                `;
                return;
            }

            let html = '<div class="timeline">';
            
            historial.forEach((item, index) => {
                const isCompleted = item.fecha_fin !== null;
                const isActive = index === 0 && !isCompleted;
                
                html += `
                    <div class="timeline-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}">
                        <div class="timeline-marker">
                            <i class="fas ${isCompleted ? 'fa-check' : (isActive ? 'fa-clock' : 'fa-circle')}"></i>
                        </div>
                        <div class="timeline-content">
                            <h6 class="timeline-title">${item.etapa ? item.etapa.nombre : 'Sin etapa'}</h6>
                            <p class="timeline-description">
                                ${item.usuario_responsable ? item.usuario_responsable.nombre_completo : 'Sistema'}
                            </p>
                            <small class="timeline-time text-muted">
                                <i class="fas fa-calendar-alt me-1"></i>
                                ${this.formatDate(new Date(item.fecha_inicio))}
                                ${item.fecha_fin ? ' - ' + this.formatDate(new Date(item.fecha_fin)) : ''}
                            </small>
                            ${item.comentarios ? `<p class="timeline-comments mt-2">${item.comentarios}</p>` : ''}
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            historialElement.innerHTML = html;
            console.log('✅ renderHistorial: Completed');
        } catch (error) {
            console.error('❌ renderHistorial: Error:', error);
        }
    }

    /**
     * Renderiza los datos personales
     */
    renderDatosPersonales() {
        try {
            console.log('🎨 renderDatosPersonales: Starting...');
            const contentElement = document.getElementById('datosPersonalesContent');
            if (!contentElement) {
                console.log('⚠️ renderDatosPersonales: Element not found, skipping');
                return;
            }

            const data = this.solicitudData;
            let cliente = data.cliente;
            
            // Si no hay cliente, usar datos de cotización
            if (!cliente && data.cotizacion) {
                cliente = {
                    nombre: data.cotizacion.nombre_cliente,
                    cedula: data.cotizacion.cedula_cliente,
                    telefono: null,
                    email: null,
                    direccion: null
                };
            }

            if (!cliente) {
                contentElement.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-user-slash fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No hay datos personales disponibles</p>
                    </div>
                `;
                return;
            }

        const html = `
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="info-group">
                        <label class="info-label">Nombre Completo</label>
                        <div class="info-value">${cliente.nombre || 'N/A'}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-group">
                        <label class="info-label">Cédula de Identidad</label>
                        <div class="info-value">${cliente.cedula || 'N/A'}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-group">
                        <label class="info-label">Teléfono</label>
                        <div class="info-value">${cliente.telefono || 'N/A'}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-group">
                        <label class="info-label">Email</label>
                        <div class="info-value">${cliente.email || 'N/A'}</div>
                    </div>
                </div>
                <div class="col-12">
                    <div class="info-group">
                        <label class="info-label">Dirección</label>
                        <div class="info-value">${cliente.direccion || 'N/A'}</div>
                    </div>
                </div>
            </div>
        `;

        contentElement.innerHTML = html;
        console.log('✅ renderDatosPersonales: Completed');
    } catch (error) {
        console.error('❌ renderDatosPersonales: Error:', error);
    }
    }

    /**
     * Renderiza el resultado de la consulta
     */
    renderResultadoConsulta() {
        try {
            console.log('🎨 renderResultadoConsulta: Starting...');
            const comentariosElement = document.getElementById('comentariosAnalistaContent');
            const comiteElement = document.getElementById('resultadoComiteContent');
            
            // Por ahora renderizar placeholders
            if (comentariosElement) {
                comentariosElement.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-user-md fa-3x text-muted mb-3"></i>
                        <p class="text-muted">Comentarios del analista no disponibles</p>
                    </div>
                `;
            }
            
            if (comiteElement) {
                comiteElement.innerHTML = `
                    <div class="text-center py-4">
                        <i class="fas fa-users fa-3x text-muted mb-3"></i>
                        <p class="text-muted">Resultado del comité no disponible</p>
                    </div>
                `;
            }
            console.log('✅ renderResultadoConsulta: Completed');
        } catch (error) {
            console.error('❌ renderResultadoConsulta: Error:', error);
        }
    }

    /**
     * Renderiza las referencias
     */
    renderReferencias() {
        try {
            console.log('🎨 renderReferencias: Starting...');
            const contentElement = document.getElementById('referenciasContent');
            if (!contentElement) {
                console.log('⚠️ renderReferencias: Element not found, skipping');
                return;
            }

            // Por ahora renderizar placeholder
            contentElement.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-address-book fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Referencias no disponibles</p>
                </div>
            `;
            console.log('✅ renderReferencias: Completed');
        } catch (error) {
            console.error('❌ renderReferencias: Error:', error);
        }
    }

    /**
     * Renderiza los documentos/requisitos
     */
    renderDocumentos() {
        try {
            console.log('📄 renderDocumentos called');
            const contentElement = document.getElementById('documentosContent');
            if (!contentElement) {
                console.error('❌ documentosContent element not found');
                return;
            }

            const requisitos = this.solicitudData.requisitos;
            console.log('📋 Requisitos data:', requisitos);
            
            if (!requisitos || requisitos.length === 0) {
                console.log('⚠️ No requisitos found, showing empty state');
                contentElement.innerHTML = `
                    <div class="text-center py-12">
                        <div class="inline-flex items-center justify-center w-20 h-20 mb-4 bg-gray-100 rounded-full">
                            <i class="fas fa-file-alt fa-2x text-gray-400"></i>
                        </div>
                        <h3 class="text-lg font-semibold text-gray-700 mb-2">No hay requisitos</h3>
                        <p class="text-gray-500">Esta solicitud no tiene requisitos asignados.</p>
                    </div>
                `;
                return;
            }

        // Calculate statistics
        const totalRequisitos = requisitos.length;
        const completedRequisitos = requisitos.filter(req => req.cumplido).length;
        const pendingRequisitos = totalRequisitos - completedRequisitos;
        const completionPercentage = totalRequisitos > 0 ? Math.round((completedRequisitos / totalRequisitos) * 100) : 0;

        let html = `
            <!-- Summary Section -->
            <div class="requisitos-summary">
                <div class="requisitos-summary-header">
                    <div class="requisitos-summary-icon">
                        <i class="fas fa-clipboard-check"></i>
                    </div>
                    <h3 class="requisitos-summary-title">Resumen de Requisitos</h3>
                </div>
                <div class="requisitos-summary-stats">
                    <div class="requisito-stat">
                        <div class="requisito-stat-number">${totalRequisitos}</div>
                        <div class="requisito-stat-label">Total</div>
                    </div>
                    <div class="requisito-stat completed">
                        <div class="requisito-stat-number">${completedRequisitos}</div>
                        <div class="requisito-stat-label">Completados</div>
                    </div>
                    <div class="requisito-stat pending">
                        <div class="requisito-stat-number">${pendingRequisitos}</div>
                        <div class="requisito-stat-label">Pendientes</div>
                    </div>
                    <div class="requisito-stat">
                        <div class="requisito-stat-number">${completionPercentage}%</div>
                        <div class="requisito-stat-label">Progreso</div>
                    </div>
                </div>
            </div>

            <!-- Requisitos List -->
            <div class="requisitos-grid">
        `;
        
        requisitos.forEach((req, index) => {
            const statusClass = req.cumplido ? 'completed' : 'pending';
            const statusIcon = req.cumplido ? 'fa-check-circle' : 'fa-clock';
            const statusText = req.cumplido ? 'Completado' : 'Pendiente';
            
            html += `
                <div class="requisito-item" data-requisito-id="${req.id}">
                    <div class="requisito-header">
                        <h4 class="requisito-title">${req.requisito.nombre}</h4>
                        <span class="requisito-status ${statusClass}">
                            <i class="fas ${statusIcon}"></i>
                            ${statusText}
                        </span>
                    </div>
                    
                    ${req.requisito.descripcion ? `
                        <div class="requisito-description">
                            ${req.requisito.descripcion}
                        </div>
                    ` : ''}
                    
                    <div class="requisito-actions">
                        ${!req.cumplido ? `
                            <button class="requisito-upload-btn" onclick="detalleSolicitud.uploadRequisito(${req.id})">
                                <i class="fas fa-upload"></i>
                                Subir Documento
                            </button>
                        ` : ''}
                        
                        ${req.archivo ? `
                            <a href="${req.archivo}" target="_blank" class="requisito-view-btn">
                                <i class="fas fa-eye"></i>
                                Ver Documento
                            </a>
                        ` : ''}
                    </div>
                    
                    ${req.observaciones ? `
                        <div class="requisito-observations">
                            <div class="requisito-observations-label">Observaciones</div>
                            <div class="requisito-observations-text">${req.observaciones}</div>
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        html += '</div>';
        contentElement.innerHTML = html;
        console.log('✅ renderDocumentos completed successfully');
    } catch (error) {
        console.error('❌ renderDocumentos: Error:', error);
    }
    }

    /**
     * Upload requisito functionality
     */
    uploadRequisito(requisitoId) {
        // Create file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf,.doc,.docx,.jpg,.jpeg,.png';
        fileInput.style.display = 'none';
        
        fileInput.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (!file) return;
            
            try {
                await this.submitRequisitoFile(requisitoId, file);
            } catch (error) {
                console.error('Error uploading requisito:', error);
                this.showError('Error al subir el documento. Intente nuevamente.');
            }
            
            // Clean up
            document.body.removeChild(fileInput);
        });
        
        document.body.appendChild(fileInput);
        fileInput.click();
    }

    /**
     * Submit requisito file to server
     */
    async submitRequisitoFile(requisitoId, file) {
        const formData = new FormData();
        formData.append('archivo', file);
        formData.append('observaciones', 'Documento subido desde detalle de solicitud');
        
        const response = await fetch(`/workflow/solicitud/${this.solicitudId}/requisito/${requisitoId}/actualizar/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': this.getCSRFToken()
            }
        });
        
        if (response.ok) {
            this.showSuccess('Documento subido exitosamente');
            // Refresh the data
            await this.refreshData();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error al subir el documento');
        }
    }

    /**
     * Renderiza los comentarios
     */
    renderComentarios() {
        const comentariosElement = document.getElementById('solicitudComentarios');
        if (!comentariosElement) return;

        if (this.comentarios.length === 0) {
            comentariosElement.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No hay comentarios</p>
                </div>
            `;
            return;
        }

        let html = '<div class="comentarios-list">';
        
        this.comentarios.forEach(comentario => {
            html += `
                <div class="comentario-item mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="comentario-header">
                            <strong>${comentario.usuario}</strong>
                            <small class="text-muted ms-2">${this.formatDate(new Date(comentario.fecha))}</small>
                        </div>
                    </div>
                    <div class="comentario-content mt-2">
                        ${comentario.texto}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        comentariosElement.innerHTML = html;
    }

    /**
     * Actualiza el estado de los botones según los permisos
     */
    updateButtonStates() {
        const data = this.solicitudData.general;
        
        // Botón Asignar
        const btnAsignar = document.getElementById('btnAsignar');
        if (btnAsignar) {
            btnAsignar.disabled = !data.puede_asignar;
            if (!data.puede_asignar) {
                btnAsignar.classList.add('d-none');
            }
        }

        // Botón Devolver
        const btnDevolver = document.getElementById('btnDevolver');
        if (btnDevolver) {
            btnDevolver.disabled = !data.puede_devolver;
            if (!data.puede_devolver) {
                btnDevolver.classList.add('d-none');
            }
        }

        // Botón Cambiar Estado
        const btnCambiarEstado = document.getElementById('btnCambiarEstado');
        if (btnCambiarEstado) {
            btnCambiarEstado.disabled = !data.puede_cambiar_estado;
        }
    }

    /**
     * Refresca los datos de la solicitud
     */
    async refreshData() {
        await this.loadSolicitudData();
    }

    /**
     * Asigna la solicitud al usuario actual
     */
    async asignarSolicitud() {
        try {
            const response = await fetch(`/workflow/api/solicitudes/${this.solicitudId}/tomar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('Solicitud asignada exitosamente');
                await this.refreshData(); // Recargar datos
            } else {
                this.showError(data.error || 'Error al asignar la solicitud');
            }
        } catch (error) {
            console.error('Error assigning solicitud:', error);
            this.showError('Error al asignar la solicitud');
        }
    }

    /**
     * Devuelve la solicitud a la bandeja grupal
     */
    async devolverSolicitud() {
        if (!confirm('¿Está seguro de que desea devolver esta solicitud?')) {
            return;
        }

        try {
            const response = await fetch(`/workflow/api/solicitudes/${this.solicitudId}/devolver/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess('Solicitud devuelta exitosamente');
                await this.refreshData(); // Recargar datos
            } else {
                this.showError(data.error || 'Error al devolver la solicitud');
            }
        } catch (error) {
            console.error('Error returning solicitud:', error);
            this.showError('Error al devolver la solicitud');
        }
    }

    /**
     * Anula la solicitud
     */
    async anularSolicitud() {
        if (!confirm('¿Está seguro de que desea anular esta solicitud? Esta acción no se puede deshacer.')) {
            return;
        }

        // TODO: Implementar endpoint para anular solicitud
        this.showWarning('Funcionalidad de anular solicitud en desarrollo');
    }

    /**
     * Muestra el modal para cambiar estado
     */
    mostrarModalCambiarEstado() {
        // TODO: Implementar modal para cambiar estado
        this.showInfo('Modal de cambio de estado en desarrollo');
    }

    /**
     * Envía un nuevo comentario
     */
    async enviarComentario(event) {
        event.preventDefault();
        
        const comentarioInput = document.getElementById('comentarioInput');
        const texto = comentarioInput.value.trim();
        
        if (!texto) {
            this.showWarning('Por favor ingrese un comentario');
            return;
        }

        try {
            const response = await fetch(`/workflow/api/solicitudes/${this.solicitudId}/comentarios/crear/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ comentario: texto })
            });

            const data = await response.json();

            if (data.success) {
                comentarioInput.value = '';
                this.showSuccess('Comentario agregado exitosamente');
                await this.loadComentarios(); // Recargar comentarios
            } else {
                this.showError(data.error || 'Error al agregar el comentario');
            }
        } catch (error) {
            console.error('Error adding comment:', error);
            this.showError('Error al agregar el comentario');
        }
    }

    // Utility methods

    /**
     * Obtiene el token CSRF
     */
    getCSRFToken() {
        // Try multiple ways to get CSRF token
        let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!token) {
            token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        }
        if (!token) {
            // Try to get from cookie
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    token = value;
                    break;
                }
            }
        }
        return token || '';
    }

    /**
     * Formatea una fecha
     */
    formatDate(date) {
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Formatea una cantidad monetaria
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    /**
     * Muestra overlay de carga
     */
    showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }

    /**
     * Oculta overlay de carga
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    /**
     * Muestra mensaje de éxito
     */
    showSuccess(message) {
        this.showToast(message, 'success');
    }

    /**
     * Muestra mensaje de error
     */
    showError(message) {
        this.showToast(message, 'danger');
    }

    /**
     * Muestra mensaje de advertencia
     */
    showWarning(message) {
        this.showToast(message, 'warning');
    }

    /**
     * Muestra mensaje informativo
     */
    showInfo(message) {
        this.showToast(message, 'info');
    }

    /**
     * Muestra un toast de notificación
     */
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;

        const toastId = 'toast_' + Date.now();
        const iconMap = {
            success: 'fa-check-circle',
            danger: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header text-bg-${type}">
                    <i class="fas ${iconMap[type]} me-2"></i>
                    <strong class="me-auto">Notificación</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        
        toast.show();
        
        // Remover el toast del DOM después de que se oculte
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el ID de la solicitud desde el atributo data del body o una variable global
    const solicitudId = document.body.dataset.solicitudId || window.solicitudId;
    
    if (solicitudId) {
        window.detalleSolicitud = new DetalleSolicitud(solicitudId);
    } else {
        console.error('No se pudo obtener el ID de la solicitud');
    }
});
