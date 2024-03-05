describe('Registrar no-select error', () => {
  it('Correctly prints a warning if the user hasn\'t selected a registrar', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('.govuk-button').click()


    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('#error-summary-title').should('include.text', 'There is a problem')
    cy.get('#id_organisations_choice_1_error').should('include.text', 'Please select an item from the list')

    cy.get('select.govuk-select').select('34SP.com')
    cy.get('.govuk-button').click()

    cy.get('h1').should('include.text', 'What is your email address?')
  })
})
