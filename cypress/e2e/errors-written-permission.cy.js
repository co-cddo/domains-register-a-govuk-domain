import './base.cy'

describe('Error messages for the Exemption form', () => {
  it('warns if the user hasn\'t selected an option', () => {
    cy.goToWrittenPermission()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Does your registrant have proof of permission')

    // but display errors
    cy.confirmProblem('Please answer Yes or No')

    // this time make a choice
    cy.selectYesOrNo('written_permission', 'yes')

    // check we are on the next page
    cy.checkPageTitleIncludes('Upload evidence of permission to apply')

  })
})
