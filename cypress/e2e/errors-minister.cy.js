import './base.cy'

describe('Error messages for the Minister form', () => {
  it('warns if the user hasn\'t selected an option', () => {
    cy.goToMinister()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Has a central government minister requested the something-pc.gov.uk domain name?')

    // but display errors
    cy.confirmProblem('Please answer Yes or No')

    // this time make a choice
    cy.selectYesOrNo('minister', 'yes')

    // check we are on the next page
    cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
  })
})
