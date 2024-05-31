import './base.cy'

describe('Error messages for registrant type form', () => {
  it('warns if the user hasn\'t selected an option', () => {
    cy.goToRegistrantType()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Who is this domain name for?')

    // but display errors
    cy.confirmProblem('Select the registrant\'s organisation type')

    // this time make a choice
    cy.chooseRegistrantType(1) // Central government -> Route 2

    // check we are on the next page
    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')

  })
})
