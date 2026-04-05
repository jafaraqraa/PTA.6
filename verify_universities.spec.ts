import { test, expect } from '@playwright/test';

test('Super Admin can see Universities page', async ({ page }) => {
  // Login as super admin
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'admin@system.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/.*dashboard/);

  // Go to Universities page
  await page.click('a[href="/universities"]');
  await expect(page).toHaveURL(/.*universities/);

  await expect(page.locator('h1')).toContainText('Universities');
  await expect(page.locator('p')).toContainText('Manage institutional tenants and their domains.');

  // Check if universities are listed
  await expect(page.locator('text=An-Najah University')).toBeVisible();
  await expect(page.locator('text=Hebron University')).toBeVisible();

  await page.screenshot({ path: 'verification/screenshots/universities_page.png' });
});
