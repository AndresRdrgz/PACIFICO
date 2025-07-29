
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('NegociosPipelineRedirect_2025-07-29', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/');

    // Fill input field
    await page.fill('#username', 'admin');

    // Fill input field
    await page.fill('#password', 'admin');

    // Click element
    await page.click('button[type="submit"]');

    // Fill input field
    await page.fill('#username', 'andresrdrgz_');

    // Fill input field
    await page.fill('#password', 'Electro3_');

    // Click element
    await page.click('button[type="submit"]');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/');

    // Click element
    await page.click('a[href="?pipeline=12&view=table"]');

    // Click element
    await page.click('#dropdownPipeline');

    // Click element
    await page.click('a[href="?pipeline=12&view=table"]');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/workflow/negocios/');
});