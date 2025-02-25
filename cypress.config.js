const { defineConfig } = require("cypress");

module.exports = defineConfig({
  viewportHeight: 1500,
  e2e: {
    baseUrl: 'http://localhost:8010/',
    experimentalCspAllowList: true,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
