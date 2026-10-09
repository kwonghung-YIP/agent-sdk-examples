import { test, expect, Locator, Page } from '@playwright/test';

test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    const path = testInfo.outputPath('failure.png');
    await page.screenshot({ path, fullPage: true });
    await testInfo.attach('failure-screenshot', {
      path,
      contentType: 'image/png',
    });
  }
});

test('has title', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Playwright/);
});

test('get started link', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Click the get started link.
  await page.getByRole('link', { name: 'Get started' }).click();

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
});

test('Dell 1st 4K monitor', async({ page }) => {
  await page.goto('https://www.dell.com/en-gb/shop/all-monitors/sac/monitors/all-monitors/appref=4k-uhd-3840-x-2160-screen-resolution');
  await page.getByRole('button', { name: 'Accept All' }).click();

  //const articles = await page.getByRole('article');
  // 
  // DOM Selector Reference:
  // https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Selection_and_traversal_on_the_DOM_tree
  const all_articles = await page.locator('article.ps-stack');
  const count = await all_articles.count();

  expect(count).toEqual(12);

  const article = await all_articles.nth(0);
  const product_id = await article.getAttribute("id");

  expect(product_id).toEqual("s2725qc_monitor");

  const product_link = await article.locator('div.ps-title-container>h3.ps-title>a');
  const link = await product_link.getAttribute('href');
  const model = await product_link.innerText();
  
  expect(link).toEqual("https://www.dell.com/en-gb/shop/monitors/apd/dell-27-plus-4k-usb-c-monitor-s2725qc/s2725qc_monitor/-");
  expect(model).toEqual("Dell 27 Plus 4K USB-C Monitor - S2725QC");

  const price_container = await article.locator('section.ps-show-hide').locator('span.ps-dell-price-amount');
  const price = await price_container.innerText();
  
  expect(price).toEqual("£329.00");
});

const BASE_URL = "https://www.dell.com/en-gb/shop/all-monitors/sac/monitors/all-monitors";

test('Dell 4K monitor', async({ page }) => {
  //await page.goto('https://www.dell.com/en-gb/shop/all-monitors/sac/monitors/all-monitors/appref=4k-uhd-3840-x-2160-screen-resolution');
  await page.goto(`${BASE_URL}`, { timeout: 1000*60 });
  //await page.keyboard.press('End');

  await page.getByRole('button', { name: 'Accept All' }).click();
  
  let pageNo = 1;
  await page.screenshot({ type: 'png', fullPage: true, path: `screenshots/monitor-p${pageNo}.png`});

  let monitors: object[] = [];
  let hasNextPage = true;
  while (hasNextPage) {
    const result = await extract_monitors_in_page(page);
    monitors = monitors.concat(result.monitors);

    hasNextPage = result.hasNextPage;
    if (hasNextPage) {
      pageNo++;
      await page.waitForTimeout(1000*1);
      //await result.nextPage.click();
      console.log(`goto page:${pageNo}`);
      await page.goto(`${BASE_URL}?page=${pageNo}`, { timeout: 1000*60 });
      //await page.keyboard.press('End');
      await page.screenshot({ type: 'png', fullPage: true, path: `screenshots/monitor-p${pageNo}.png`});
    }
    //hasNextPage = false;
  }
  console.info(JSON.stringify(monitors));

  expect(monitors.length).toBe(88);
});

const extract_monitors_in_page = async( page: Page ) => {
  const articles = await page.locator('article.ps-stack');
  const count = await articles.count();
  
  const page_container = await page.locator('#ar-pagination-container');
  const nextPage = await page_container.getByLabel('Next Page');
  const pageno = await page_container.locator('input[type="text"]').inputValue();
  const hasNextPage = await nextPage.isEnabled();

  console.info(pageno);

  const monitors = []
  for (let i=0; i<count; i++) {
    const article = await articles.nth(i);

    await expect(article).toHaveAttribute("id");
    const id = await article.getAttribute("id");

    //await article.screenshot({ type: 'png', path: `screenshots/monitor-p${pageno}-${id}.png`});

    const link = await article.locator('div.ps-title-container>h3.ps-title>a');
    await expect(link).toHaveAttribute('href');
    const href = await link.getAttribute('href');
    await expect(link).toContainText(/.*/);
    const model = await link.innerText();

    const price_span = await article.locator('section.ps-show-hide').locator('span.ps-dell-price-amount');
    await expect(price_span).toContainText(/£[0-9.]+/);
    const price = await price_span.innerText();

    monitors.push({
      id,
      link:href,
      model,
      price,
      pageno,
    });
  }
  return {
    hasNextPage,
    nextPage,
    monitors,
  };
}