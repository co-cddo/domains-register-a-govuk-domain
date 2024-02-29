const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    experimentalStudio: true,
    baseUrl: 'http://0.0.0.0:8000/',
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
