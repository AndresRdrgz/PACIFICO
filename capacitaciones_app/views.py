# capacitaciones_app/views.py

# Este archivo importa todas las vistas organizadas en archivos separados
from .views_cursos import (
    lista_cursos,
    detalle_curso,
    ver_tema,
    marcar_tema_completado,
)

from .views_quiz import (
    quiz_modulo,
)

from .views_certificados import (
    certificado,
)

from .views_asignacion import (
    asignacion_admin,
    asignar_curso_ajax,
    desasignar_curso_ajax,
    cursos_asignados_ajax,
    exportar_asignaciones_excel,
)

