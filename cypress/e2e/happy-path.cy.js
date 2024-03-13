describe('Happy passes', () => {
  it('performs a full transaction', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('select.govuk-select').should('exist')

    cy.get('select.govuk-select').select('WeRegister')

    cy.get('.govuk-button#id_submit').click()


  })
})
