// Debug script para modalRequisitos
console.log("🔍 Iniciando debug del modal de requisitos...");

// 1. Verificar que Bootstrap esté disponible
if (typeof bootstrap === "undefined") {
  console.error("❌ Bootstrap no está disponible");
} else {
  console.log("✅ Bootstrap está disponible");
}

// 2. Verificar que el modal existe en el DOM
const modal = document.getElementById("modalRequisitosFaltantes");
if (!modal) {
  console.error('❌ Modal "modalRequisitosFaltantes" no encontrado en el DOM');
} else {
  console.log("✅ Modal encontrado en el DOM");
  console.log("Modal element:", modal);
}

// 3. Verificar que la función principal existe
if (typeof window.mostrarModalRequisitosFaltantes === "function") {
  console.log("✅ Función mostrarModalRequisitosFaltantes está disponible");
} else {
  console.error(
    "❌ Función mostrarModalRequisitosFaltantes no está disponible"
  );
}

// 4. Verificar elementos críticos del modal
const elementosImportantes = [
  "modalRequisitosFaltantesLabel",
  "listaRequisitosFaltantes",
  "loadingRequisitos",
  "btnValidarYContinuar",
  "etapaDestinoNombre",
];

elementosImportantes.forEach((id) => {
  const elemento = document.getElementById(id);
  if (elemento) {
    console.log(`✅ Elemento "${id}" encontrado`);
  } else {
    console.error(`❌ Elemento "${id}" no encontrado`);
  }
});

// 5. Función de prueba para modal
window.testModalRequisitos = function () {
  console.log("🧪 Probando modal de requisitos...");

  try {
    // Intentar mostrar el modal directamente con Bootstrap
    const modalElement = document.getElementById("modalRequisitosFaltantes");
    if (modalElement) {
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
      console.log("✅ Modal mostrado exitosamente con Bootstrap");

      // Cerrar después de 3 segundos para no interferir
      setTimeout(() => {
        modal.hide();
        console.log("🔒 Modal cerrado automáticamente");
      }, 3000);
    } else {
      console.error("❌ No se pudo encontrar el elemento del modal");
    }
  } catch (error) {
    console.error("❌ Error al mostrar modal:", error);
  }
};

// 6. Verificar si hay errores en la consola relacionados con el modal
console.log(
  "💡 Para probar el modal manualmente, ejecuta: testModalRequisitos()"
);

// 7. Interceptar llamadas a la función principal para debug
if (typeof window.mostrarModalRequisitosFaltantes === "function") {
  const originalFunction = window.mostrarModalRequisitosFaltantes;
  window.mostrarModalRequisitosFaltantes = function (
    solicitudId,
    nuevaEtapaId,
    nombreEtapa,
    callbackExito,
    callbackCancelacion
  ) {
    console.log(
      "🔍 [DEBUG] mostrarModalRequisitosFaltantes llamada con parámetros:"
    );
    console.log("  - solicitudId:", solicitudId);
    console.log("  - nuevaEtapaId:", nuevaEtapaId);
    console.log("  - nombreEtapa:", nombreEtapa);
    console.log("  - callbackExito:", typeof callbackExito);
    console.log("  - callbackCancelacion:", typeof callbackCancelacion);

    // Llamar a la función original
    try {
      return originalFunction.call(
        this,
        solicitudId,
        nuevaEtapaId,
        nombreEtapa,
        callbackExito,
        callbackCancelacion
      );
    } catch (error) {
      console.error(
        "❌ [DEBUG] Error en mostrarModalRequisitosFaltantes:",
        error
      );
      throw error;
    }
  };
  console.log("✅ Función interceptada para debug");
}

console.log(
  "🔍 Debug completado. Revisa los mensajes anteriores para identificar problemas."
);
