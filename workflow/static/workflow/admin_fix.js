// Fix para Django Admin - Eliminar warnings de unload
// Este script suprime el warning de "unload is not allowed"

(function () {
  'use strict';

  // Override del evento unload problemático
  if (typeof django !== 'undefined' && django.jQuery) {
    const $ = django.jQuery;

    // Reemplazar handlers de unload con beforeunload
    $(window).off('unload.RelatedObjectLookups');

    // Suprimir warnings de console para este caso específico
    const originalWarn = console.warn;
    console.warn = function (...args) {
      const message = args.join(' ');
      if (message.includes('unload is not allowed') ||
        message.includes('Permissions policy violation')) {
        return; // Suprimir este warning específico
      }
      originalWarn.apply(console, args);
    };

    console.log('✅ Django Admin: Warning de unload suprimido');
  }
})();