# 🎯 PROMPTS CORPORATIVOS - DASHBOARD EJECUTIVO MODERNO

## 📋 Descripción General
Sistema de prompts para crear dashboards modernos con enfoque corporativo sobrio, usando Tailwind CSS, glassmorphism, animaciones y micro-interacciones, diseñado especialmente para líderes y ejecutivos.

## 🎨 Paleta de Colores Corporativa

### Colores Principales (Sobrios y Profesionales):
- **Azul Corporativo**: `from-blue-600 to-blue-800`, `text-blue-600`
- **Gris Ejecutivo**: `from-slate-600 to-slate-800`, `text-slate-700`
- **Gris Neutro**: `from-gray-600 to-gray-800`, `text-gray-600`
- **Índigo Profesional**: `from-indigo-600 to-indigo-800`, `text-indigo-600`

### Fondos y Efectos:
- **Glassmorphism**: `bg-white/10 backdrop-blur-lg border border-white/20`
- **Cards Transparentes**: `bg-white/20 backdrop-blur-sm border border-white/30`
- **Bases Neutrales**: `bg-slate-200`, `text-slate-700`

## 🚀 PROMPT PRINCIPAL - DASHBOARD CORPORATIVO

```
Actualizar este dashboard para que tenga un look moderno, corporativo y sobrio, apropiado para líderes y ejecutivos. Usar:

ESTILO VISUAL:
- Tailwind CSS con glassmorphism (bg-white/10 backdrop-blur-lg)
- Colores corporativos: azul (#3b82f6), gris slate (#475569), indigo (#4f46e5)
- EVITAR colores vibrantes como verde lima, rosa, cyan, amber - solo usar tonos sobrios
- Gradientes sutiles: from-blue-600 to-blue-800, from-slate-600 to-slate-800
- Fondos semitransparentes: bg-white/20 backdrop-blur-sm

ANIMACIONES SOBRIAS:
- hover:scale-105 transition-all duration-300
- animate-bounce-in con delays escalonados (0.1s, 0.2s, 0.3s)
- animate-float para iconos
- Micro-interacciones suaves y profesionales

ESTRUCTURA:
- Cards con rounded-2xl o rounded-3xl
- Sombras: shadow-xl hover:shadow-2xl
- Bordes sutiles: border border-white/20
- Espaciado generoso: p-6, p-8, gap-6

COMPONENTES:
- KPIs con iconos SVG y métricas grandes
- Barras de progreso con bg-slate-200 y fill corporativo
- Badges con colores sobrios: bg-blue-600, bg-slate-600, bg-indigo-600
- Texto en slate-700, slate-600 para mejor legibilidad corporativa

OBJETIVO: Dashboard elegante, minimalista y profesional que inspire confianza en líderes empresariales.
```

## 🎨 PROMPT PARA CARDS MODERNAS

```
Crear cards modernas con estilo corporativo:
- bg-white/10 backdrop-blur-lg rounded-2xl p-6
- border border-white/20 shadow-xl hover:shadow-2xl
- transition-all duration-300 hover:scale-105
- Gradientes corporativos: from-slate-600 to-slate-800
- Iconos con animate-float y bg-corporativo/20
- Texto en slate-700 y slate-600
- Efectos de círculos decorativos: bg-blue-500/10 rounded-full
```

## 📊 PROMPT PARA MÉTRICAS Y KPIs

```
Diseñar métricas corporativas:
- Números grandes: text-3xl font-bold text-slate-700
- Labels descriptivos: text-slate-500 text-sm
- Barras de progreso: bg-slate-200 con fill blue-500, slate-500, indigo-500
- Animaciones de entrada: animate-bounce-in con delays
- Glassmorphism para contenedores: bg-white/10 backdrop-blur-lg
- Iconos SVG con colores corporativos matching
```

## 🎯 PROMPT PARA SECCIONES DE ANÁLISIS

```
Crear secciones de análisis con estilo ejecutivo:
- Contenedores: bg-white/10 backdrop-blur-lg rounded-3xl p-8
- Headers con iconos: gradient corporativo (slate, blue, indigo)
- Progress circles con gradientes sobrios
- Badges informativos: bg-white/20 backdrop-blur-sm
- Data points con text-slate-700 font-semibold
- Micro-interacciones suaves y profesionales
```

## 💫 ANIMACIONES CORPORATIVAS

### CSS Personalizado:
```css
@keyframes bounce-in {
    0% { opacity: 0; transform: translateY(30px) scale(0.9); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}

@keyframes fade-in {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-bounce-in { animation: bounce-in 0.6s ease-out forwards; }
.animate-float { animation: float 3s ease-in-out infinite; }
.animate-fade-in { animation: fade-in 1s ease-out; }
```

## 🎨 COLORES CORPORATIVOS ESPECÍFICOS

### ✅ USAR (Sobrios y Profesionales):
- Blue: #2563eb, #1d4ed8, #1e40af
- Slate: #475569, #334155, #1e293b
- Gray: #4b5563, #374151, #1f2937
- Indigo: #4338ca, #3730a3, #312e81

### ❌ EVITAR (Muy Coloridos):
- Lime, Pink, Cyan, Amber, Orange, Purple vibrante
- Cualquier color muy saturado o "arcoíris"
- Combinaciones de más de 3-4 colores diferentes

## 📝 VARIABLES DE CONTEXTO DJANGO

```python
# Variables disponibles en el template:
context = {
    'total_cursos': int,
    'total_usuarios': int,
    'total_asignaciones': int,
    'total_cursos_completados': int,
    'tasa_completado': float,
    'tasa_participacion': float,
    'total_horas_disponibles': float,
    'total_horas_completadas': float,
    'promedio_duracion_curso': float,
    'total_cursos_con_duracion': int,
    # ... más variables según necesidad
}
```

## 🔄 PROMPT PARA REPLICAR EN OTRAS APPS

```
Aplicar el mismo estilo corporativo moderno a [NOMBRE_APP]:
1. Usar la paleta corporativa (blue, slate, gray, indigo)
2. Implementar glassmorphism: bg-white/10 backdrop-blur-lg
3. Añadir animaciones sobrias: hover:scale-105, animate-bounce-in
4. Cards con rounded-2xl, shadow-xl, border border-white/20
5. Texto en tonos slate para máxima legibilidad
6. Micro-interacciones profesionales y suaves
7. EVITAR colores muy vibrantes o "arcoíris"
8. Mantener diseño limpio, minimalista y ejecutivo

OBJETIVO: Consistencia visual corporativa en toda la aplicación.
```

## 🎨 COMBINACIONES CORPORATIVAS ESPECÍFICAS

### Para KPIs Principales:
1. **Curso**: `from-slate-600 to-slate-800` + `text-slate-200`
2. **Usuarios**: `from-blue-600 to-blue-800` + `text-blue-200`
3. **Asignaciones**: `from-gray-600 to-gray-800` + `text-gray-200`
4. **Completados**: `from-indigo-600 to-indigo-800` + `text-indigo-200`

### Para Métricas de Duración:
1. **Horas Totales**: `bg-blue-500/20` + `text-blue-600`
2. **Horas Completadas**: `bg-slate-500/20` + `text-slate-600`
3. **Promedio**: `bg-gray-500/20` + `text-gray-600`
4. **Con Duración**: `bg-indigo-500/20` + `text-indigo-600`

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN CORPORATIVA

- [ ] ✅ Colores corporativos aplicados (blue, slate, gray, indigo)
- [ ] ✅ Glassmorphism implementado (backdrop-blur-lg)
- [ ] ✅ Animaciones sobrias añadidas
- [ ] ✅ Cards modernas con rounded-2xl
- [ ] ✅ Micro-interacciones profesionales
- [ ] ✅ Tipografía clara (slate-700, slate-600)
- [ ] ✅ Eliminados colores muy vibrantes
- [ ] ✅ Probado en desktop y mobile
- [ ] ✅ Performance optimizada
- [ ] ✅ Accesibilidad verificada

---

## 🏢 CASOS DE USO CORPORATIVOS

### Dashboard Ejecutivo:
- Métricas financieras con tonos azul/slate
- KPIs operacionales en formato minimalista
- Gráficos con paleta corporativa restringida

### Panel de Liderazgo:
- Indicadores de rendimiento en estilo sobrio
- Comparativas visuales con gradientes sutiles
- Reportes con diseño profesional y elegante

### Sistema de Gestión:
- Formularios con glassmorphism corporativo
- Tablas con hover effects suaves
- Navegación con micro-interacciones profesionales

---

> **💡 TIP CORPORATIVO**: Estos prompts están diseñados para crear interfaces que inspiren confianza y profesionalismo en entornos corporativos, manteniendo un balance perfecto entre modernidad y sobriedad ejecutiva. El objetivo es transmitir solidez, competencia y liderazgo a través del diseño.
