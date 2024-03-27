import './base.cy'

describe('Email format verification', () => {
  it('Should give an error if the text entered isn\'t a valid email', () => {

    cy.goToRegistrarEmail()

    // although email addresses are checked by the browser, we can't expect all
    // browsers to do so, so we do need to check server-side
    cy.typeInEmail('a@b.c') // Somehow Chrome allows this one
    cy.confirmProblem('Please enter a valid email address')

    // Trying a correct one
    cy.typeInEmail('a@b.com')
    cy.checkPageTitleIncludes('Which of the following best describes your registrant\'s organisation?')

  })
})
