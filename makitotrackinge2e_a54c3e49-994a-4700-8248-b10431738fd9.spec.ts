
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('MakitoTrackingE2E_2025-07-31', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/makito-tracking/');

    // Fill input field
    await page.fill('input[name="username"]', 'andresrdrgz_');

    // Fill input field
    await page.fill('input[name="password"]', 'Electro3_');

    // Click element
    await page.click('button[type="submit"]');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/makito-tracking/');

    // Click element
    await page.click('button:has-text("Nueva solicitud")');

    // Take screenshot
    await page.screenshot({ path: 'nueva-solicitud-modal-opened.png' });

    // Click element
    await page.click('.service-option[data-type="apc"]');

    // Take screenshot
    await page.screenshot({ path: 'apc-service-selected.png' });

    // Click element
    await page.click('.solicitud-item[data-solicitud-id="130"]');

    // Take screenshot
    await page.screenshot({ path: 'solicitud-selected.png' });

    // Click element
    await page.click('#continuarValidacionBtn');

    // Take screenshot
    await page.screenshot({ path: 'validation-form-displayed.png' });

    // Select option
    await page.selectOption('#apcTipoDocumento', 'cedula');

    // Fill input field
    await page.fill('#apcNumeroDocumento', '8-123-456');

    // Take screenshot
    await page.screenshot({ path: 'validation-form-filled.png' });

    // Take screenshot
    await page.screenshot({ path: 'buttons-fixed.png' });

    // Click element
    await page.click('#procesarSolicitudBtn');

    // Take screenshot
    await page.screenshot({ path: 'procesar-clicked.png' });

    // Click element
    await page.click('#volverSolicitudesBtn');

    // Take screenshot
    await page.screenshot({ path: 'volver-clicked.png' });

    // Click element
    await page.click('.service-option[data-type="sura"]');

    // Click element
    await page.click('.solicitud-item[data-solicitud-id="130"]');

    // Click element
    await page.click('#continuarValidacionBtn');

    // Take screenshot
    await page.screenshot({ path: 'sura-validation-form.png' });

    // Click element
    await page.click('.btn-close');

    // Click element
    await page.click('#nuevaSolicitudModal .btn-close');
});