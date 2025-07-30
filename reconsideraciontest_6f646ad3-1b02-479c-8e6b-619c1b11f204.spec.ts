
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('ReconsideracionTest_2025-07-30', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://127.0.0.1:8000');

    // Fill input field
    await page.fill('input[name="username"]', 'andresrdrgz_');

    // Fill input field
    await page.fill('input[name="password"]', 'Electro3_');

    // Click element
    await page.click('button[type="submit"]');

    // Click element
    await page.click('a[href*="workflow"]');

    // Click element
    await page.click('tr:has-text('FLU-125') .btn:has-text('Ver')');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/?pipeline=12');

    // Click element
    await page.click('#reconsideracion-tab');

    // Click element
    await page.click('tr[data-codigo="FLU-125"]');

    // Click element
    await page.click('tr[data-solicitud-id="125"]');

    // Click element
    await page.click('#reconsideracion-tab');

    // Click element
    await page.click('#reconsideracion-tab');

    // Click element
    await page.click('#modalBtnReconsideracion');

    // Take screenshot
    await page.screenshot({ path: 'reconsideracion_tab_implementation_test.png' });
});