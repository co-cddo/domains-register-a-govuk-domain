import './base.cy'

describe('Error messages for the Exemption form', () => {
  it('warns if the user hasn\'t selected an option', () => {
    cy.goToExemption()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Does your registrant have an exemption')

    // but display errors
    cy.confirmProblem('Select yes if your registrant has permission to apply for a .gov.uk domain name')

    // this time make a choice
    cy.selectYesOrNo('exemption', 'yes')

    // check we are on the next page
    cy.checkPageTitleIncludes('Upload evidence of the exemption')

  })
})
