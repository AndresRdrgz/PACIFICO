// Comprehensive fix for modalRequisitos not showing issue
console.log("🛠️ Aplicando fix para modalRequisitos...");

// Wait for DOM to be ready
document.addEventListener("DOMContentLoaded", function () {
  // 1. Verify Bootstrap is available
  if (typeof bootstrap === "undefined") {
    console.error(
      "❌ Bootstrap no disponible - cargando desde CDN como fallback"
    );

    // Load Bootstrap as fallback
    const bootstrapCSS = document.createElement("link");
    bootstrapCSS.rel = "stylesheet";
    bootstrapCSS.href =
      "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css";
    document.head.appendChild(bootstrapCSS);

    const bootstrapJS = document.createElement("script");
    bootstrapJS.src =
      "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js";
    document.head.appendChild(bootstrapJS);

    return;
  }

  console.log("✅ Bootstrap disponible");

  // 2. Verify modal element exists
  const modalElement = document.getElementById("modalRequisitosFaltantes");
  if (!modalElement) {
    console.error("❌ Modal element no encontrado");
    return;
  }

  console.log("✅ Modal element encontrado");

  // 3. Enhanced modal show function with error handling
  window.showModalRequisitosSafe = function (
    solicitudId,
    nuevaEtapaId,
    nombreEtapa,
    callbackExito,
    callbackCancelacion
  ) {
    console.log("🔍 [SAFE] Mostrando modal de requisitos - parámetros:", {
      solicitudId,
      nuevaEtapaId,
      nombreEtapa,
    });

    try {
      // Call original function
      if (typeof window.mostrarModalRequisitosFaltantes === "function") {
        window.mostrarModalRequisitosFaltantes(
          solicitudId,
          nuevaEtapaId,
          nombreEtapa,
          callbackExito,
          callbackCancelacion
        );
      } else {
        throw new Error(
          "Función mostrarModalRequisitosFaltantes no disponible"
        );
      }
    } catch (error) {
      console.error("❌ [SAFE] Error en función original:", error);

      // Fallback: show modal directly
      try {
        console.log("🔄 [SAFE] Intentando mostrar modal directamente...");

        // Update modal title
        const etapaDestinoElement =
          document.getElementById("etapaDestinoNombre");
        if (etapaDestinoElement) {
          etapaDestinoElement.textContent = nombreEtapa;
        }

        // Show loading
        const loadingElement = document.getElementById("loadingRequisitos");
        if (loadingElement) {
          loadingElement.style.display = "block";
        }

        // Show modal
        const modal = new bootstrap.Modal(modalElement, {
          backdrop: "static",
          keyboard: false,
        });

        modal.show();
        console.log("✅ [SAFE] Modal mostrado con fallback");

        // Hide loading after a moment
        setTimeout(() => {
          if (loadingElement) {
            loadingElement.style.display = "none";
          }

          // Show error message in modal
          const listaContainer = document.getElementById(
            "listaRequisitosFaltantes"
          );
          if (listaContainer) {
            listaContainer.innerHTML = `
                            <div class="alert alert-warning">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                <strong>Error técnico:</strong> No se pudieron cargar los requisitos. 
                                Por favor, intenta nuevamente o contacta al administrador.
                            </div>
                        `;
          }
        }, 1000);
      } catch (fallbackError) {
        console.error("❌ [SAFE] Error en fallback:", fallbackError);
        alert(
          "Error crítico: No se puede mostrar el modal de requisitos. Por favor, recarga la página."
        );
      }
    }
  };

  // 4. Override original function with safer version
  if (typeof window.mostrarModalRequisitosFaltantes === "function") {
    const originalFunction = window.mostrarModalRequisitosFaltantes;

    window.mostrarModalRequisitosFaltantes = function (
      solicitudId,
      nuevaEtapaId,
      nombreEtapa,
      callbackExito,
      callbackCancelacion
    ) {
      console.log("🔍 [INTERCEPTED] mostrarModalRequisitosFaltantes llamada");

      // Enhanced parameter validation
      if (!solicitudId || solicitudId === "undefined" || solicitudId === "") {
        console.error("❌ [INTERCEPTED] solicitudId inválido:", solicitudId);
        return;
      }

      if (
        !nuevaEtapaId ||
        nuevaEtapaId === "undefined" ||
        nuevaEtapaId === ""
      ) {
        console.error("❌ [INTERCEPTED] nuevaEtapaId inválido:", nuevaEtapaId);
        return;
      }

      if (!nombreEtapa || nombreEtapa === "undefined" || nombreEtapa === "") {
        console.error("❌ [INTERCEPTED] nombreEtapa inválido:", nombreEtapa);
        return;
      }

      // Call original with enhanced error handling
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
        console.error("❌ [INTERCEPTED] Error en función original:", error);

        // Show modal anyway with error message
        window.showModalRequisitosSafe(
          solicitudId,
          nuevaEtapaId,
          nombreEtapa,
          callbackExito,
          callbackCancelacion
        );
      }
    };

    console.log("✅ Función original interceptada para debug mejorado");
  }

  // 5. Test function
  window.testModalRequisitosFixed = function () {
    console.log("🧪 Probando modal corregido...");

    const testParams = {
      solicitudId: 1,
      nuevaEtapaId: 1,
      nombreEtapa: "Etapa de Prueba",
    };

    window.showModalRequisitosSafe(
      testParams.solicitudId,
      testParams.nuevaEtapaId,
      testParams.nombreEtapa,
      function () {
        console.log("✅ Callback éxito ejecutado");
      },
      function () {
        console.log("❌ Callback cancelación ejecutado");
      }
    );
  };

  // 6. Enhanced modal event debugging
  modalElement.addEventListener("show.bs.modal", function () {
    console.log("🎭 Modal show event triggered");
  });

  modalElement.addEventListener("shown.bs.modal", function () {
    console.log("✅ Modal shown successfully");
  });

  modalElement.addEventListener("hide.bs.modal", function () {
    console.log("🚪 Modal hide event triggered");
  });

  modalElement.addEventListener("hidden.bs.modal", function () {
    console.log("🔒 Modal hidden successfully");
  });

  console.log("✅ Fix para modalRequisitos aplicado correctamente");
  console.log("💡 Para probar: testModalRequisitosFixed()");
});
