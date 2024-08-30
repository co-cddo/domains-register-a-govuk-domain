import './base.cy'

describe('Cookie banner', () => {

  beforeEach(() => {
    cy.clearCookie('cookies_accepted')
    cy.clearCookie('cookies_preference_set')
    cy.start()
  })

  Cypress.Commands.add('acceptCookies', () => {
    cy.get('.govuk-cookie-banner button').eq(0).click()
    cy.get('.govuk-cookie-banner button').eq(2).click()
    cy.getCookie('cookies_preference_set').should('have.property', 'value', 'true')
    cy.getCookie('cookies_accepted').should('have.property', 'value', 'true')
  })

  Cypress.Commands.add('refuseCookies', () => {
    cy.get('.govuk-cookie-banner button').eq(1).click()
    cy.get('.govuk-cookie-banner button').eq(2).click()
    cy.getCookie('cookies_preference_set').should('have.property', 'value', 'true')
    cy.getCookie('cookies_accepted').should('have.property', 'value', 'false')
  })

  it('shows when user hasn\'t visited before', () => {
    cy.get('.govuk-cookie-banner button').eq(0).should('include.text', 'Accept analytics cookies')
    cy.get('.govuk-cookie-banner button').eq(1).should('include.text', 'Reject analytics cookies')
    cy.get('a').should('include.text', 'View cookies')
  })

  it('hides the banner when user has made their choice', () => {
    cy.get('.govuk-cookie-banner button').eq(0).click()
    cy.get('.govuk-cookie-banner').should('include.text', 'You have accepted additional cookies')
    cy.get('.govuk-cookie-banner button').should('include.text', 'Hide this message')
    cy.get('.govuk-cookie-banner button').eq(2).click()
    cy.get('.govuk-cookie-banner').should('not.be.visible')
  })

  it('doesn\'t show the banner again after the user chooses and starts', () => {
    cy.acceptCookies();
    cy.get('a[role=button]').should('include.text', 'Get approval').click()
    cy.get('.govuk-cookie-banner').should('not.be.visible')
  })

  it('shows the banner again if the user hasn\'t chosen', () => {
    cy.get('a[role=button]').should('include.text', 'Get approval').click()
    cy.get('.govuk-cookie-banner').should('be.visible')
  })

  it('does not load the GTM code if cookies are refused', () => {
    cy.refuseCookies()
    cy.get('#replaced-gtm-snippet').should('not.exist');
  })

  it('Loads the GTM code if cookies are refused', () => {
    cy.acceptCookies();
    cy.get('#replaced-gtm-snippet').should('exist');
  })

  it('lets the user change their mind from accept to reject', () => {
    cy.acceptCookies()
    cy.visit('/cookies')
    cy.get('#replaced-gtm-snippet').should('exist')
    cy.get('#use-cookies').should('be.checked')
    cy.get('#no-cookies').should('not.be.checked')
    cy.get('#no-cookies').click()
    cy.get('#save-cookies').click()
    cy.getCookie('cookies_preference_set').should('have.property', 'value', 'true')
    cy.getCookie('cookies_accepted').should('have.property', 'value', 'false')
    cy.visit('/')
    cy.get('#replaced-gtm-snippet').should('not.exist')
  })

  it('lets the user change their mind from reject to accept', () => {
    cy.refuseCookies()
    cy.visit('/cookies')
    cy.get('#replaced-gtm-snippet').should('not.exist')
    cy.get('#use-cookies').should('not.be.checked')
    cy.get('#no-cookies').should('be.checked')
    cy.get('#use-cookies').click()
    cy.get('#save-cookies').click()
    cy.getCookie('cookies_preference_set').should('have.property', 'value', 'true')
    cy.getCookie('cookies_accepted').should('have.property', 'value', 'true')
    cy.visit('/')
    cy.get('#replaced-gtm-snippet').should('exist')
  })
})
