document.addEventListener('DOMContentLoaded', function () {

    // ✅ Agrega encabezados "MÓDULO N"
    function agregarTituloModulos() {
        const modulos = document.querySelectorAll('.inline-group .inline-related');

        modulos.forEach((modulo, i) => {
            let titulo = modulo.querySelector('h2');
            if (!titulo) {
                const encabezado = document.createElement('h2');
                encabezado.textContent = `MÓDULO ${i + 1}`;
                encabezado.style.backgroundColor = '#004d99';
                encabezado.style.color = 'white';
                encabezado.style.padding = '10px';
                encabezado.style.fontSize = '16px';
                encabezado.style.borderRadius = '4px';
                encabezado.style.marginBottom = '10px';
                modulo.prepend(encabezado);
            }
        });
    }

    // ✅ Mostrar/Ocultar preguntas si tiene_quiz está activado
    function togglePreguntas(moduloElement) {
        const checkbox = moduloElement.querySelector('input[id$="tiene_quiz"]');
        const preguntas = moduloElement.querySelector('.nested-pregunta');

        if (!checkbox || !preguntas) return;

        preguntas.style.display = checkbox.checked ? 'block' : 'none';

        checkbox.addEventListener('change', () => {
            preguntas.style.display = checkbox.checked ? 'block' : 'none';
        });
    }

    // ✅ Aplicar toggle a todos los módulos
    function aplicarTogglePreguntas() {
        document.querySelectorAll('.inline-group .inline-related').forEach((modulo) => {
            togglePreguntas(modulo);
        });
    }

    // Ejecutar al cargar
    agregarTituloModulos();
    aplicarTogglePreguntas();

    // Reaplicar si agregan un nuevo módulo dinámicamente
    document.body.addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('add-row')) {
            setTimeout(() => {
                agregarTituloModulos();
                aplicarTogglePreguntas();
            }, 300);
        }
    });

});
