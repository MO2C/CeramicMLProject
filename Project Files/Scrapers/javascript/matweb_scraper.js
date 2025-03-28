const puppeteer = require('puppeteer');
const fs = require('fs');

const BASE_URL = 'https://www.matweb.com/search/MaterialGroupSearch.aspx';
const RANGE_START = 0; // Start index for scraping
const RANGE_END = 5; // End index for scraping

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    console.log('Navigating to MatWeb search page...');
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await new Promise(resolve => setTimeout(resolve, 5000)); // Ensure elements load

    // Click the main category
    console.log('Clicking main category...');
    await page.waitForSelector('#ctl00_ContentMain_ucMatGroupTree_msTreeViewn1');
    await page.click('#ctl00_ContentMain_ucMatGroupTree_msTreeViewn1');

    console.log('Waiting for subcategory to expand...');
    await page.waitForSelector('#ctl00_ContentMain_ucMatGroupTree_msTreeViewn1Nodes', { visible: true });

    // Click the second subcategory
    console.log('Clicking second subcategory...');
    await page.waitForSelector('#ctl00_ContentMain_ucMatGroupTree_msTreeViewt9');
    await page.click('#ctl00_ContentMain_ucMatGroupTree_msTreeViewt9');

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

    while (true) {
        console.log('Extracting material links...');

        // Extract links from the table
        let links = await page.$$eval('#tblResults tr', rows => {
            return rows.map(row => {
                let link = row.querySelector('td:nth-child(3) a');
                return link ? link.href : null;
            }).filter(href => href);
        });

        materialLinks = materialLinks.concat(links);
        console.log(`Found ${links.length} new links, total: ${materialLinks.length}`);

        if (materialLinks.length >= RANGE_END) break;

        // Check if next button is disabled
        const nextButton = await page.$('a#ctl00_ContentMain_UcSearchResults1_lnkNextPage2');
        if (nextButton) {
            const isDisabled = await page.evaluate(button => button.hasAttribute('disabled'), nextButton);
            if (isDisabled) break;
            await Promise.all([
                nextButton.click(),
                page.waitForNavigation({ waitUntil: 'domcontentloaded' })
            ]);
        } else {
            break;
        }
    }

    console.log(`Total materials found: ${materialLinks.length}`);

    for (const link of materialLinks.slice(RANGE_START, RANGE_END)) {
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
    fs.writeFileSync('refractory_ceramics.json', JSON.stringify(materials, null, 2));

    await browser.close();
    console.log('Data saved successfully!');
})();
