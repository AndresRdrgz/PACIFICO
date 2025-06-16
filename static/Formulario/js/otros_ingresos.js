{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Entrevista de Cliente</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="{% static 'formulario/css/formulario.css' %}" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
  <style>
    .seccion { margin-bottom: 3rem; }
    .seccion h2 {
      display: flex;
      align-items: center;
      border-bottom: 2px solid var(--verde-pacifico);
      padding-bottom: .5rem;
      margin-bottom: 1.5rem;
      color: var(--gris-texto);
    }
    .seccion h2 .section-icon {
      margin-right: .5rem;
      color: var(--verde-pacifico);
    }
  </style>
</head>
<body class="form-bg">
  <div class="form-container">
    <div class="form-card shadow-lg rounded-4">
      <!-- HEADER -->
      <div class="form-header text-center">
        <img src="{% static 'formulario/img/logoCol.png' %}" alt="Logo Pacífico" class="logo mb-2">
        <h2 class="fw-bold mb-0" style="color:#fff;">Entrevista de Cliente</h2>
        <p class="mb-0 subtitulo" style="color:#e0ffe0;">Complete todos los datos a continuación</p>
      </div>
      <!-- BODY -->
      <div class="form-body">
        <form method="post" novalidate id="entrevista-form">
          {% csrf_token %}
          {% if form.errors or referencias_formset.errors or referencias_comerciales_formset.errors or otros_ingresos_formset.errors %}
            <div class="alert alert-danger">
              <strong>Por favor, corrija los campos obligatorios resaltados en rojo.</strong>
              <ul class="mb-0">
                {% for field in form %}{% for error in field.errors %}<li>{{ field.label }}: {{ error }}</li>{% endfor %}{% endfor %}
                {% for error in form.non_field_errors %}<li>{{ error }}</li>{% endfor %}
                {% for subform in referencias_formset.forms %}{% for field in subform %}{% for error in field.errors %}<li>Referencia Personal {{ forloop.parentloop.counter }} - {{ field.label }}: {{ error }}</li>{% endfor %}{% endfor %}{% for error in subform.non_field_errors %}<li>{{ error }}</li>{% endfor %}{% endfor %}
                {% for error in referencias_formset.non_form_errors %}<li>{{ error }}</li>{% endfor %}
                {% for subform in referencias_comerciales_formset.forms %}{% for field in subform %}{% for error in field.errors %}<li>Referencia Comercial {{ forloop.parentloop.counter }} - {{ field.label }}: {{ error }}</li>{% endfor %}{% endfor %}{% for error in subform.non_field_errors %}<li>{{ error }}</li>{% endfor %}{% endfor %}
                {% for error in referencias_comerciales_formset.non_form_errors %}<li>{{ error }}</li>{% endfor %}
                {% for subform in otros_ingresos_formset.forms %}{% for field in subform %}{% for error in field.errors %}<li>Otro Ingreso {{ forloop.parentloop.counter }} - {{ field.label }}: {{ error }}</li>{% endfor %}{% endfor %}{% for error in subform.non_field_errors %}<li>{{ error }}</li>{% endfor %}{% endfor %}
                {% for error in otros_ingresos_formset.non_form_errors %}<li>{{ error }}</li>{% endfor %}
              </ul>
            </div>
          {% endif %}

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-user-check"></i></span> 1. Datos Generales</h2>
            {% include 'formulario/componentes/datos_generales.html' with form=form %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-map-marker-alt"></i></span> 2. Dirección Residencial</h2>
            {% include 'formulario/componentes/direccion_residencial.html' with form=form %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-users"></i></span> 3. Datos del Cónyuge o Deudor Solidario</h2>
            {% include 'formulario/componentes/conyuge.html' with form=form %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-briefcase"></i></span> 4. Información Laboral y Otros Ingresos</h2>
            {% include 'formulario/componentes/informacion_laboral.html' with form=form otros_ingresos_formset=otros_ingresos_formset %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-user-shield"></i></span> 5. PEP - Persona Expuesta Políticamente</h2>
            {% include 'formulario/componentes/pep.html' with form=form %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-user-friends"></i></span> 6. Referencias Personales</h2>
            {% include 'formulario/componentes/referencias_personales.html' with referencias_formset=referencias_formset %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-briefcase"></i></span> 7. Referencias Comerciales</h2>
            {% include 'formulario/componentes/referencias_comerciales.html' with referencias_comerciales_formset=referencias_comerciales_formset %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-university"></i></span> 8. Datos Bancarios</h2>
            {% include 'formulario/componentes/datos_bancarios.html' with form=form %}
          </div>

          <div class="seccion">
            <h2><span class="section-icon"><i class="fas fa-check-circle"></i></span> 9. Autorizaciones</h2>
            {% include 'formulario/componentes/autorizaciones.html' with form=form %}
          </div>

          <div class="text-end mb-4">
            <button type="submit" class="btn btn-success btn-submit px-5 py-2">Enviar</button>
          </div>
        </form>

        {% if messages %}
          {% for message in messages %}
            <div class="alert alert-success mt-4 text-center">
              {{ message }}
            </div>
          {% endfor %}
        {% endif %}
      </div>
    </div>
  </div>
</body>
</html>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const addBtn = document.getElementById('add_otros_ingresos');
    const formsDiv = document.getElementById('otros-ingresos-forms');
    const managementForm = document.getElementById('id_otros_ingresos-TOTAL_FORMS');

    addBtn.addEventListener('click', function() {
      const totalForms = parseInt(managementForm.value, 10);
      const emptyForm = formsDiv.children[0].cloneNode(true);

      // Limpiar valores y errores
      emptyForm.querySelectorAll('input, select, textarea').forEach(el => {
        if (el.type === 'checkbox' || el.type === 'radio') {
          el.checked = false;
        } else {
          el.value = '';
        }
      });
      emptyForm.querySelectorAll('.text-danger, .is-invalid').forEach(el => {
        el.textContent = '';
        el.classList.remove('is-invalid');
      });

      // Actualizar los atributos name y id
      emptyForm.querySelectorAll('[name], [id]').forEach(el => {
        if (el.name) {
          el.name = el.name.replace(/\d+/, totalForms);
        }
        if (el.id) {
          el.id = el.id.replace(/\d+/, totalForms);
        }
      });

      formsDiv.appendChild(emptyForm);
      managementForm.value = totalForms + 1;
    });

    formsDiv.addEventListener('click', function(e) {
      if (e.target.closest('.remove-otro-ingreso')) {
        const form = e.target.closest('.otros-ingreso-form');
        if (formsDiv.children.length > 1) {
          form.remove();
          managementForm.value = formsDiv.children.length;
        }
      }
    });
  });
</script>