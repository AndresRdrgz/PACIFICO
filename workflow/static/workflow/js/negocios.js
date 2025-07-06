/**
 * Funcionalidades avanzadas para la vista de tabla de negocios
 * Sistema de Workflow - PACIFICO
 */

class NegociosTableManager {
    constructor() {
        this.solicitudesSeleccionadas = new Set();
        this.vistaCompacta = false;
        this.init();
    }

    init() {
        this.initSeleccionMasiva();
        this.initOrdenamiento();
        this.initBusqueda();
        this.initVistaCompacta();
        this.initExportacion();
        this.initAccionesMasivas();
        this.initTooltips();
        this.initResponsive();
    }

    initSeleccionMasiva() {
        const selectAll = document.getElementById('selectAll');
        const checkboxes = document.querySelectorAll('.solicitud-checkbox');

        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                checkboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                    if (e.target.checked) {
                        this.solicitudesSeleccionadas.add(checkbox.value);
                    } else {
                        this.solicitudesSeleccionadas.delete(checkbox.value);
                    }
                });
                this.actualizarAccionesMasivas();
            });
        }

        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.solicitudesSeleccionadas.add(e.target.value);
                } else {
                    this.solicitudesSeleccionadas.delete(e.target.value);
                }
                this.actualizarAccionesMasivas();
            });
        });
    }

    actualizarAccionesMasivas() {
        const accionesMasivas = document.getElementById('accionesMasivas');
        const seleccionadosCount = document.getElementById('seleccionadosCount');

        if (this.solicitudesSeleccionadas.size > 0) {
            accionesMasivas.style.display = 'block';
            seleccionadosCount.textContent = this.solicitudesSeleccionadas.size;
        } else {
            accionesMasivas.style.display = 'none';
        }
    }

    initOrdenamiento() {
        const sortableHeaders = document.querySelectorAll('.sortable');
        sortableHeaders.forEach(header => {
            header.addEventListener('click', (e) => {
                const sortField = e.currentTarget.dataset.sort;
                const currentUrl = new URL(window.location);
                currentUrl.searchParams.set('ordenar', sortField);
                window.location.href = currentUrl.toString();
            });
        });
    }

    initBusqueda() {
        const busquedaInput = document.getElementById('busqueda');
        if (busquedaInput) {
            let timeoutId;
            busquedaInput.addEventListener('input', (e) => {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    this.filtrarTabla(e.target.value);
                }, 300);
            });
        }
    }

    filtrarTabla(searchTerm) {
        const rows = document.querySelectorAll('.solicitud-row');
        const searchLower = searchTerm.toLowerCase();
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchLower)) {
                row.style.display = '';
                row.classList.remove('filtered-out');
            } else {
                row.style.display = 'none';
                row.classList.add('filtered-out');
            }
        });

        this.actualizarContadorFiltrado();
    }

    actualizarContadorFiltrado() {
        const totalRows = document.querySelectorAll('.solicitud-row').length;
        const visibleRows = document.querySelectorAll('.solicitud-row:not(.filtered-out)').length;
        
        // Mostrar contador si hay filtros aplicados
        const busquedaInput = document.getElementById('busqueda');
        if (busquedaInput && busquedaInput.value) {
            this.mostrarContadorFiltrado(visibleRows, totalRows);
        }
    }

    mostrarContadorFiltrado(visible, total) {
        let contador = document.getElementById('contadorFiltrado');
        if (!contador) {
            contador = document.createElement('div');
            contador.id = 'contadorFiltrado';
            contador.className = 'alert alert-info alert-sm mt-2';
            const tabla = document.getElementById('tablaSolicitudes');
            tabla.parentNode.insertBefore(contador, tabla);
        }
        
        contador.innerHTML = `
            <i class="fas fa-filter me-2"></i>
            Mostrando ${visible} de ${total} solicitudes
            <button type="button" class="btn btn-sm btn-outline-secondary ms-2" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
    }

    initVistaCompacta() {
        const toggleVista = document.getElementById('toggleVista');
        if (toggleVista) {
            toggleVista.addEventListener('click', () => {
                this.vistaCompacta = !this.vistaCompacta;
                const tabla = document.getElementById('tablaSolicitudes');
                
                if (this.vistaCompacta) {
                    tabla.classList.add('table-sm');
                    toggleVista.innerHTML = '<i class="fas fa-expand-alt"></i>';
                    toggleVista.title = 'Vista expandida';
                } else {
                    tabla.classList.remove('table-sm');
                    toggleVista.innerHTML = '<i class="fas fa-compress-alt"></i>';
                    toggleVista.title = 'Vista compacta';
                }
            });
        }
    }

    initExportacion() {
        const exportarExcel = document.getElementById('exportarExcel');
        const exportarPDF = document.getElementById('exportarPDF');

        if (exportarExcel) {
            exportarExcel.addEventListener('click', () => {
                this.exportarAExcel();
            });
        }

        if (exportarPDF) {
            exportarPDF.addEventListener('click', () => {
                this.exportarAPDF();
            });
        }
    }

    exportarAExcel() {
        // Implementar exportación a Excel
        const solicitudes = this.obtenerDatosTabla();
        
        // Crear CSV
        let csv = 'Código,Pipeline,Etapa,Progreso,SLA,Asignado,Creado por,Fecha Creación,Estado\n';
        
        solicitudes.forEach(solicitud => {
            csv += `"${solicitud.codigo}","${solicitud.pipeline}","${solicitud.etapa}","${solicitud.progreso}","${solicitud.sla}","${solicitud.asignado}","${solicitud.creadoPor}","${solicitud.fechaCreacion}","${solicitud.estado}"\n`;
        });

        // Descargar archivo
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `solicitudes_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    exportarAPDF() {
        // Implementar exportación a PDF
        alert('Funcionalidad de exportación a PDF en desarrollo');
    }

    obtenerDatosTabla() {
        const rows = document.querySelectorAll('.solicitud-row:not(.filtered-out)');
        const datos = [];

        rows.forEach(row => {
            const codigo = row.querySelector('td:nth-child(2) a').textContent.trim();
            const pipeline = row.querySelector('td:nth-child(3) .badge').textContent.trim();
            const etapa = row.querySelector('td:nth-child(4) .badge').textContent.trim();
            const progreso = row.querySelector('td:nth-child(5) small').textContent.trim();
            const sla = row.querySelector('td:nth-child(6) .badge')?.textContent.trim() || '-';
            const asignado = row.querySelector('td:nth-child(7) span')?.textContent.trim() || 'Sin asignar';
            const creadoPor = row.querySelector('td:nth-child(8) span').textContent.trim();
            const fechaCreacion = row.querySelector('td:nth-child(9) small:first-child').textContent.trim();
            const estado = row.querySelector('td:nth-child(11) .badge').textContent.trim();

            datos.push({
                codigo, pipeline, etapa, progreso, sla, asignado, creadoPor, fechaCreacion, estado
            });
        });

        return datos;
    }

    initAccionesMasivas() {
        const asignarMasivo = document.getElementById('asignarMasivo');
        const cambiarEtapaMasivo = document.getElementById('cambiarEtapaMasivo');
        const eliminarMasivo = document.getElementById('eliminarMasivo');

        if (asignarMasivo) {
            asignarMasivo.addEventListener('click', () => {
                this.asignarMasivo();
            });
        }

        if (cambiarEtapaMasivo) {
            cambiarEtapaMasivo.addEventListener('click', () => {
                this.cambiarEtapaMasivo();
            });
        }

        if (eliminarMasivo) {
            eliminarMasivo.addEventListener('click', () => {
                this.eliminarMasivo();
            });
        }
    }

    asignarMasivo() {
        if (this.solicitudesSeleccionadas.size > 0) {
            // Mostrar modal para seleccionar usuario
            this.mostrarModalAsignacion();
        }
    }

    cambiarEtapaMasivo() {
        if (this.solicitudesSeleccionadas.size > 0) {
            // Mostrar modal para seleccionar etapa
            this.mostrarModalCambioEtapa();
        }
    }

    eliminarMasivo() {
        if (this.solicitudesSeleccionadas.size > 0) {
            if (confirm(`¿Estás seguro de eliminar ${this.solicitudesSeleccionadas.size} solicitudes?`)) {
                // Implementar eliminación masiva
                this.ejecutarEliminacionMasiva();
            }
        }
    }

    mostrarModalAsignacion() {
        // Crear modal dinámicamente
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'modalAsignacion';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Asignar Solicitudes</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Selecciona el usuario para asignar ${this.solicitudesSeleccionadas.size} solicitudes:</p>
                        <select class="form-select" id="usuarioAsignacion">
                            <option value="">Selecciona un usuario...</option>
                            <!-- Aquí se cargarían los usuarios disponibles -->
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-success" onclick="negociosManager.ejecutarAsignacionMasiva()">Asignar</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }

    mostrarModalCambioEtapa() {
        // Implementar modal de cambio de etapa
        alert('Modal de cambio de etapa en desarrollo');
    }

    ejecutarAsignacionMasiva() {
        const usuarioId = document.getElementById('usuarioAsignacion').value;
        if (usuarioId) {
            // Implementar lógica de asignación masiva
            console.log('Asignando solicitudes:', Array.from(this.solicitudesSeleccionadas), 'al usuario:', usuarioId);
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalAsignacion'));
            modal.hide();
            
            // Limpiar selección
            this.solicitudesSeleccionadas.clear();
            this.actualizarAccionesMasivas();
        }
    }

    ejecutarEliminacionMasiva() {
        // Implementar eliminación masiva
        console.log('Eliminando solicitudes:', Array.from(this.solicitudesSeleccionadas));
        
        // Limpiar selección
        this.solicitudesSeleccionadas.clear();
        this.actualizarAccionesMasivas();
    }

    initTooltips() {
        // Inicializar tooltips de Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initResponsive() {
        // Manejar responsive de la tabla
        const tabla = document.getElementById('tablaSolicitudes');
        if (tabla) {
            const checkResponsive = () => {
                if (window.innerWidth < 768) {
                    tabla.classList.add('table-responsive-sm');
                } else {
                    tabla.classList.remove('table-responsive-sm');
                }
            };

            window.addEventListener('resize', checkResponsive);
            checkResponsive();
        }
    }
}

// Función global para eliminar solicitud individual
function eliminarSolicitud(solicitudId) {
    if (confirm('¿Estás seguro de eliminar esta solicitud?')) {
        // Implementar eliminación individual
        console.log('Eliminando solicitud:', solicitudId);
        
        // Aquí se haría la llamada AJAX para eliminar
        fetch(`/workflow/api/solicitudes/${solicitudId}/eliminar/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remover fila de la tabla
                const row = document.querySelector(`[data-solicitud-id="${solicitudId}"]`);
                if (row) {
                    row.remove();
                }
            } else {
                alert('Error al eliminar la solicitud');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar la solicitud');
        });
    }
}

// Función para obtener cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.negociosManager = new NegociosTableManager();
}); 