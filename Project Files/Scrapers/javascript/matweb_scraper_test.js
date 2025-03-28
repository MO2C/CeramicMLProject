const puppeteer = require('puppeteer');
const fs = require('fs');

const BASE_URL = 'https://www.matweb.com/search/MaterialGroupSearch.aspx';

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    console.log('Navigating to MatWeb search page...');
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await new Promise(resolve => setTimeout(resolve, 5000)); // Ensure elements load

    // Click the second refractory ceramics category (updated selector using nth-child)
    await page.waitForSelector('a[class^="ctl00_ContentMain_ucMatGroupTree_msTreeView_0"]');
    const categories = await page.$$('a[class^="ctl00_ContentMain_ucMatGroupTree_msTreeView_0"]');
    if (categories.length > 1) {
        await categories[1].click();
    }
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Click the submit button
    await page.waitForSelector('input[name="ctl00$ContentMain$btnSubmit"]');
    await page.click('input[name="ctl00$ContentMain$btnSubmit"]');
    await page.waitForNavigation({ waitUntil: 'domcontentloaded' });

    // Select 200 items per page
    await page.waitForSelector('select[name="ctl00$ContentMain$UcSearchResults1$drpPageSize2"]');
    await page.select('select[name="ctl00$ContentMain$UcSearchResults1$drpPageSize2"]', '200');
    await page.waitForNavigation({ waitUntil: 'domcontentloaded' });

    let materials = [];
    let materialLinks = [];

    console.log('Extracting material links...');

    // Extract only one material link for testing
    let links = await page.$$eval('#tblResults tr', rows => {
        let link = rows.map(row => {
            let anchor = row.querySelector('td:nth-child(3) a');
            return anchor ? anchor.href : null;
        }).filter(href => href);
        return link.length > 0 ? [link[0]] : [];
    });

    materialLinks = links;
    console.log(`Found ${materialLinks.length} material link for testing.`);

    if (materialLinks.length > 0) {
        const link = materialLinks[0];
        console.log(`Scraping: ${link}`);
        await page.goto(link, { waitUntil: 'domcontentloaded' });
        await new Promise(resolve => setTimeout(resolve, 5000));

        let material = await page.evaluate(() => {
            let name = document.querySelector('table.tabledataformat.t_ableborder.tableloose.altrow th')?.innerText.trim() || 'No name available';
            let properties = {};
            let currentPropertyType = '';
            
            document.querySelectorAll('table:nth-of-type(2) tr').forEach(row => {
                if (row.querySelector('th') && !row.className) {
                    currentPropertyType = row.querySelector('th').innerText.trim();
                    if (!properties[currentPropertyType]) {
                        properties[currentPropertyType] = [];
                    }
                }
                if (row.classList.contains('datarowSeparator')) {
                    let cells = row.querySelectorAll('td');
                    let propertyName = cells[0].innerText.trim() || (properties[currentPropertyType].length > 0 ? properties[currentPropertyType][properties[currentPropertyType].length - 1].propertyName : '');
                    let metricValue = cells[1]?.innerText.trim() || '';
                    let englishValue = cells[2]?.innerText.trim() || '';
                    let comments = cells[3]?.innerText.trim() || '';
                    properties[currentPropertyType].push({ propertyName, metricValue, englishValue, comments });
                }
            });

            return { name, properties };
        });

        console.log(material);
        materials.push(material);
    }

    console.log('Scraping completed. Saving data...');
    fs.writeFileSync('refractory_ceramics_test.json', JSON.stringify(materials, null, 2));

    await browser.close();
    console.log('Data saved successfully!');
})();