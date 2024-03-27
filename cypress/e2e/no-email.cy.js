import './base.cy'

describe('Check if user entered an email', () => {
  it('Complains when no email is entered', () => {

    cy.goToRegistrarEmail()

    // Don't type anything, just click on the button
    cy.get('.govuk-button#id_submit').click()

    // There should be an error
    cy.confirmProblem('This field is required')

    // Retrying with a correct email
    cy.typeInEmail('something@some.gov.uk')

    // No errors, move to next page
    cy.checkPageTitleIncludes('Which of the following best describes your registrant\'s organisation?')
  })
})
