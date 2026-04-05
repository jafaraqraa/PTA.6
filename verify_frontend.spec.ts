import { test, expect } from '@playwright/test';

test.describe('PTA Simulator RBAC & Dashboard Verification', () => {

  test('Super Admin sees full management navigation and stats', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', 'admin@system.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    await page.waitForURL('**/dashboard');

    // Check Sidebar for Super Admin items
    await expect(page.getByRole('link', { name: 'Universities' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Subscriptions' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Users' })).toBeVisible();

    // Check Stats
    await expect(page.getByText('Total Universities')).toBeVisible();
    await expect(page.getByText('Total Users')).toBeVisible();

    // Navigate to Universities
    await page.click('text=Universities');
    await page.waitForURL('**/universities');
    await expect(page.getByText('An-Najah University')).toBeVisible();
  });

  test('University Admin sees restricted navigation and stats', async ({ page }) => {
    await page.goto('http://najah.localhost:5173/login');
    await page.fill('input[type="email"]', 'admin@najah.com');
    await page.fill('input[type="password"]', '123456');
    await page.click('button[type="submit"]');

    await page.waitForURL('**/dashboard');

    // Check Sidebar - should NOT see Universities/Subscriptions
    await expect(page.getByRole('link', { name: 'Universities' })).not.toBeVisible();
    await expect(page.getByRole('link', { name: 'Subscriptions' })).not.toBeVisible();
    await expect(page.getByRole('link', { name: 'Users' })).toBeVisible();

    // Check Stats
    await expect(page.getByText('Total Students')).toBeVisible();
    await expect(page.getByText('Lab Admins')).toBeVisible();

    // Try unauthorized access to Universities
    await page.goto('http://najah.localhost:5173/universities');
    await expect(page.url()).toContain('/unauthorized');
  });

  test('Student sees dashboard and simulator but no management', async ({ page }) => {
    await page.goto('http://najah.localhost:5173/login');
    await page.fill('input[type="email"]', 'student@najah.com');
    await page.fill('input[type="password"]', '123456');
    await page.click('button[type="submit"]');

    await page.waitForURL('**/dashboard');

    // Check Sidebar - should only see Dashboard, Sessions, Profile
    await expect(page.getByRole('link', { name: 'Users' })).not.toBeVisible();
    await expect(page.getByRole('link', { name: 'Universities' })).not.toBeVisible();

    // Check Launch Simulator button
    await expect(page.getByRole('link', { name: 'Launch Simulator' })).toBeVisible();

    // Try unauthorized access to Users
    await page.goto('http://najah.localhost:5173/users');
    await expect(page.url()).toContain('/unauthorized');
  });
});
