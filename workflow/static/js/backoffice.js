// Variables globales
let currentRequisitoId = null;
let currentRequisitoForOpciones = null;

// Función para validar y abrir modal (ejecutada al hacer clic)
function validarYAbrirModal() {
  console.log('🔘 validarYAbrirModal ejecutada');

  try {
    console.log('🔍 Validando documentos antes de abrir modal...');

    // Obtener todos los documentos obligatorios
    const documentosObligatorios = [];
    const documentosOpcionales = [];

    document.querySelectorAll('.archivo-card-mejorada-backoffice').forEach(card => {
      const obligatorio = card.querySelector('.text-danger') !== null; // Buscar etiqueta "Obligatorio"
      const requisitoId = card.getAttribute('data-requisito-id');
      const nombreDocumento = card.querySelector('.archivo-nombre-backoffice')?.textContent?.trim() || 'Documento';

      // Skip si no hay requisito ID válido
      if (!requisitoId || requisitoId === '0') {
        return;
      }

      const documentoInfo = {
        requisitoId,
        nombre: nombreDocumento,
        obligatorio,
        calificado: false,
        estadoCalificacion: null
      };

      // Verificar el estado de calificación actual
      const botonBueno = card.querySelector('.calificar-btn-backoffice[data-estado="bueno"]');
      const botonMalo = card.querySelector('.calificar-btn-backoffice[data-estado="malo"]');
      const botonPendiente = card.querySelector('.calificar-btn-backoffice[data-estado="pendiente"]');

      if (botonBueno && botonBueno.classList.contains('activo')) {
        documentoInfo.calificado = true;
        documentoInfo.estadoCalificacion = 'bueno';
      } else if (botonMalo && botonMalo.classList.contains('activo')) {
        documentoInfo.calificado = true;
        documentoInfo.estadoCalificacion = 'malo';
      } else if (botonPendiente && botonPendiente.classList.contains('activo')) {
        documentoInfo.calificado = true;
        documentoInfo.estadoCalificacion = 'pendiente';
      }

      if (obligatorio) {
        documentosObligatorios.push(documentoInfo);
      } else {
        documentosOpcionales.push(documentoInfo);
      }
    });

    console.log('📋 Documentos obligatorios:', documentosObligatorios);

    // Verificar si todos los obligatorios están calificados como "buenos"
    const obligatoriosNoBuenos = documentosObligatorios.filter(doc =>
      !doc.calificado || doc.estadoCalificacion !== 'bueno'
    );
    const todosObligatoriosCalificados = obligatoriosNoBuenos.length === 0;

    console.log(`🔍 Total obligatorios: ${documentosObligatorios.length}`);
    console.log(`🔍 Obligatorios no "buenos": ${obligatoriosNoBuenos.length}`);
    console.log(`🔍 Todos calificados como "buenos": ${todosObligatoriosCalificados}`);

    if (todosObligatoriosCalificados) {
      // ✅ Todos los obligatorios están calificados - Abrir modal
      console.log('✅ Validación exitosa - Abriendo modal');
      const modal = new bootstrap.Modal(document.getElementById('modalAvanzarSubestado'));
      modal.show();
    } else {
      // ❌ Hay documentos obligatorios que no están calificados como "buenos"
      console.log('❌ Validación fallida - Documentos obligatorios no están todos como "buenos"');

      const documentosProblematicos = obligatoriosNoBuenos.map(doc => {
        if (!doc.calificado) {
          return `${doc.nombre} (sin calificar)`;
        } else {
          return `${doc.nombre} (calificado como "${doc.estadoCalificacion}")`;
        }
      }).join(', ');

      mostrarMensaje(
        `Todos los documentos obligatorios deben estar calificados como "Buenos" para poder avanzar. Documentos problemáticos: ${documentosProblematicos}`,
        'error'
      );

      // Resaltar los documentos problemáticos
      obligatoriosNoBuenos.forEach(doc => {
        const card = document.querySelector(`[data-requisito-id="${doc.requisitoId}"]`);
        if (card) {
          card.style.border = '2px solid #dc3545';
          card.style.backgroundColor = '#fff5f5';

          // Quitar el resaltado después de 5 segundos
          setTimeout(() => {
            card.style.border = '';
            card.style.backgroundColor = '';
          }, 5000);
        }
      });
    }

  } catch (error) {
    console.error('❌ Error en validarYAbrirModal:', error);
    mostrarMensaje('Error al validar documentos. Recarga la página e intenta de nuevo.', 'error');
  }
}

// Función para calificar documento
function calificarDocumento(requisitoId, estado, opcionId = null) {
  const csrfToken = getCsrfToken();
  const data = {
    requisito_solicitud_id: requisitoId,
    estado: estado,
    opcion_desplegable_id: opcionId
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
    boton.classList.remove('btn-success', 'btn-danger', 'btn-warning', 'activo');
    if (estado === 'bueno') {
      boton.classList.add('btn-success');
      if (boton.dataset.estado === 'bueno') {
        boton.classList.add('activo');
      }
    } else if (estado === 'malo') {
      boton.classList.add('btn-danger');
      if (boton.dataset.estado === 'malo') {
        boton.classList.add('activo');
      }
    } else if (estado === 'pendiente') {
      boton.classList.add('btn-warning');
      if (boton.dataset.estado === 'pendiente') {
        boton.classList.add('activo');
      }
    }
  });

  // Ya no necesitamos validación automática - solo al hacer clic
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

// Función eliminada - se usa la implementación del template que es más específica

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

// Función para seleccionar una opción (califica automáticamente como malo)
function seleccionarOpcion(opcionId, opcionNombre) {
  // Calificar automáticamente como malo con la opción seleccionada
  calificarDocumento(currentRequisitoForOpciones, 'malo', opcionId);

  // Cerrar el modal
  const modal = bootstrap.Modal.getInstance(document.getElementById('modalOpciones'));
  modal.hide();

  // Mostrar feedback optimizado
  mostrarMensaje(`Documento calificado como "Malo": ${opcionNombre}`, 'warning');
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
// cargarEstadosInicialesCalificaciones eliminada - se usa la del template
window.mostrarModalOpciones = mostrarModalOpciones;
window.cargarOpcionesDisponibles = cargarOpcionesDisponibles;
window.seleccionarOpcion = seleccionarOpcion;
window.mostrarMensaje = mostrarMensaje;
window.refreshFiles = refreshFiles;
window.generateReport = generateReport;
window.showToast = showToast;
window.createToastContainer = createToastContainer;

// Variables globales para el nuevo flujo de avance
let opcionAvanceSeleccionada = null;
let usuarioSeleccionadoAvance = null;
let siguienteSubestado = null;

// Event listeners cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
  // La carga de estados iniciales se maneja en el template

  // Inicializar validación en tiempo real
  inicializarValidacionTiempoReal();

  // Event listener para el botón de avanzar
  const btnAvanzar = document.getElementById('btn-avanzar-subestado');
  if (btnAvanzar) {
    btnAvanzar.addEventListener('click', function () {
      console.log('🔘 Botón Avanzar clickeado');

      // Verificar que la función existe antes de llamarla
      if (typeof validarYAbrirModal === 'function') {
        validarYAbrirModal();
      } else {
        console.error('❌ Función validarYAbrirModal no está definida');
        // Fallback: mostrar mensaje de error
        mostrarMensaje('Error: Función de validación no disponible. Recarga la página.', 'error');
      }
    });
    console.log('✅ Event listener del botón Avanzar configurado');
  } else {
    console.warn('⚠️ Botón Avanzar no encontrado');
  }

  // Botones de calificación
  document.addEventListener('click', function (e) {
    if (e.target.closest('.calificar-btn-backoffice')) {
      const boton = e.target.closest('.calificar-btn-backoffice');
      const requisitoId = boton.getAttribute('data-requisito');
      const estado = boton.getAttribute('data-estado');

      // Solo calificar automáticamente si NO es el botón "malo"
      // El botón "malo" abre el modal y califica solo cuando se selecciona una opción
      if (estado !== 'malo') {
        calificarDocumento(requisitoId, estado);
      }
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

// =======================================================
// FUNCIONES PARA EL NUEVO FLUJO DE AVANCE DE SUBESTADO
// =======================================================

// Función para inicializar la validación (simplificada)
function inicializarValidacionTiempoReal() {
  console.log('🚀 Sistema de validación por clic inicializado');
  // Ya no necesitamos validación continua, solo al hacer clic en "Avanzar"
}

// Función para validar documentos en tiempo real
function validarDocumentosEnTiempoReal() {
  console.log('🔍 Validando documentos...');

  const btnAvanzar = document.getElementById('btn-avanzar-subestado');
  const mensajeValidacion = document.getElementById('validacion-mensaje');

  if (!btnAvanzar) {
    console.warn('⚠️ Botón de avanzar no encontrado');
    return;
  }

  if (!mensajeValidacion) {
    console.warn('⚠️ Mensaje de validación no encontrado');
    return;
  }

  // Obtener todos los documentos obligatorios
  const documentosObligatorios = [];
  const documentosOpcionales = [];

  document.querySelectorAll('.archivo-card-mejorada-backoffice').forEach(card => {
    const obligatorio = card.querySelector('.text-danger') !== null; // Buscar etiqueta "Obligatorio"
    const requisitoId = card.getAttribute('data-requisito-id');
    const nombreDocumento = card.querySelector('.archivo-nombre-backoffice')?.textContent?.trim() || 'Documento';

    // Skip si no hay requisito ID válido
    if (!requisitoId || requisitoId === '0') {
      console.log(`⚠️ Skipping card sin requisito ID válido: ${nombreDocumento}`);
      return;
    }

    const documentoInfo = {
      requisitoId,
      nombre: nombreDocumento,
      obligatorio,
      calificado: false,
      estadoCalificacion: null
    };

    // Verificar si tiene calificación "bueno"
    const botonBueno = card.querySelector('.calificar-btn-backoffice[data-estado="bueno"]');
    if (botonBueno && botonBueno.classList.contains('activo')) {
      documentoInfo.calificado = true;
      documentoInfo.estadoCalificacion = 'bueno';
    }

    // Debug detallado
    console.log(`📋 Documento: ${nombreDocumento}`);
    console.log(`   - RequisitoID: ${requisitoId}`);
    console.log(`   - Obligatorio: ${obligatorio}`);
    console.log(`   - Calificado: ${documentoInfo.calificado}`);
    console.log(`   - Estado: ${documentoInfo.estadoCalificacion}`);
    console.log(`   - Botón bueno encontrado: ${botonBueno ? 'Sí' : 'No'}`);
    console.log(`   - Botón bueno activo: ${botonBueno?.classList.contains('activo') ? 'Sí' : 'No'}`);

    if (obligatorio) {
      documentosObligatorios.push(documentoInfo);
    } else {
      documentosOpcionales.push(documentoInfo);
    }
  });

  console.log('📋 Documentos obligatorios:', documentosObligatorios);
  console.log('📋 Documentos opcionales:', documentosOpcionales);

  // Verificar si todos los obligatorios están calificados como "buenos"
  const obligatoriosPendientes = documentosObligatorios.filter(doc => !doc.calificado);
  const todosObligatoriosCalificados = obligatoriosPendientes.length === 0;

  console.log(`🔍 Total obligatorios: ${documentosObligatorios.length}`);
  console.log(`🔍 Obligatorios pendientes: ${obligatoriosPendientes.length}`);
  console.log(`🔍 Todos calificados: ${todosObligatoriosCalificados}`);

  if (obligatoriosPendientes.length > 0) {
    console.log('❌ Documentos obligatorios pendientes:');
    obligatoriosPendientes.forEach(doc => {
      console.log(`   - ${doc.nombre} (ID: ${doc.requisitoId})`);
    });
  }

  // Actualizar estado del botón
  if (todosObligatoriosCalificados) {
    const wasDisabled = btnAvanzar.disabled;
    btnAvanzar.disabled = false;
    btnAvanzar.title = 'Todos los documentos obligatorios están calificados correctamente';
    mensajeValidacion.innerHTML = `
      <i class="fas fa-check-circle text-success me-1"></i>
      Listo para avanzar (${documentosObligatorios.length} obligatorios completados)
    `;

    // Agregar animación de pulse si se acaba de habilitar
    if (wasDisabled) {
      btnAvanzar.classList.add('pulse');
      setTimeout(() => {
        btnAvanzar.classList.remove('pulse');
      }, 4000);
    }

    console.log('✅ Botón habilitado - Todos los obligatorios calificados');
  } else {
    btnAvanzar.disabled = true;
    btnAvanzar.classList.remove('pulse');
    btnAvanzar.title = `Faltan ${obligatoriosPendientes.length} documentos obligatorios por calificar como 'Buenos'`;
    mensajeValidacion.innerHTML = `
      <i class="fas fa-exclamation-triangle text-warning me-1"></i>
      Faltan ${obligatoriosPendientes.length} documentos obligatorios por calificar
    `;
    console.log(`⚠️ Botón deshabilitado - Faltan ${obligatoriosPendientes.length} obligatorios`);
  }
}

// Función para cargar información del modal cuando se abre
function cargarInformacionAvance() {
  console.log('📂 Cargando información de avance...');

  const loading = document.getElementById('avance-loading');
  const error = document.getElementById('avance-error');

  // Mostrar loading
  loading.style.display = 'block';
  error.style.display = 'none';

  // Obtener siguiente subestado y usuarios disponibles
  const solicitudId = window.location.pathname.match(/solicitudes\/(\d+)\//)?.[1];

  if (!solicitudId) {
    mostrarErrorAvance('No se pudo obtener el ID de la solicitud');
    return;
  }

  fetch(`/workflow/api/solicitudes/${solicitudId}/siguiente-subestado/`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        siguienteSubestado = data.siguiente_subestado;
        document.getElementById('avanzar-siguiente-subestado').textContent =
          siguienteSubestado ? siguienteSubestado.nombre : 'Finalizar Back Office';

        // Cargar usuarios disponibles
        return cargarUsuariosDisponiblesAvance();
      } else {
        throw new Error(data.error || 'Error al obtener siguiente subestado');
      }
    })
    .then(() => {
      loading.style.display = 'none';
    })
    .catch(error => {
      console.error('Error:', error);
      mostrarErrorAvance(error.message);
      loading.style.display = 'none';
    });
}

// Función para cargar usuarios disponibles
function cargarUsuariosDisponiblesAvance() {
  return fetch('/workflow/api/usuarios/')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        mostrarUsuariosEnTabla(data.usuarios);
        return Promise.resolve();
      } else {
        throw new Error(data.error || 'Error al cargar usuarios');
      }
    });
}

// Función para mostrar usuarios en la tabla
function mostrarUsuariosEnTabla(usuarios) {
  const tbody = document.getElementById('lista-usuarios-avance');
  const contador = document.getElementById('contador-usuarios-avance');

  tbody.innerHTML = '';

  usuarios.forEach((usuario, index) => {
    const row = document.createElement('tr');
    row.className = 'usuario-item';
    row.setAttribute('data-usuario-id', usuario.id);
    row.setAttribute('data-usuario-nombre', usuario.nombre);
    row.setAttribute('data-usuario-email', usuario.email);

    const avatar = usuario.profile_picture ?
      `<img src="${usuario.profile_picture}" alt="${usuario.nombre}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #e0e0e0;">` :
      `<div style="width: 40px; height: 40px; background: linear-gradient(135deg, #007bff, #0056b3); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin: 0 auto;">
        ${usuario.nombre.charAt(0).toUpperCase()}
      </div>`;

    const badges = [];
    if (usuario.is_staff) badges.push('<span class="badge bg-info ms-1">Staff</span>');
    if (usuario.is_superuser) badges.push('<span class="badge bg-danger ms-1">Admin</span>');

    const grupos = usuario.grupos && usuario.grupos.length > 0 ?
      usuario.grupos.map(grupo => `<span class="badge bg-light text-dark me-1">${grupo}</span>`).join('') :
      '<span class="text-muted">Sin grupos</span>';

    row.innerHTML = `
      <td class="text-center">
        <span class="badge bg-secondary">${index + 1}</span>
      </td>
      <td class="text-center">${avatar}</td>
      <td>
        <div>
          <strong class="fw-bold">${usuario.nombre}</strong>
          ${badges.join('')}
        </div>
      </td>
      <td>
        <small class="text-muted">${usuario.email}</small>
      </td>
      <td>${grupos}</td>
      <td class="text-center">
        <button class="btn btn-success btn-sm asignar-usuario-avance" 
                data-usuario-id="${usuario.id}" 
                data-usuario-nombre="${usuario.nombre}">
          <i class="fas fa-user-plus me-1"></i>
          Asignar
        </button>
      </td>
    `;

    tbody.appendChild(row);
  });

  contador.textContent = usuarios.length;

  // Agregar event listeners a los botones de asignar
  document.querySelectorAll('.asignar-usuario-avance').forEach(btn => {
    btn.addEventListener('click', function () {
      const usuarioId = this.getAttribute('data-usuario-id');
      const usuarioNombre = this.getAttribute('data-usuario-nombre');
      seleccionarUsuarioAvance(usuarioId, usuarioNombre);
    });
  });

  // Configurar funcionalidad de búsqueda
  configurarBusquedaUsuarios();
}

// Función para configurar la búsqueda de usuarios
function configurarBusquedaUsuarios() {
  const inputBusqueda = document.getElementById('buscar-usuario-avance');
  const btnLimpiar = document.getElementById('limpiar-busqueda-avance');

  if (inputBusqueda) {
    inputBusqueda.addEventListener('input', function () {
      filtrarUsuarios(this.value.toLowerCase());
    });
  }

  if (btnLimpiar) {
    btnLimpiar.addEventListener('click', function () {
      inputBusqueda.value = '';
      filtrarUsuarios('');
    });
  }
}

// Función para filtrar usuarios en la tabla
function filtrarUsuarios(termino) {
  const filas = document.querySelectorAll('#lista-usuarios-avance .usuario-item');
  const contador = document.getElementById('contador-usuarios-avance');
  let usuariosVisibles = 0;

  filas.forEach(fila => {
    const nombre = fila.getAttribute('data-usuario-nombre').toLowerCase();
    const email = fila.getAttribute('data-usuario-email').toLowerCase();
    const grupos = fila.querySelector('td:nth-child(5)').textContent.toLowerCase();

    // Buscar en nombre, email o grupos
    const coincide = termino === '' ||
      nombre.includes(termino) ||
      email.includes(termino) ||
      grupos.includes(termino);

    if (coincide) {
      fila.style.display = '';
      usuariosVisibles++;
    } else {
      fila.style.display = 'none';
    }
  });

  if (contador) {
    contador.textContent = usuariosVisibles;
  }
}

// Función para seleccionar opción de avance (yo vs otro)
function seleccionarOpcionAvance(opcion) {
  console.log('👤 Opción seleccionada:', opcion);

  opcionAvanceSeleccionada = opcion;

  const btnContinuarYo = document.getElementById('btn-continuar-yo');
  const btnAsignarOtro = document.getElementById('btn-asignar-otro');
  const seccionAsignar = document.getElementById('seccion-asignar-usuario');
  const btnConfirmar = document.getElementById('btn-confirmar-avance');

  // Resetear estilos
  btnContinuarYo.classList.remove('btn-primary', 'btn-outline-primary');
  btnAsignarOtro.classList.remove('btn-success', 'btn-outline-success');

  if (opcion === 'yo') {
    btnContinuarYo.classList.add('btn-primary');
    btnAsignarOtro.classList.add('btn-outline-success');
    seccionAsignar.style.display = 'none';
    btnConfirmar.disabled = false;
    usuarioSeleccionadoAvance = null;
  } else if (opcion === 'otro') {
    btnContinuarYo.classList.add('btn-outline-primary');
    btnAsignarOtro.classList.add('btn-success');
    seccionAsignar.style.display = 'block';
    btnConfirmar.disabled = true; // Se habilitará cuando seleccione usuario
    usuarioSeleccionadoAvance = null;
  }
}

// Función para seleccionar usuario para asignar
function seleccionarUsuarioAvance(usuarioId, usuarioNombre) {
  console.log('👥 Usuario seleccionado:', usuarioNombre);

  usuarioSeleccionadoAvance = {
    id: usuarioId,
    nombre: usuarioNombre
  };

  // Actualizar estilos de botones
  document.querySelectorAll('.asignar-usuario-avance').forEach(btn => {
    btn.classList.remove('btn-primary');
    btn.classList.add('btn-success');
    btn.innerHTML = '<i class="fas fa-user-plus me-1"></i>Asignar';
  });

  const btnSeleccionado = document.querySelector(`[data-usuario-id="${usuarioId}"]`);
  if (btnSeleccionado) {
    btnSeleccionado.classList.remove('btn-success');
    btnSeleccionado.classList.add('btn-primary');
    btnSeleccionado.innerHTML = '<i class="fas fa-check me-1"></i>Seleccionado';
  }

  // Habilitar botón de confirmar
  document.getElementById('btn-confirmar-avance').disabled = false;
}

// Función para confirmar el avance
function confirmarAvance() {
  console.log('✅ Confirmando avance...');

  if (!opcionAvanceSeleccionada) {
    mostrarMensaje('Debe seleccionar una opción de avance', 'error');
    return;
  }

  if (opcionAvanceSeleccionada === 'otro' && !usuarioSeleccionadoAvance) {
    mostrarMensaje('Debe seleccionar un usuario para asignar', 'error');
    return;
  }

  const solicitudId = window.location.pathname.match(/solicitudes\/(\d+)\//)?.[1];
  const btnConfirmar = document.getElementById('btn-confirmar-avance');

  // Deshabilitar botón y mostrar loading
  btnConfirmar.disabled = true;
  btnConfirmar.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Procesando...';

  const data = {
    opcion: opcionAvanceSeleccionada,
    usuario_id: usuarioSeleccionadoAvance?.id || null,
    siguiente_subestado_id: siguienteSubestado?.id || null
  };

  fetch(`/workflow/api/solicitudes/${solicitudId}/avanzar-subestado/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalAvanzarSubestado'));
        modal.hide();

        // Mostrar mensaje de éxito
        const mensaje = opcionAvanceSeleccionada === 'yo' ?
          'Avanzando al siguiente subestado...' :
          `Solicitud asignada a ${usuarioSeleccionadoAvance.nombre}`;

        mostrarMensaje(mensaje, 'success');

        // Redirigir según la opción
        setTimeout(() => {
          if (opcionAvanceSeleccionada === 'yo') {
            window.location.href = data.redirect_url;
          } else {
            window.location.href = '/workflow/bandeja-mixta/';
          }
        }, 1500);

      } else {
        throw new Error(data.error || 'Error al procesar el avance');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      mostrarMensaje('Error al procesar el avance: ' + error.message, 'error');

      // Restaurar botón
      btnConfirmar.disabled = false;
      btnConfirmar.innerHTML = '<i class="fas fa-check me-1"></i>Confirmar Avance';
    });
}

// Función para mostrar errores en el modal
function mostrarErrorAvance(mensaje) {
  const errorDiv = document.getElementById('avance-error');
  const errorMensaje = document.getElementById('avance-error-mensaje');

  errorMensaje.textContent = mensaje;
  errorDiv.style.display = 'block';
}

// Event listener para cuando se abre el modal
document.addEventListener('DOMContentLoaded', function () {
  // Cargar transiciones negativas al cargar la página
  cargarTransicionesNegativas();

  const modalAvanzar = document.getElementById('modalAvanzarSubestado');
  if (modalAvanzar) {
    modalAvanzar.addEventListener('show.bs.modal', function () {
      console.log('🚀 Abriendo modal de avance...');
      cargarInformacionAvance();
    });

    modalAvanzar.addEventListener('hidden.bs.modal', function () {
      // Reset estado del modal
      opcionAvanceSeleccionada = null;
      usuarioSeleccionadoAvance = null;
      siguienteSubestado = null;

      document.getElementById('seccion-asignar-usuario').style.display = 'none';
      document.getElementById('btn-confirmar-avance').disabled = true;
      document.getElementById('avance-loading').style.display = 'none';
      document.getElementById('avance-error').style.display = 'none';
    });
  }
});

// Función de emergencia para habilitar el botón
function habilitarBotonEmergencia() {
  const btn = document.getElementById('btn-avanzar-subestado');
  if (btn) {
    btn.disabled = false;
    btn.title = 'Listo para avanzar';
    btn.classList.add('pulse');
    document.getElementById('validacion-mensaje').innerHTML = `
      <i class="fas fa-check-circle text-success me-1"></i>
      Botón habilitado manualmente
    `;
    console.log('✅ Botón habilitado por emergencia');
    return true;
  }
  return false;
}

// Función de diagnóstico rápido
function diagnosticarBotonAvanzar() {
  console.log('🔧 DIAGNÓSTICO DEL BOTÓN AVANZAR:');

  const btn = document.getElementById('btn-avanzar-subestado');
  console.log('1. Botón encontrado:', !!btn);
  console.log('2. Botón deshabilitado:', btn?.disabled);
  console.log('3. Título del botón:', btn?.title);

  const cards = document.querySelectorAll('.archivo-card-mejorada-backoffice');
  console.log('4. Cards encontradas:', cards.length);

  const botonesActivos = document.querySelectorAll('.calificar-btn-backoffice.activo');
  console.log('5. Botones activos:', botonesActivos.length);

  botonesActivos.forEach(boton => {
    console.log(`   - ${boton.dataset.estado} para requisito ${boton.dataset.requisito}`);
  });

  const obligatorios = [];
  cards.forEach(card => {
    const obligatorio = card.querySelector('.text-danger') !== null;
    const requisitoId = card.getAttribute('data-requisito-id');
    const nombre = card.querySelector('.archivo-nombre-backoffice')?.textContent?.trim();

    if (requisitoId && requisitoId !== '0' && obligatorio) {
      const botonBueno = card.querySelector('.calificar-btn-backoffice[data-estado="bueno"]');
      const activo = botonBueno?.classList.contains('activo');
      obligatorios.push({ nombre, requisitoId, activo });
    }
  });

  console.log('6. Documentos obligatorios:', obligatorios);

  return {
    botonEncontrado: !!btn,
    botonDeshabilitado: btn?.disabled,
    cardsTotal: cards.length,
    botonesActivos: botonesActivos.length,
    obligatorios
  };
}

// Funciones para transiciones negativas
let transicionesNegativas = [];

function cargarTransicionesNegativas() {
  const solicitudId = window.location.pathname.split('/')[3];

  fetch(`/workflow/api/solicitudes/${solicitudId}/transiciones-negativas/`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        transicionesNegativas = data.transiciones_negativas || [];

        // Mostrar/ocultar botón "Devolver a Oficial"
        const btnDevolver = document.getElementById('btn-devolver-oficial');
        if (btnDevolver) {
          if (data.tiene_transiciones_negativas) {
            btnDevolver.style.display = 'inline-block';
          } else {
            btnDevolver.style.display = 'none';
          }
        }
      }
    })
    .catch(error => {
      console.error('Error al cargar transiciones negativas:', error);
    });
}

function mostrarModalDevolucion() {
  // Cargar documentos problemáticos
  cargarDocumentosProblematicos();

  // Mostrar modal
  const modal = new bootstrap.Modal(document.getElementById('modalDevolverOficial'));
  modal.show();
}

function cargarDocumentosProblematicos() {
  const solicitudId = window.location.pathname.split('/')[3];

  fetch(`/workflow/api/solicitudes/${solicitudId}/validar-documentos/`)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('lista-documentos-problematicos');
      if (container && data.documentos_problematicos) {
        let html = '<h6>Documentos con problemas:</h6><ul class="list-unstyled">';

        data.documentos_problematicos.forEach(doc => {
          let problema = '';
          if (doc.problema === 'sin_calificar') {
            problema = 'Sin calificar';
          } else if (doc.problema === 'mal_calificado') {
            problema = `Calificado como "${doc.estado_actual}"`;
          }

          html += `<li class="text-danger"><i class="fas fa-exclamation-circle me-2"></i><strong>${doc.nombre}:</strong> ${problema}</li>`;
        });

        html += '</ul>';
        container.innerHTML = html;
      }
    })
    .catch(error => {
      console.error('Error al cargar documentos problemáticos:', error);
    });
}

function confirmarDevolucion() {
  const motivo = document.getElementById('motivo-devolucion').value.trim();

  if (!motivo) {
    alert('Debes proporcionar un motivo para la devolución');
    return;
  }

  if (transicionesNegativas.length === 0) {
    alert('No hay transiciones negativas disponibles');
    return;
  }

  // Usar la primera transición negativa disponible
  const transicion = transicionesNegativas[0];
  const solicitudId = window.location.pathname.split('/')[3];

  // Ejecutar transición
  fetch(`/workflow/api/solicitudes/${solicitudId}/ejecutar-transicion/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
      transicion_id: transicion.id,
      comentario: `Devuelto a oficial: ${motivo}`
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        mostrarMensaje('Solicitud devuelta al oficial exitosamente', 'success');

        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalDevolverOficial'));
        modal.hide();

        // Recargar página después de un momento
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        mostrarMensaje(`Error al devolver solicitud: ${data.error}`, 'error');
      }
    })
    .catch(error => {
      console.error('Error al devolver solicitud:', error);
      mostrarMensaje('Error al devolver solicitud', 'error');
    });
}

// Hacer funciones disponibles globalmente
window.inicializarValidacionTiempoReal = inicializarValidacionTiempoReal;
window.validarDocumentosEnTiempoReal = validarDocumentosEnTiempoReal;
window.seleccionarOpcionAvance = seleccionarOpcionAvance;
window.seleccionarUsuarioAvance = seleccionarUsuarioAvance;
window.confirmarAvance = confirmarAvance;
window.diagnosticarBotonAvanzar = diagnosticarBotonAvanzar;
window.habilitarBotonEmergencia = habilitarBotonEmergencia;
window.validarYAbrirModal = validarYAbrirModal;
window.cargarTransicionesNegativas = cargarTransicionesNegativas;
window.mostrarModalDevolucion = mostrarModalDevolucion;
window.confirmarDevolucion = confirmarDevolucion; 