describe('Email format verification', () => {
  it('Should give an error if the text entered isn\'t a valid email', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('#id_organisations_choice').type('WeRegister')
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'What is your email address?')

    // although email addresses are checked by the browser, we can't expect all
    // browsers to do so, so we do need to check server-side
    cy.get('.govuk-input').type('a@b.c') // Somehow Chrome allows this one
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'What is your email address?')
    cy.get('#error-summary-title').should('include.text', 'There is a problem')
    cy.get('#id_registrant_email_address_1_error').should('include.text', 'Please enter a valid email address')

    cy.get('.govuk-input').clear().type('a@b.com')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Which of the following best describes your registrant\'s organisation?')

  })
})
