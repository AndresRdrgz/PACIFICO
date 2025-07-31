"""
Comando de Django para cargar plantillas de orden de expediente desde un archivo Excel.

Uso:
    python manage.py cargar_plantillas_excel archivo.xlsx --pipeline="Nombre Pipeline"

Formato del Excel:
    - Columna A: seccion
    - Columna B: orden_seccion (1, 2, 3... para ordenar las secciones)
    - Columna C: nombre_documento  
    - Columna D: orden
    - Columna E: obligatorio (si/no, true/false, 1/0)
    - Columna F: descripcion (opcional)
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from workflow.modelsWorkflow import Pipeline, PlantillaOrdenExpediente
import pandas as pd
import os


class Command(BaseCommand):
    help = 'Carga plantillas de orden de expediente desde un archivo Excel'

    def add_arguments(self, parser):
        parser.add_argument(
            'archivo_excel',
            type=str,
            help='Ruta al archivo Excel con las plantillas'
        )
        parser.add_argument(
            '--pipeline',
            type=str,
            required=True,
            help='Nombre del pipeline al que aplicar las plantillas'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default=0,
            help='Nombre o índice de la hoja de Excel (por defecto: 0)'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Limpiar plantillas existentes del pipeline antes de cargar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular la carga sin guardar en la base de datos'
        )

    def handle(self, *args, **options):
        archivo_excel = options['archivo_excel']
        pipeline_nombre = options['pipeline']
        sheet = options['sheet']
        limpiar = options['limpiar']
        dry_run = options['dry_run']

        self.stdout.write(f"🚀 Iniciando carga de plantillas desde: {archivo_excel}")
        
        # Validar archivo
        if not os.path.exists(archivo_excel):
            raise CommandError(f'El archivo {archivo_excel} no existe')

        # Obtener pipeline
        try:
            pipeline = Pipeline.objects.get(nombre=pipeline_nombre)
            self.stdout.write(f"✅ Pipeline encontrado: {pipeline.nombre}")
        except Pipeline.DoesNotExist:
            raise CommandError(f'Pipeline "{pipeline_nombre}" no encontrado')

        # Leer Excel
        try:
            self.stdout.write(f"📖 Leyendo archivo Excel...")
            df = pd.read_excel(archivo_excel, sheet_name=sheet)
            self.stdout.write(f"✅ Archivo leído exitosamente: {len(df)} filas")
        except Exception as e:
            raise CommandError(f'Error al leer el archivo Excel: {str(e)}')

        # Validar columnas requeridas
        columnas_requeridas = ['seccion', 'orden_seccion', 'nombre_documento', 'orden', 'obligatorio']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            raise CommandError(f'Columnas faltantes en el Excel: {", ".join(columnas_faltantes)}')

        self.stdout.write(f"✅ Estructura del Excel validada")

        # Procesar datos
        plantillas_procesadas = []
        errores = []

        for index, row in df.iterrows():
            try:
                # Validar datos de la fila
                seccion = str(row['seccion']).strip()
                orden_seccion = int(row['orden_seccion'])
                nombre_documento = str(row['nombre_documento']).strip()
                orden = int(row['orden'])
                obligatorio = self._parse_boolean(row['obligatorio'])
                descripcion = str(row.get('descripcion', '')).strip() if pd.notna(row.get('descripcion')) else None

                if not seccion or not nombre_documento:
                    errores.append(f"Fila {index + 2}: seccion y nombre_documento son obligatorios")
                    continue

                if orden <= 0:
                    errores.append(f"Fila {index + 2}: orden debe ser mayor a 0")
                    continue

                if orden_seccion <= 0:
                    errores.append(f"Fila {index + 2}: orden_seccion debe ser mayor a 0")
                    continue

                plantilla_data = {
                    'pipeline': pipeline,
                    'seccion': seccion,
                    'orden_seccion': orden_seccion,
                    'nombre_documento': nombre_documento,
                    'orden': orden,
                    'obligatorio': obligatorio,
                    'descripcion': descripcion
                }

                plantillas_procesadas.append(plantilla_data)

            except Exception as e:
                errores.append(f"Fila {index + 2}: {str(e)}")

        # Mostrar resumen
        self.stdout.write(f"\n📊 Resumen de procesamiento:")
        self.stdout.write(f"  - Plantillas válidas: {len(plantillas_procesadas)}")
        self.stdout.write(f"  - Errores encontrados: {len(errores)}")

        if errores:
            self.stdout.write(f"\n❌ Errores encontrados:")
            for error in errores[:10]:  # Mostrar solo los primeros 10 errores
                self.stdout.write(f"  - {error}")
            if len(errores) > 10:
                self.stdout.write(f"  ... y {len(errores) - 10} errores más")

        if not plantillas_procesadas:
            raise CommandError("No hay plantillas válidas para procesar")

        # Mostrar estadísticas por sección
        secciones = {}
        for plantilla in plantillas_procesadas:
            seccion = plantilla['seccion']
            if seccion not in secciones:
                secciones[seccion] = 0
            secciones[seccion] += 1

        self.stdout.write(f"\n📂 Documentos por sección:")
        for seccion, count in sorted(secciones.items()):
            self.stdout.write(f"  - {seccion}: {count} documentos")

        if dry_run:
            self.stdout.write(f"\n🔍 DRY RUN - No se guardaron cambios en la base de datos")
            return

        # Confirmar antes de proceder
        if not options.get('verbosity', 1) == 0:  # Si no es --verbosity=0
            confirmar = input(f"\n¿Proceder con la carga de {len(plantillas_procesadas)} plantillas? (s/N): ")
            if confirmar.lower() not in ['s', 'si', 'y', 'yes']:
                self.stdout.write("❌ Operación cancelada por el usuario")
                return

        # Guardar en base de datos
        try:
            with transaction.atomic():
                # Limpiar plantillas existentes si se solicita
                if limpiar:
                    plantillas_existentes = PlantillaOrdenExpediente.objects.filter(pipeline=pipeline)
                    count_eliminadas = plantillas_existentes.count()
                    plantillas_existentes.delete()
                    self.stdout.write(f"🗑️  Eliminadas {count_eliminadas} plantillas existentes")

                # Crear nuevas plantillas
                plantillas_creadas = []
                for plantilla_data in plantillas_procesadas:
                    plantilla, created = PlantillaOrdenExpediente.objects.get_or_create(
                        pipeline=plantilla_data['pipeline'],
                        seccion=plantilla_data['seccion'],
                        orden=plantilla_data['orden'],
                        defaults=plantilla_data
                    )
                    
                    if created:
                        plantillas_creadas.append(plantilla)
                    else:
                        # Actualizar plantilla existente
                        plantilla.nombre_documento = plantilla_data['nombre_documento']
                        plantilla.orden_seccion = plantilla_data['orden_seccion']
                        plantilla.obligatorio = plantilla_data['obligatorio']
                        plantilla.descripcion = plantilla_data['descripcion']
                        plantilla.save()

                self.stdout.write(f"✅ Procesamiento completado:")
                self.stdout.write(f"  - Plantillas creadas: {len(plantillas_creadas)}")
                self.stdout.write(f"  - Plantillas actualizadas: {len(plantillas_procesadas) - len(plantillas_creadas)}")

                # Mostrar resumen final
                total_plantillas = PlantillaOrdenExpediente.objects.filter(pipeline=pipeline).count()
                self.stdout.write(f"  - Total plantillas en pipeline: {total_plantillas}")

        except Exception as e:
            raise CommandError(f'Error al guardar en la base de datos: {str(e)}')

        self.stdout.write(f"\n🎉 ¡Carga completada exitosamente!")
        self.stdout.write(f"Las plantillas ya están disponibles para aplicar a solicitudes del pipeline '{pipeline.nombre}'")

    def _parse_boolean(self, value):
        """Convierte diferentes formatos de boolean a True/False"""
        if pd.isna(value):
            return True  # Por defecto obligatorio
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ['si', 'sí', 's', 'yes', 'y', 'true', '1', 'obligatorio']:
                return True
            elif value in ['no', 'n', 'false', '0', 'opcional']:
                return False
        
        # Si no se puede determinar, asumir obligatorio
        return True