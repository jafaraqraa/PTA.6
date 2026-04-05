import { test, expect } from '@playwright/test';

test('Super Admin can create and edit a university', async ({ page }) => {
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'admin@system.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');

  await page.click('a[href="/universities"]');
  await page.click('button:has-text("Add University")');

  await page.fill('input[placeholder="e.g. An-Najah University"]', 'Test University');
  await page.fill('input[placeholder="e.g. najah"]', 'testuni');
  await page.click('button:has-text("Create University")');

  await expect(page.locator('text=Test University')).toBeVisible();

  // Edit
  await page.click('.card:has-text("Test University") button:has(svg)');
  await page.fill('input[value="Test University"]', 'Updated University');
  await page.click('button:has-text("Save Changes")');

  await expect(page.locator('text=Updated University')).toBeVisible();
  await page.screenshot({ path: 'verification/screenshots/university_management.png' });
});

test('Super Admin can manage users', async ({ page }) => {
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'admin@system.com');
  await page.fill('input[type="password"]', 'admin123');
  await page.click('button[type="submit"]');

  await page.click('a[href="/users"]');
  await page.click('button:has-text("Add User")');

  await page.fill('input[placeholder="e.g. John Doe"]', 'New Student');
  await page.fill('input[placeholder="name@email.com"]', 'newstudent@test.com');
  await page.fill('input[placeholder="••••••••"]', 'password123');
  await page.selectOption('select', 'student');
  await page.click('button:has-text("Create User")');

  await expect(page.locator('text=New Student')).toBeVisible();
  await page.screenshot({ path: 'verification/screenshots/user_management.png' });
});
