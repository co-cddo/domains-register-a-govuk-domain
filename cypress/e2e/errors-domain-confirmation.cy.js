import './base.cy'

describe('Error messages for domain confirmation form', () => {
  it('complains when no choice was made', () => {
    cy.goToDomain()
    cy.enterDomainName('dosac')
    cy.checkPageTitleIncludes('Can you confirm if the dosac.gov.uk domain name is correct?')

    // just click, don't chose
    cy.get('.govuk-button#id_submit').click()
    cy.confirmProblem('Please answer Yes or No')

    // try again and succeed
    cy.selectYesOrNo('domain_confirmation', 'yes')
    cy.checkPageTitleIncludes('Registrant details')
  })
})
