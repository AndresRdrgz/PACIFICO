// Make functions globally available
window.loadComments = loadComments;
window.submitComment = submitComment;
window.showSuccess = showSuccess;
window.showError = showError;
window.showWarning = showWarning;
window.showInfo = showInfo;

document.addEventListener('DOMContentLoaded', function() {
  console.log('Main script DOMContentLoaded event fired');
  
  // Get solicitudId from a global JS variable or data attribute
  let solicitudId = window.solicitudId;
  if (!solicitudId) {
    // Try to get from a data attribute on the body
    solicitudId = document.body.getAttribute('data-solicitud-id');
  }
  if (!solicitudId) {
    showError('No se pudo determinar el ID de la solicitud.');
    return;
  }

  console.log('Main script: Initializing with solicitudId:', solicitudId);

  // Initialize the page
  initializePage();
  
  // Fetch solicitud data
  fetchSolicitudData(solicitudId);

  // Event listeners
  setupEventListeners(solicitudId);
});

function initializePage() {
  // Show loading states for all sections
  showLoadingStates();
  
  // Initialize tooltips
  if (typeof bootstrap !== 'undefined') {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
}

function showLoadingStates() {
  // Show spinners in all content areas
  const contentAreas = [
    'datosPersonalesContent',
    'infoFinancieraContent', 
    'referenciasContent',
    'documentosContent',
    'solicitudHistorial',
    'solicitudComentarios'
  ];
  
  contentAreas.forEach(areaId => {
    const element = document.getElementById(areaId);
    if (element) {
      element.innerHTML = `
        <div class="text-center py-4">
          <div class="spinner-custom mx-auto mb-3"></div>
          <p class="text-muted">Cargando...</p>
        </div>
      `;
    }
  });
}

function fetchSolicitudData(solicitudId) {
  // Show loading overlay
  showLoadingOverlay();
  
  fetch(`/workflow/api/solicitud_brief/${solicitudId}/`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Fill header and cards
      fillHeaderData(data);
      fillInfoCards(data);
      
      // Fill tabs
      fillDatosPersonales(data.datos_personales);
      fillInfoFinanciera(data.info_financiera);
      fillReferencias(data.referencias);
      fillDocumentos(data.documentos);
      
      // Timeline and comments
      renderTimeline(data.historial);
      
      // Load comments separately using the dedicated API
      loadComments(solicitudId);
      
      // Hide loading overlay
      hideLoadingOverlay();
      
      // Add fade-in animation
      document.querySelector('.fade-in-up').classList.add('fade-in-up');
    })
    .catch(error => {
      console.error('Error fetching solicitud data:', error);
      showError('Error al cargar los datos de la solicitud: ' + error.message);
      hideLoadingOverlay();
    });
}

function loadComments(solicitudId) {
  fetch(`/workflow/api/solicitudes/${solicitudId}/comentarios/`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        renderComments(data.comentarios);
      } else {
        throw new Error(data.error || 'Error al cargar comentarios');
      }
    })
    .catch(error => {
      console.error('Error loading comments:', error);
      renderComments([]);
    });
}

function fillHeaderData(data) {
  // Fill header information
  const codigoElement = document.getElementById('solicitudCodigo');
  const clienteElement = document.getElementById('solicitudCliente');
  
  if (codigoElement) {
    codigoElement.textContent = data.general?.codigo || 'N/A';
  }
  
  if (clienteElement) {
    const nombre = data.cliente?.nombre || 'N/A';
    const cedula = data.cliente?.cedula || 'N/A';
    clienteElement.textContent = `${nombre} - CI: ${cedula}`;
  }
}

function fillInfoCards(data) {
  // Fill main info cards
  const elements = {
    'solicitudEtapa': data.general?.etapa_actual || 'N/A',
    'solicitudMonto': data.cotizacion?.monto ? `$${Number(data.cotizacion.monto).toLocaleString()}` : 'N/A',
    'solicitudProducto': data.general?.producto || 'N/A',
    'solicitudPropietario': data.general?.propietario || 'N/A',
    'solicitudAsignado': data.general?.asignado_a || 'N/A',
    'solicitudFechaInicio': data.general?.fecha_inicio || 'N/A',
    'solicitudSLA': data.general?.sla_restante || 'N/A'
  };
  
  Object.entries(elements).forEach(([id, value]) => {
    const element = document.getElementById(id);
    if (element) {
      element.textContent = value;
    }
  });
  
  // Fill progress bar
  const progreso = data.general?.progreso || 0;
  const progresoBar = document.getElementById('solicitudProgreso');
  const progresoText = document.getElementById('solicitudProgresoText');
  
  if (progresoBar) {
    progresoBar.style.width = `${progreso}%`;
    // Add color based on progress
    if (progreso >= 80) {
      progresoBar.classList.add('bg-success');
    } else if (progreso >= 50) {
      progresoBar.classList.add('bg-warning');
    } else {
      progresoBar.classList.add('bg-danger');
    }
  }
  
  if (progresoText) {
    progresoText.textContent = `${progreso}%`;
  }
}

function fillDatosPersonales(datos) {
  const container = document.getElementById('datosPersonalesContent');
  if (!container) return;
  
  if (!datos || Object.keys(datos).length === 0) {
    container.innerHTML = `
      <div class="text-center py-4">
        <i class="fas fa-user-slash fa-3x text-muted mb-3"></i>
        <p class="text-muted mb-0">No hay datos personales disponibles</p>
      </div>
    `;
    return;
  }
  
  const html = Object.entries(datos).map(([key, value]) => `
    <div class="data-row">
      <span class="data-label">${formatLabel(key)}</span>
      <span class="data-value">${value || 'N/A'}</span>
    </div>
  `).join('');
  
  container.innerHTML = html;
}

function fillInfoFinanciera(datos) {
  const container = document.getElementById('infoFinancieraContent');
  if (!container) return;
  
  if (!datos || Object.keys(datos).length === 0) {
    container.innerHTML = `
      <div class="text-center py-4">
        <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
        <p class="text-muted mb-0">No hay información financiera disponible</p>
      </div>
    `;
    return;
  }
  
  const html = Object.entries(datos).map(([key, value]) => `
    <div class="data-row">
      <span class="data-label">${formatLabel(key)}</span>
      <span class="data-value">${formatFinancialValue(key, value)}</span>
    </div>
  `).join('');
  
  container.innerHTML = html;
}

function fillReferencias(datos) {
  const container = document.getElementById('referenciasContent');
  if (!container) return;
  
  if (!datos || datos.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4">
        <i class="fas fa-address-book fa-3x text-muted mb-3"></i>
        <p class="text-muted mb-0">No hay referencias disponibles</p>
      </div>
    `;
    return;
  }
  
  const html = datos.map(ref => `
    <div class="reference-card">
      <div class="reference-name">
        <i class="fas fa-user me-2"></i>
        ${ref.nombre || ref.tipo || 'Sin nombre'}
      </div>
      <div class="reference-details">
        ${ref.telefono ? `<div><i class="fas fa-phone me-1"></i>${ref.telefono}</div>` : ''}
        ${ref.relacion ? `<div><i class="fas fa-link me-1"></i>${ref.relacion}</div>` : ''}
        ${ref.email ? `<div><i class="fas fa-envelope me-1"></i>${ref.email}</div>` : ''}
      </div>
    </div>
  `).join('');
  
  container.innerHTML = html;
}

function fillDocumentos(datos) {
  const container = document.getElementById('documentosContent');
  if (!container) return;
  
  if (!datos || datos.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4">
        <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
        <p class="text-muted mb-0">No hay documentos disponibles</p>
      </div>
    `;
    return;
  }
  
  const html = datos.map(doc => `
    <div class="document-item">
      <div class="document-info">
        <div class="document-name">
          <i class="fas fa-file me-2"></i>
          ${doc.nombre}
        </div>
        <div class="document-meta">
          ${doc.tipo || ''} ${doc.fecha ? `• ${doc.fecha}` : ''}
        </div>
      </div>
      <div class="document-actions">
        <a href="${doc.url}" target="_blank" class="btn btn-outline-pacifico btn-sm" 
           data-bs-toggle="tooltip" title="Ver documento">
          <i class="fas fa-eye"></i>
        </a>
        <a href="${doc.url}" download class="btn btn-outline-secondary btn-sm"
           data-bs-toggle="tooltip" title="Descargar">
          <i class="fas fa-download"></i>
        </a>
      </div>
    </div>
  `).join('');
  
  container.innerHTML = html;
}

function renderTimeline(historial) {
  const container = document.getElementById('solicitudHistorial');
  if (!container) return;
  
  if (!historial || historial.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4">
        <i class="fas fa-history fa-3x text-muted mb-3"></i>
        <p class="text-muted mb-0">No hay historial disponible</p>
      </div>
    `;
    return;
  }
  
  const html = historial.map(item => `
    <div class="timeline-item">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div>
          <span class="badge-pacifico me-2">${item.etapa || 'Actividad'}</span>
          <strong>${item.subestado || 'Sin título'}</strong>
        </div>
        <small class="text-muted">${formatDate(item.fecha_inicio)}</small>
      </div>
      <div class="mb-2">
        <small class="text-muted">
          <i class="fas fa-user me-1"></i>${item.usuario || 'Usuario'}
        </small>
      </div>
      <div class="text-muted">
        ${item.fecha_fin ? `Completado: ${formatDate(item.fecha_fin)}` : 'En progreso'}
      </div>
    </div>
  `).join('');
  
  container.innerHTML = html;
}

function renderComments(comentarios) {
  const container = document.getElementById('solicitudComentarios');
  if (!container) return;
  
  if (!comentarios || comentarios.length === 0) {
    container.innerHTML = `
      <div class="text-center py-4">
        <i class="fas fa-comments fa-3x text-muted mb-3"></i>
        <p class="text-muted mb-0">No hay comentarios</p>
      </div>
    `;
    return;
  }
  
  const html = comentarios.map(c => `
    <div class="comment-item" data-comentario-id="${c.id}">
      <div class="comment-header">
        <div class="d-flex align-items-center">
          <div class="comment-avatar me-2">
            <i class="fas fa-user-circle fa-lg text-muted"></i>
          </div>
          <div>
            <span class="comment-author">${c.usuario.nombre_completo}</span>
            <div class="comment-meta">
              <span class="comment-date">${formatDate(c.fecha_creacion)}</span>
              ${c.es_editado ? '<span class="badge bg-secondary ms-2">Editado</span>' : ''}
            </div>
          </div>
        </div>
        <div class="comment-actions">
          ${c.puede_editar ? `
            <button class="btn btn-sm btn-outline-secondary me-1" onclick="editComment(${c.id})" title="Editar">
              <i class="fas fa-edit"></i>
            </button>
          ` : ''}
          ${c.puede_eliminar ? `
            <button class="btn btn-sm btn-outline-danger" onclick="deleteComment(${c.id})" title="Eliminar">
              <i class="fas fa-trash"></i>
            </button>
          ` : ''}
        </div>
      </div>
      <div class="comment-content" id="comment-content-${c.id}">${escapeHtml(c.comentario)}</div>
      <div class="comment-edit-form d-none" id="comment-edit-form-${c.id}">
        <textarea class="form-control form-control-custom mb-2" id="edit-comment-${c.id}" rows="3">${escapeHtml(c.comentario)}</textarea>
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-sm btn-outline-secondary" onclick="cancelEditComment(${c.id})">Cancelar</button>
          <button class="btn btn-sm btn-pacifico" onclick="saveEditComment(${c.id})">Guardar</button>
        </div>
      </div>
    </div>
  `).join('');
  
  container.innerHTML = html;
}

function setupEventListeners(solicitudId) {
  // Comment form submission
  const comentarioForm = document.getElementById('comentarioForm');
  if (comentarioForm) {
    comentarioForm.addEventListener('submit', function(e) {
      e.preventDefault();
      submitComment(solicitudId);
    });
  }
  
  // Action buttons
  const actionButtons = {
    'btnAsignar': () => handleAction('asignar', solicitudId),
    'btnDevolver': () => handleAction('devolver', solicitudId),
    'btnAnular': () => handleAction('anular', solicitudId),
    'btnCambiarEstado': () => handleAction('cambiar_estado', solicitudId)
  };
  
  Object.entries(actionButtons).forEach(([id, handler]) => {
    const button = document.getElementById(id);
    if (button) {
      button.addEventListener('click', handler);
    }
  });
}

function submitComment(solicitudId) {
  console.log('=== SUBMIT COMMENT FUNCTION CALLED ===');
  console.log('submitComment called with solicitudId:', solicitudId);
  console.log('Function source: detalleSolicitud_V2.js');
  
  const comentarioInput = document.getElementById('comentarioInput');
  const comentario = comentarioInput.value.trim();
  
  if (!comentario) {
    showWarning('Por favor escribe un comentario antes de enviar.');
    return;
  }
  
  // Show loading state
  const submitButton = document.querySelector('#comentarioForm button[type="submit"]');
  const originalText = submitButton.innerHTML;
  submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
  submitButton.disabled = true;
  
  const apiUrl = `/workflow/api/solicitudes/${solicitudId}/comentarios/crear/`;
  console.log('Submitting comment to:', apiUrl);
  console.log('Comment text:', comentario);
  console.log('=== END SUBMIT COMMENT FUNCTION ===');
  
  fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ comentario })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
          .then(data => {
          if (data.success) {
            comentarioInput.value = '';
            showSuccess('¡Comentario enviado exitosamente!');
            
            // Reload comments
            loadComments(solicitudId);
          } else {
            throw new Error(data.error || 'Error al enviar comentario');
          }
        })
        .catch(error => {
          console.error('Error submitting comment:', error);
          showError('Error al enviar el comentario: ' + error.message);
        })
  .finally(() => {
    // Restore button state
    submitButton.innerHTML = originalText;
    submitButton.disabled = false;
  });
}

function editComment(comentarioId) {
  const contentDiv = document.getElementById(`comment-content-${comentarioId}`);
  const editForm = document.getElementById(`comment-edit-form-${comentarioId}`);
  
  if (contentDiv && editForm) {
    contentDiv.classList.add('d-none');
    editForm.classList.remove('d-none');
  }
}

function cancelEditComment(comentarioId) {
  const contentDiv = document.getElementById(`comment-content-${comentarioId}`);
  const editForm = document.getElementById(`comment-edit-form-${comentarioId}`);
  
  if (contentDiv && editForm) {
    contentDiv.classList.remove('d-none');
    editForm.classList.add('d-none');
  }
}

function saveEditComment(comentarioId) {
  const textarea = document.getElementById(`edit-comment-${comentarioId}`);
  const nuevoComentario = textarea.value.trim();
  
  if (!nuevoComentario) {
    showWarning('El comentario no puede estar vacío.');
    return;
  }
  
  fetch(`/workflow/api/comentarios/${comentarioId}/editar/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ comentario: nuevoComentario })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    if (data.success) {
      showSuccess('Comentario actualizado exitosamente.');
      
      // Reload comments to show updated data
      const solicitudId = document.body.getAttribute('data-solicitud-id');
      loadComments(solicitudId);
    } else {
      throw new Error(data.error || 'Error al actualizar comentario');
    }
  })
  .catch(error => {
    console.error('Error updating comment:', error);
    showError('Error al actualizar el comentario: ' + error.message);
  });
}

function deleteComment(comentarioId) {
  if (!confirm('¿Estás seguro de que quieres eliminar este comentario?')) {
    return;
  }
  
  fetch(`/workflow/api/comentarios/${comentarioId}/eliminar/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    if (data.success) {
      showSuccess('Comentario eliminado exitosamente.');
      
      // Reload comments
      const solicitudId = document.body.getAttribute('data-solicitud-id');
      loadComments(solicitudId);
    } else {
      throw new Error(data.error || 'Error al eliminar comentario');
    }
  })
  .catch(error => {
    console.error('Error deleting comment:', error);
    showError('Error al eliminar el comentario: ' + error.message);
  });
}

function handleAction(action, solicitudId) {
  // This would handle different actions like assign, return, cancel, change status
  console.log(`Handling action: ${action} for solicitud: ${solicitudId}`);
  
  // For now, just show a placeholder message
  showInfo(`Acción "${action}" no implementada aún.`);
}

// Utility functions
function formatLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatFinancialValue(key, value) {
  if (key.toLowerCase().includes('monto') || key.toLowerCase().includes('precio') || key.toLowerCase().includes('valor')) {
    return value ? `$${Number(value).toLocaleString()}` : 'N/A';
  }
  return value || 'N/A';
}

function formatDate(dateString) {
  if (!dateString) return 'N/A';
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    return dateString;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function showLoadingOverlay() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) {
    overlay.classList.add('show');
  }
}

function hideLoadingOverlay() {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) {
    overlay.classList.remove('show');
  }
}

function showSuccess(message) {
  if (typeof window.showToast === 'function') {
    window.showToast(message, 'success');
  } else {
    showNotification(message, 'success');
  }
}

function showError(message) {
  if (typeof window.showToast === 'function') {
    window.showToast(message, 'error');
  } else {
    showNotification(message, 'danger');
  }
}

function showWarning(message) {
  if (typeof window.showToast === 'function') {
    window.showToast(message, 'warning');
  } else {
    showNotification(message, 'warning');
  }
}

function showInfo(message) {
  if (typeof window.showToast === 'function') {
    window.showToast(message, 'info');
  } else {
    showNotification(message, 'info');
  }
}

function showNotification(message, type) {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `alert alert-${type}-custom alert-custom fade show position-fixed`;
  notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
  notification.innerHTML = `
    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'times-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  // Add to page
  document.body.appendChild(notification);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 5000);
}

// CSRF helper
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