describe('Happy passes', () => {
  it('performs a full transaction', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('select.govuk-select').should('exist')

    cy.get('select.govuk-select').select('34SP.com')

    cy.get('.govuk-button').click()


  })
})
