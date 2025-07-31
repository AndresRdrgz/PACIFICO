/**
 * MODAL ETAPA VISIBILITY FIX
 * =========================
 *
 * This script fixes the modal visibility issues by:
 * 1. Ensuring proper Bootstrap modal initialization
 * 2. Adding fallback methods for visibility
 * 3. Fixing z-index conflicts
 * 4. Adding debugging information
 */

// Enhanced modal visibility fix
window.fixModalEtapaVisibility = function () {
  console.log("🔧 Fixing modal etapa visibility...");

  // 1. Check if modal element exists
  const modalElement = document.getElementById("modalRequisitosFaltantes");
  if (!modalElement) {
    console.error("❌ Modal element not found");
    return false;
  }

  // 2. Check Bootstrap availability
  if (typeof bootstrap === "undefined") {
    console.error("❌ Bootstrap not available");
    return false;
  }

  // 3. Fix z-index issues
  const modalDialog = modalElement.querySelector(".modal-dialog");
  if (modalDialog) {
    modalDialog.style.zIndex = "1056"; // Above bootstrap backdrop (1055)
  }

  // 4. Ensure modal is properly structured
  modalElement.style.zIndex = "1055";
  modalElement.style.display = "block"; // Ensure it's not hidden by CSS

  // 5. Remove any existing backdrop conflicts
  const existingBackdrops = document.querySelectorAll(".modal-backdrop");
  existingBackdrops.forEach((backdrop) => {
    if (backdrop.id && backdrop.id.includes("modalRequisitosFaltantes")) {
      backdrop.remove();
    }
  });

  console.log("✅ Modal visibility fixes applied");
  return true;
};

// Enhanced show modal function with visibility fixes
window.showModalRequisitosFaltantesFixed = function (
  solicitudId,
  nuevaEtapaId,
  nombreEtapa,
  callbackExito,
  callbackCancelacion
) {
  console.log("🎭 ShowModalRequisitosFaltantesFixed called");
  console.log("📋 Parameters:", { solicitudId, nuevaEtapaId, nombreEtapa });

  // Apply visibility fixes first
  if (!window.fixModalEtapaVisibility()) {
    console.error("❌ Failed to apply visibility fixes");
    return;
  }

  // Set up the modal content
  const etapaDestinoElement = document.getElementById("etapaDestinoNombre");
  if (etapaDestinoElement) {
    etapaDestinoElement.textContent = nombreEtapa;
  }

  // Show loading
  const loadingElement = document.getElementById("loadingRequisitos");
  const listaContainer = document.getElementById("listaRequisitosFaltantes");

  if (loadingElement) loadingElement.style.display = "block";
  if (listaContainer) listaContainer.innerHTML = "";

  // Get modal element
  const modalElement = document.getElementById("modalRequisitosFaltantes");

  try {
    // Try Bootstrap modal first
    console.log("🎭 Attempting Bootstrap modal...");

    const modal = new bootstrap.Modal(modalElement, {
      backdrop: "static",
      keyboard: false,
    });

    // Force show the modal
    modal.show();
    console.log("✅ Bootstrap modal.show() called");

    // Verify modal is actually visible
    setTimeout(() => {
      const isVisible =
        modalElement.classList.contains("show") &&
        modalElement.style.display !== "none" &&
        getComputedStyle(modalElement).display !== "none";

      if (!isVisible) {
        console.warn("⚠️ Modal not visible, applying manual fixes...");
        window.forceShowModal(modalElement);
      } else {
        console.log("✅ Modal is visible via Bootstrap");
      }
    }, 100);

    // Set up event listeners
    modalElement.addEventListener(
      "shown.bs.modal",
      function () {
        console.log("✅ Modal shown event fired");
      },
      { once: true }
    );
  } catch (error) {
    console.error("❌ Bootstrap modal failed:", error);
    // Use manual fallback
    window.forceShowModal(modalElement);
  }

  // Load requisitos (simulated for testing)
  setTimeout(() => {
    if (loadingElement) loadingElement.style.display = "none";

    // Simulate requisitos data
    const testRequisitos = [
      {
        id: 1,
        nombre: "Documento de Identidad",
        esta_cumplido: false,
        descripcion: "Cedula de ciudadania o documento equivalente",
      },
    ];

    if (typeof window.llenarListaRequisitosFaltantes === "function") {
      window.llenarListaRequisitosFaltantes(testRequisitos, 1, 0);
    } else {
      // Simple fallback
      if (listaContainer) {
        listaContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Test: Se requiere completar documentos faltantes
                    </div>
                `;
      }
    }
  }, 500);
};

// Force show modal manually
window.forceShowModal = function (modalElement) {
  console.log("🔧 Force showing modal manually...");

  // Remove hidden attributes
  modalElement.removeAttribute("aria-hidden");
  modalElement.setAttribute("aria-modal", "true");
  modalElement.style.display = "block";
  modalElement.classList.add("show");

  // Ensure proper z-index
  modalElement.style.zIndex = "1055";

  // Create backdrop manually
  let backdrop = document.getElementById("modalRequisitosFaltantes-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop fade show";
    backdrop.id = "modalRequisitosFaltantes-backdrop";
    backdrop.style.zIndex = "1050"; // Below modal
    document.body.appendChild(backdrop);
  }

  // Add modal-open class to body
  document.body.classList.add("modal-open");

  // Center the modal
  const modalDialog = modalElement.querySelector(".modal-dialog");
  if (modalDialog) {
    modalDialog.style.transform = "translate(0, 50px)";
    modalDialog.style.margin = "1.5rem auto";
  }

  console.log("✅ Modal forced to show");
};

// Enhanced close function
window.cerrarModalRequisitosFijo = function () {
  console.log("🚪 Closing modal (fixed version)...");

  const modalElement = document.getElementById("modalRequisitosFaltantes");
  if (!modalElement) return;

  try {
    // Try Bootstrap first
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) {
      modal.hide();
      console.log("✅ Modal closed via Bootstrap");
    } else {
      throw new Error("No Bootstrap instance");
    }
  } catch (error) {
    // Manual close
    console.log("🔧 Manual modal close...");

    modalElement.style.display = "none";
    modalElement.classList.remove("show");
    modalElement.setAttribute("aria-hidden", "true");
    modalElement.removeAttribute("aria-modal");

    // Remove backdrop
    const backdrop = document.getElementById(
      "modalRequisitosFaltantes-backdrop"
    );
    if (backdrop) {
      backdrop.remove();
    }

    // Remove modal-open from body
    document.body.classList.remove("modal-open");

    console.log("✅ Modal closed manually");
  }
};

// Test function to verify modal visibility
window.testModalVisibility = function () {
  console.log("🧪 Testing modal visibility...");

  const results = {
    modalExists: false,
    bootstrapAvailable: false,
    modalVisible: false,
    modalInDOM: false,
    hasCorrectClasses: false,
    zIndexOK: false,
  };

  // Test 1: Modal exists
  const modalElement = document.getElementById("modalRequisitosFaltantes");
  results.modalExists = !!modalElement;
  results.modalInDOM = document.contains(modalElement);

  if (modalElement) {
    // Test 2: Bootstrap available
    results.bootstrapAvailable = typeof bootstrap !== "undefined";

    // Test 3: Modal visible
    const computedStyle = getComputedStyle(modalElement);
    results.modalVisible =
      computedStyle.display !== "none" &&
      computedStyle.visibility !== "hidden" &&
      modalElement.offsetHeight > 0;

    // Test 4: Correct classes
    results.hasCorrectClasses =
      modalElement.classList.contains("modal") &&
      modalElement.classList.contains("fade");

    // Test 5: Z-index
    const zIndex = parseInt(computedStyle.zIndex) || 0;
    results.zIndexOK = zIndex >= 1050;
  }

  console.table(results);

  // Visual test
  if (results.modalExists && !results.modalVisible) {
    console.log("🔧 Modal exists but not visible, trying to show...");
    window.showModalRequisitosFaltantesFixed(
      1,
      2,
      "Test Etapa",
      () => console.log("✅ Test success callback"),
      () => console.log("❌ Test cancel callback")
    );
  }

  return results;
};

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  console.log("🚀 Modal visibility fixes loaded");

  // Replace original function if it exists
  if (typeof window.mostrarModalRequisitosFaltantes === "function") {
    window.mostrarModalRequisitosFaltantesOriginal =
      window.mostrarModalRequisitosFaltantes;
  }

  // Override with fixed version
  window.mostrarModalRequisitosFaltantes =
    window.showModalRequisitosFaltantesFixed;

  // Override close function
  window.cerrarModalRequisitos = window.cerrarModalRequisitosFijo;

  // Add test function to window for debugging
  window.testModal = window.testModalVisibility;

  console.log("✅ Modal functions overridden with fixed versions");
  console.log("💡 Use window.testModal() to test modal visibility");
  console.log(
    '💡 Use window.showModalRequisitosFaltantesFixed(1, 2, "Test") to test modal'
  );
});

// CSS fixes for modal visibility
const modalCSS = `
<style id="modal-etapa-fixes">
/* Modal visibility fixes */
.modal#modalRequisitosFaltantes {
    z-index: 1055 !important;
}

.modal#modalRequisitosFaltantes .modal-dialog {
    z-index: 1056 !important;
    margin: 1.5rem auto !important;
}

.modal#modalRequisitosFaltantes.show {
    display: block !important;
}

/* Backdrop fixes */
.modal-backdrop {
    z-index: 1050 !important;
}

.modal-backdrop#modalRequisitosFaltantes-backdrop {
    z-index: 1050 !important;
}

/* Ensure modal is above other elements */
.modal#modalRequisitosFaltantes {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
}

/* Debug outline for testing */
.modal#modalRequisitosFaltantes.debug-outline {
    border: 3px solid red !important;
}

.modal#modalRequisitosFaltantes.debug-outline .modal-dialog {
    border: 2px solid blue !important;
}
</style>
`;

// Inject CSS fixes
document.head.insertAdjacentHTML("beforeend", modalCSS);
