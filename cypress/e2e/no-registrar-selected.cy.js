import './base.cy'

describe('Registrar no-select error', () => {
  it('Correctly prints a warning if the user hasn\'t selected a registrar', () => {
    cy.goToRegistrar()

    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('.govuk-button#id_submit').click()


    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.confirmProblem('This field is required')

    cy.chooseRegistrar('WeRegister')
    cy.checkPageTitleIncludes('What is your email address?')
  })
})
