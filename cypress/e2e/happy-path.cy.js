import './base.cy'

describe('Happy passes', () => {
  it('performs a full transaction', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('select.govuk-select').should('exist')

    cy.get('#id_organisations_choice').type('WeRegister')

    cy.get('.govuk-button#id_submit').click()


  })
})
