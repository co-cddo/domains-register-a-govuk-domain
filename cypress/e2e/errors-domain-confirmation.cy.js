import './base.cy'

describe('Error messages for domain confirmation form', () => {
  it('complains when no choice was made', () => {
    cy.goToDomainViaRoute(3)
    cy.enterDomainName('dosac')
    cy.checkPageTitleIncludes('Is dosac.gov.uk the correct domain name?')

    // just click, don't chose
    cy.get('.govuk-button#id_submit').click()
    cy.confirmProblem('Select yes if the requested .gov.uk domain name is correct')

    // try again and succeed
    cy.selectYesOrNo('domain_confirmation', 'yes')
    cy.checkPageTitleIncludes('Registrant details')
  })
})
