// Variables globales
let currentRequisitoId = null;
let currentRequisitoForOpciones = null;

// Función para calificar documento
function calificarDocumento(requisitoId, estado, opcionId = null) {
  const csrfToken = getCsrfToken();
  const data = {
    requisito_id: requisitoId,
    estado: estado,
    opcion_id: opcionId
  };

  fetch('/workflow/api/documento/calificar/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        actualizarEstadoCalificacion(requisitoId, estado, data);
        mostrarMensaje('Documento calificado correctamente', 'success');
      } else {
        mostrarMensaje('Error al calificar documento: ' + data.error, 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      mostrarMensaje('Error de conexión al calificar documento', 'error');
    });
}

// Función para agregar comentario
function agregarComentario(requisitoId, comentario) {
  const csrfToken = getCsrfToken();
  const data = {
    requisito_id: requisitoId,
    comentario: comentario
  };

  fetch('/workflow/api/documento/comentar/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        actualizarModalComentarios(requisitoId);
        document.getElementById('form-nuevo-comentario').reset();
        mostrarMensaje('Comentario agregado correctamente', 'success');
      } else {
        mostrarMensaje('Error al agregar comentario: ' + data.error, 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      mostrarMensaje('Error de conexión al agregar comentario', 'error');
    });
}

// Función para obtener comentarios
function obtenerComentarios(requisitoId) {
  fetch(`/workflow/api/documento/${requisitoId}/comentarios/`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        mostrarComentariosEnModal(data.comentarios);
      } else {
        mostrarMensaje('Error al cargar comentarios: ' + data.error, 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      mostrarMensaje('Error de conexión al cargar comentarios', 'error');
    });
}

// Función para actualizar estado de calificación en la interfaz
function actualizarEstadoCalificacion(requisitoId, estado, data) {
  const botones = document.querySelectorAll(`[data-requisito="${requisitoId}"]`);
  botones.forEach(boton => {
    boton.classList.remove('btn-success', 'btn-danger', 'btn-warning');
    if (estado === 'bueno') {
      boton.classList.add('btn-success');
    } else if (estado === 'malo') {
      boton.classList.add('btn-danger');
    } else {
      boton.classList.add('btn-warning');
    }
  });
}

// Función para actualizar modal de comentarios
function actualizarModalComentarios(requisitoId) {
  obtenerComentarios(requisitoId);
}

// Función para mostrar modal de comentarios
function mostrarModalComentarios(requisitoId) {
  currentRequisitoId = requisitoId;
  obtenerComentarios(requisitoId);
  const modal = new bootstrap.Modal(document.getElementById('modalComentarios'));
  modal.show();
}

// Función para cargar estados iniciales de calificaciones
function cargarEstadosInicialesCalificaciones() {
  // Obtener el código de solicitud del atributo data
  const solicitudCodigo = document.querySelector('.container-fluid.mt-4').dataset.solicitudCodigo;

  fetch(`/workflow/api/documento/${solicitudCodigo}/calificaciones/`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        data.calificaciones.forEach(cal => {
          actualizarEstadoCalificacion(cal.requisito_id, cal.estado, cal);
        });
      }
    })
    .catch(error => {
      console.error('Error al cargar calificaciones iniciales:', error);
    });
}

// Función para mostrar modal de opciones
function mostrarModalOpciones(requisitoId, documentoNombre) {
  currentRequisitoForOpciones = requisitoId;
  document.getElementById('opciones-documento-nombre').textContent = documentoNombre;
  cargarOpcionesDisponibles();
  const modal = new bootstrap.Modal(document.getElementById('modalOpciones'));
  modal.show();
}

// Función para cargar las opciones disponibles
function cargarOpcionesDisponibles() {
  fetch('/workflow/api/opciones-calificacion/')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        mostrarOpcionesEnModal(data.opciones);
      } else {
        mostrarMensaje('Error al cargar opciones: ' + data.error, 'error');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      mostrarMensaje('Error de conexión al cargar opciones', 'error');
    });
}

// Función para seleccionar una opción
function seleccionarOpcion(opcionId, opcionNombre) {
  calificarDocumento(currentRequisitoForOpciones, 'malo', opcionId);
  const modal = bootstrap.Modal.getInstance(document.getElementById('modalOpciones'));
  modal.hide();
}

// Función para obtener CSRF token
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Función para mostrar mensajes (toast notifications)
function mostrarMensaje(mensaje, tipo) {
  const toastContainer = document.getElementById('toast-container') || createToastContainer();

  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white bg-${tipo === 'success' ? 'success' : tipo === 'error' ? 'danger' : 'info'} border-0`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.setAttribute('aria-atomic', 'true');

  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        ${mensaje}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  toastContainer.appendChild(toast);
  const bsToast = new bootstrap.Toast(toast);
  bsToast.show();

  toast.addEventListener('hidden.bs.toast', function () {
    this.remove();
  });
}

// Funciones adicionales para el backoffice
function refreshFiles(subestadoId) {
  // Implementar lógica de refresh
  console.log('Refreshing files for subestado:', subestadoId);
}

function generateReport(subestadoId) {
  // Implementar generación de reporte
  console.log('Generating report for subestado:', subestadoId);
}

function showToast(message, type = 'info') {
  mostrarMensaje(message, type);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container position-fixed top-0 end-0 p-3';
  container.style.zIndex = '1055';
  document.body.appendChild(container);
  return container;
}

// Hacer funciones disponibles globalmente
window.calificarDocumento = calificarDocumento;
window.agregarComentario = agregarComentario;
window.obtenerComentarios = obtenerComentarios;
window.actualizarEstadoCalificacion = actualizarEstadoCalificacion;
window.actualizarModalComentarios = actualizarModalComentarios;
window.mostrarModalComentarios = mostrarModalComentarios;
window.cargarEstadosInicialesCalificaciones = cargarEstadosInicialesCalificaciones;
window.mostrarModalOpciones = mostrarModalOpciones;
window.cargarOpcionesDisponibles = cargarOpcionesDisponibles;
window.seleccionarOpcion = seleccionarOpcion;
window.mostrarMensaje = mostrarMensaje;
window.refreshFiles = refreshFiles;
window.generateReport = generateReport;
window.showToast = showToast;
window.createToastContainer = createToastContainer;
window.mostrarModalAvanzarEtapa = mostrarModalAvanzarEtapa;
window.cargarUsuariosDisponibles = cargarUsuariosDisponibles;
window.manejarCambioOpcionAvance = manejarCambioOpcionAvance;
window.procesarAvanceEtapa = procesarAvanceEtapa;

// Función para mostrar el modal de avanzar etapa
function mostrarModalAvanzarEtapa() {
  // Cargar usuarios disponibles
  cargarUsuariosDisponibles();

  // Mostrar el modal
  const modal = new bootstrap.Modal(document.getElementById('modalAvanzarEtapa'));
  modal.show();
}

// Función para cargar usuarios disponibles
function cargarUsuariosDisponibles() {
  fetch('/workflow/api/usuarios/disponibles/', {
    method: 'GET',
    headers: {
      'X-CSRFToken': getCsrfToken(),
      'Content-Type': 'application/json',
    },
  })
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('usuarioDestino');
      select.innerHTML = '<option value="">-- Selecciona un usuario --</option>';

      if (data.usuarios) {
        data.usuarios.forEach(usuario => {
          const option = document.createElement('option');
          option.value = usuario.id;
          option.textContent = usuario.nombre_completo || usuario.username;
          select.appendChild(option);
        });
      }
    })
    .catch(error => {
      console.error('Error cargando usuarios:', error);
      mostrarMensaje('Error cargando usuarios disponibles', 'error');
    });
}

// Función para manejar cambios en las opciones de radio
function manejarCambioOpcionAvance() {
  const opcionUsuarioEspecifico = document.getElementById('opcionUsuarioEspecifico');
  const selectorUsuario = document.getElementById('selectorUsuario');

  if (opcionUsuarioEspecifico.checked) {
    selectorUsuario.style.display = 'block';
  } else {
    selectorUsuario.style.display = 'none';
  }
}

// Función para procesar el avance de etapa
function procesarAvanceEtapa() {
  const form = document.getElementById('formAvanzarEtapa');
  const formData = new FormData(form);

  // Obtener la opción seleccionada
  const opcionSeleccionada = form.querySelector('input[name="opcionAvance"]:checked').value;
  const comentario = document.getElementById('comentarioAvance').value;
  const usuarioDestino = document.getElementById('usuarioDestino').value;

  // Validaciones
  if (opcionSeleccionada === 'usuario_especifico' && !usuarioDestino) {
    mostrarMensaje('Debes seleccionar un usuario específico', 'error');
    return;
  }

  // Preparar datos para enviar
  const datos = {
    solicitud_codigo: solicitudCodigo,
    opcion_avance: opcionSeleccionada,
    comentario: comentario,
    usuario_destino: usuarioDestino
  };

  // Enviar solicitud al servidor
  fetch('/workflow/api/solicitud/avanzar-etapa/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCsrfToken(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(datos)
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        mostrarMensaje(data.mensaje || 'Etapa avanzada exitosamente', 'success');

        // Cerrar el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalAvanzarEtapa'));
        if (modal) {
          modal.hide();
        }

        // Redirigir o recargar la página según la respuesta
        if (data.redirect_url) {
          setTimeout(() => {
            window.location.href = data.redirect_url;
          }, 1500);
        } else {
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        }
      } else {
        mostrarMensaje(data.mensaje || 'Error al avanzar la etapa', 'error');
      }
    })
    .catch(error => {
      console.error('Error procesando avance de etapa:', error);
      mostrarMensaje('Error de conexión al procesar el avance', 'error');
    });
}

// Agregar event listeners cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
  // Event listeners para las opciones de radio del modal de avanzar etapa
  const opcionesRadio = document.querySelectorAll('input[name="opcionAvance"]');
  opcionesRadio.forEach(radio => {
    radio.addEventListener('change', manejarCambioOpcionAvance);
  });
});

// Event listeners cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
  // Cargar estados iniciales de calificaciones
  cargarEstadosInicialesCalificaciones();

  // Botones de calificación
  document.addEventListener('click', function (e) {
    if (e.target.closest('.calificar-btn-backoffice')) {
      const boton = e.target.closest('.calificar-btn-backoffice');
      const requisitoId = boton.getAttribute('data-requisito');
      const estado = boton.getAttribute('data-estado');
      calificarDocumento(requisitoId, estado);
    }

    if (e.target.closest('.comentario-btn-backoffice')) {
      const boton = e.target.closest('.comentario-btn-backoffice');
      const requisitoId = boton.getAttribute('data-requisito');
      const documentoNombre = boton.getAttribute('data-documento');
      mostrarModalComentarios(requisitoId);
    }
  });

  // Formulario de nuevo comentario
  const formComentario = document.getElementById('form-nuevo-comentario');
  if (formComentario) {
    formComentario.addEventListener('submit', function (e) {
      e.preventDefault();
      const comentario = this.querySelector('[name=comentario]').value;
      if (comentario.trim()) {
        agregarComentario(currentRequisitoId, comentario);
      }
    });
  }
}); 