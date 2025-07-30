
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('ReconsideracionTest_2025-07-30', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://localhost:8000');

    // Fill input field
    await page.fill('#username', 'andresrdrgz_');

    // Fill input field
    await page.fill('#password', 'Electro3_');

    // Click element
    await page.click('button[type="submit"]');

    // Click element
    await page.click('a[href="/workflow/"]');

    // Click element
    await page.click('a:has-text("Ver"), button:has-text("Ver")');

    // Click element
    await page.click('button:has-text("Ver Detalle"), a:has-text("Ver Detalle")');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/?pipeline=12');

    // Fill input field
    await page.fill('#username', 'andresrdrgz_');

    // Fill input field
    await page.fill('#password', 'Electro3_');

    // Click element
    await page.click('button[type="submit"]');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/?pipeline=12');

    // Click element
    await page.click('button:has-text("Ver Detalle")');

    // Click element
    await page.click('text=FLU-125');

    // Click element
    await page.click('tr[data-solicitud-id='125']"');

    // Click element
    await page.click('tr[data-solicitud-id='125']');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/solicitud/125/reconsideracion/solicitar/');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/?pipeline=12');

    // Click element
    await page.click('tr[data-solicitud-id='125']');

    // Take screenshot
    await page.screenshot({ path: 'reconsideracion_modal_test.png', { fullPage: true } });
});