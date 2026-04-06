
import { test, expect } from '@playwright/test';

test.use({
  baseURL: 'http://localhost:5173',
});

test('Lab Admin Dashboard and Student Management', async ({ page }) => {
  // 1. Login as Lab Admin
  await page.goto('/login');
  await page.fill('input[type="email"]', 'lab@najah.com');
  await page.fill('input[type="password"]', '123456');
  await page.click('button[type="submit"]');

  // 2. Verify Dashboard
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('h1')).toContainText('Welcome back, lab', { ignoreCase: true });
  await expect(page.getByText('Assigned Students')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Manage Students' })).toBeVisible();

  // 3. Navigate to Students Page via Sidebar
  await page.getByRole('link', { name: 'Students', exact: true }).click();
  await expect(page).toHaveURL('/users');
  await expect(page.locator('h1')).toContainText('Student Management');

  // 4. Verify "Add Student" button exists
  const addStudentBtn = page.getByRole('button', { name: 'Add Student' });
  await expect(addStudentBtn).toBeVisible();

  // 5. Open Modal
  await addStudentBtn.click();
  await expect(page.getByText('Add User')).toBeVisible(); // The modal title is still 'Add User' but button was 'Add Student'

  // 6. Verify Role is restricted to Student
  const roleSelect = page.locator('select').first();
  const options = await roleSelect.locator('option').allInnerTexts();
  console.log('Available roles in modal:', options);
  expect(options).toEqual(['STUDENT']);

  // Take a screenshot of the dashboard
  await page.goto('/dashboard');
  await page.screenshot({ path: 'verification/screenshots/lab_admin_dashboard_final.png' });

  // Take a screenshot of the student management page
  await page.goto('/users');
  await page.screenshot({ path: 'verification/screenshots/lab_admin_student_management.png' });
});
