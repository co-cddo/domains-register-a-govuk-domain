import './base.cy'

describe('Don\'t allow breaking the flow', () => {

  it('Sends you to the start if you join in the middle', () => {
    cy.visit('http://0.0.0.0:8000/registrant_type_fail')

    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.url().should('be.equal', 'http://0.0.0.0:8000/')
  })


  it('Sends you to the start if you post data with no CSRF token', () => {
    cy.visit({
        url: "http://0.0.0.0:8000/email",
        method: "POST",
        body: {
          registrant_email_address: "example@example.com"
          // No CSRF token
        }
    });

    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.url().should('be.equal', 'http://0.0.0.0:8000/')
  })


  it('Sends you to the start if you post data with a random CSRF token', () => {
    cy.visit({
        url: "http://0.0.0.0:8000/email",
        method: "POST",
        body: {
          registrant_email_address: "example@example.com",
          csrfmiddlewaretoken: "eLqwO7i5BCusJsqUD7EWkkGKSt8Ztu63X8Lkf0x5OF8a3xAh8Dpr0joJsuELlX0i" // pragma: allowlist secret
        }
    });

    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.url().should('be.equal', 'http://0.0.0.0:8000/')
  })

})
