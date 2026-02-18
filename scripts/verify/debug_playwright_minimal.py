import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Starting minimal test...")
    async with async_playwright() as p:
        print("Launching browser...")
        # Use simple launch first (not persistent)
        try:
             browser = await p.chromium.launch(headless=False)
             page = await browser.new_page()
             print("Navigating to Instagram...")
             await page.goto("https://www.instagram.com/")
             print("Page title:", await page.title())
             await asyncio.sleep(5)
             await browser.close()
             print("Minimal test success (launch)")
        except Exception as e:
             print(f"Minimal launch failed: {e}")

        # Now try persistent context like the class does
        print("\nTesting persistent context...")
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir="./test_instagram_debug_session",
                headless=False,
                args=[
                    '--disable-notifications',
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled'
                ],
                no_viewport=True
            )
            page = context.pages[0]
            print("Navigating to Instagram (persistent)...")
            await page.goto("https://www.instagram.com/")
            print("Page title:", await page.title())
            await asyncio.sleep(5)
            await context.close()
            print("Persistent test success")
        except Exception as e:
            print(f"Persistent launch failed: {e}")

if __name__ == "__main__":
    asyncio.run(run())
