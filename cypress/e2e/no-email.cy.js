import './base.cy'

describe('Check if user entered an email', () => {
  it('Complains when no email is entered', () => {

    cy.goToRegistrarEmail()

    // Don't type anything, just click on the button
    cy.get('.govuk-button#id_submit').click()

    // There should be an error
    cy.get('#error-summary-title').should('exist')
    cy.get('#error-summary-title').should('include.text', 'There is a problem')
    cy.get('.govuk-error-summary__list').should('include.text', 'This field is required')

    // Retrying with a correct email
    cy.get('.govuk-input').type('something@some.gov.uk')
    cy.get('.govuk-button#id_submit').click()

    // No error message this time
    cy.get('#error-summary-title').should('not.exist')
  })
})
