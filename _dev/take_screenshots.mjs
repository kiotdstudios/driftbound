import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const shots = [
  { w: 1920, h: 1080, name: 'hud_1920x1080.png' },
  { w: 2560, h: 1440, name: 'hud_2560x1440.png' },
  { w: 1366, h: 768,  name: 'hud_1366x768.png'  },
];
for (const { w, h, name } of shots) {
  const page = await browser.newPage();
  await page.setViewportSize({ width: w, height: h });
  await page.goto('http://localhost:8420/driftbound_flight_test.html', { waitUntil: 'load' });
  await page.waitForTimeout(800);

  // Click PLAY SOLO to bypass lobby
  const soloBtn = page.locator('text=PLAY SOLO');
  if (await soloBtn.count() > 0) {
    await soloBtn.click();
    console.log(`Clicked PLAY SOLO for ${name}`);
  } else {
    // Try pressing Escape as fallback
    await page.keyboard.press('Escape');
    console.log(`Pressed Escape for ${name}`);
  }

  // Wait for game loop to run, stars to render, etc.
  await page.waitForTimeout(2500);

  const outPath = `C:\\Users\\diepowel\\Documents\\DRIFTBOUND\\_dev\\${name}`;
  await page.screenshot({ path: outPath });
  console.log(`Captured: ${name} (${w}x${h})`);
  await page.close();
}
await browser.close();
console.log('Done');
