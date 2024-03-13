describe('Registrar no-select error', () => {
  it('Correctly prints a warning if the user hasn\'t selected a registrar', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('.govuk-button#id_submit').click()


    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('#error-summary-title').should('include.text', 'There is a problem')
    cy.get('#id_organisations_choice_1_error').should('include.text', 'This field is required')

    cy.get('select.govuk-select').select('WeRegister')
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'What is your email address?')
  })
})
