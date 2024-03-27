import './base.cy'

describe('Email format verification', () => {
  it('Should give an error if the text entered isn\'t a valid email', () => {

    cy.goToRegistrantType()

    // Don't select anything, just click submit
    cy.get('.govuk-button#id_submit').click()

    // There should be an error
    cy.confirmProblem('Please select from one of the choices')

    // Correct
    cy.chooseRegistrantType(5)

    cy.checkPageTitleIncludes('What is your registrant’s organisation name?')
  })
})
