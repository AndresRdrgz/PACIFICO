
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('NotasRecordatorios_2025-07-29', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://127.0.0.1:8000');

    // Take screenshot
    await page.screenshot({ path: 'initial_page.png' });

    // Fill input field
    await page.fill('input[name="username"]', 'andresrdrgz_');

    // Fill input field
    await page.fill('input[name="password"]', 'Electro3_');

    // Click element
    await page.click('button[type="submit"]');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/');

    // Take screenshot
    await page.screenshot({ path: 'negocios_page.png' });

    // Click element
    await page.click('a[href="#notas"]');

    // Click element
    await page.click('#notas-tab');

    // Click element
    await page.click('button:has-text('Flujo de Consulta de Auto')');

    // Click element
    await page.click('a:has-text('Ver en Tabla')');

    // Take screenshot
    await page.screenshot({ path: 'table_view.png' });

    // Click element
    await page.click('tr:has-text('FLU-120')');

    // Click element
    await page.click('#notas-tab');

    // Take screenshot
    await page.screenshot({ path: 'notes_tab_opened.png' });

    // Click element
    await page.click('#btnNuevaNota');

    // Take screenshot
    await page.screenshot({ path: 'note_creation_form.png' });

    // Fill input field
    await page.fill('#tituloNota', 'Test Note - Automated Testing');

    // Fill input field
    await page.fill('#contenidoNota', 'This is a test note created via automated testing with Playwright to verify the notes and reminders functionality is working correctly.');

    // Wait for response
    const create_note_responseResponse = page.waitForResponse('**/workflow/api/notas-recordatorios/120/crear/**');

    // Click element
    await page.click('button:has-text('Guardar')');

    // Assert response
    expect(create_note_responseResponse.ok()).toBeTruthy();

    // Take screenshot
    await page.screenshot({ path: 'note_created_success.png' });

    // Click element
    await page.click('#btnNuevaNota');

    // Select option
    await page.selectOption('#tipoNota', 'recordatorio');

    // Fill input field
    await page.fill('#tituloNota', 'Test Reminder - Follow up with client');

    // Fill input field
    await page.fill('#contenidoNota', 'Automated test reminder: Follow up with client regarding their loan application status and any additional documentation needed.');

    // Fill input field
    await page.fill('#fechaVencimiento', '2025-07-30T10:00');

    // Wait for response
    const create_reminder_responseResponse = page.waitForResponse('**/workflow/api/notas-recordatorios/120/crear/**');

    // Click element
    await page.click('button:has-text('Guardar')');

    // Assert response
    expect(create_reminder_responseResponse.ok()).toBeTruthy();

    // Take screenshot
    await page.screenshot({ path: 'reminder_error_state.png' });
});