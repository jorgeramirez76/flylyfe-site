const {defineConfig,devices}=require('@playwright/test');
module.exports=defineConfig({
  testDir:'./tests',fullyParallel:true,workers:2,retries:process.env.CI?1:0,
  reporter:[['list'],['html',{open:'never'}]],
  use:{baseURL:'http://127.0.0.1:8765',trace:'retain-on-failure',channel:process.env.PLAYWRIGHT_CHANNEL||undefined},
  projects:[{name:'desktop',use:{viewport:{width:1440,height:900}}},{name:'mobile',use:{...devices['iPhone 13'],defaultBrowserType:'chromium'}}],
  webServer:{command:'python3 tools/serve_preview.py',url:'http://127.0.0.1:8765',reuseExistingServer:!process.env.CI}
});
