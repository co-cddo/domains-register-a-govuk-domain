describe('Email format verification', () => {
  it('Should give an error if the text entered isn\'t a valid email', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('#id_organisations_choice').type('WeRegister')
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'What is your email address?')

    cy.get('.govuk-input').type('a@b.com')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Which of the following best describes your registrant\'s organisation?')

    cy.get('.govuk-button#id_submit').click()

    // There should be an error
    cy.get('#error-summary-title').should('exist')
    cy.get('#error-summary-title').should('include.text', 'There is a problem')
    cy.get('.govuk-error-summary__list').should('include.text', 'Please select from one of the choices')

    cy.get('#id_registrant_type_5').click()
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'What is your registrant’s organisation name?')
  })
})
