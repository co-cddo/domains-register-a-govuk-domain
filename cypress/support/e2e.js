// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')


beforeEach(() => {
  // Intercept any breach of CSP rules
  cy.intercept(
    'POST', '/csp-report',
    req => req.reply(200, { message: 'mocked response' })
  ).as('cspReport')
});

afterEach(() => {
  // There should have been no CSP breaches
  cy.get('@cspReport.all').should('have.length', 0);
});
