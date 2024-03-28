import './base.cy'

describe('Error messages for the domain purpose form', () => {
  it('warns if the user hasn\'t selected an option', () => {
    cy.goToDomainPurpose()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')

    // but display errors
    cy.confirmProblem('Please select from one of the choices')

    // this time make a choice
    cy.chooseDomainPurpose(1)

    // check we are on the next page
    cy.checkPageTitleIncludes('Does your registrant have an exemption')

  })
})
