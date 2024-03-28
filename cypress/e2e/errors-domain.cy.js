import './base.cy'

describe('Error messages for domain form', () => {
  it('accepts valid domain names', () => {
    cy.goToDomain()
    cy.enterDomainName('dosac')
    cy.checkPageTitleIncludes('Can you confirm if the dosac.gov.uk domain name is correct?')
  })

  it('accepts valid domain names with hyphens', () => {
    cy.goToDomain()
    cy.enterDomainName('dos-ac')
    cy.checkPageTitleIncludes('Can you confirm if the dos-ac.gov.uk domain name is correct?')
  })

  it('accepts valid domain names when user has entered .gov.uk', () => {
    cy.goToDomain()
    cy.enterDomainName('dosac.gov.uk')
    cy.checkPageTitleIncludes('Can you confirm if the dosac.gov.uk domain name is correct?')
  })

  it('rejects invalid domain names', () => {
    cy.goToDomain()
    cy.get('.govuk-button#id_submit').click()
    cy.confirmProblem('This field is required')

    cy.goToDomain()
    cy.enterDomainName('dos.ac')
    cy.confirmProblem('Please enter a valid domain name')

    cy.enterDomainName('dos.ac.gov.uk')
    cy.confirmProblem('Please enter a valid domain name')

    cy.enterDomainName('DoSAC.gov.uk')
    cy.confirmProblem('Please enter a valid domain name')

    cy.enterDomainName('007.gov.uk')
    cy.confirmProblem('Please enter a valid domain name')

    cy.enterDomainName('-blah.gov.uk')
    cy.confirmProblem('Please enter a valid domain name')

    cy.enterDomainName('blah-.gov.uk')
    cy.confirmProblem('Please enter a valid domain name')

    cy.enterDomainName('b.gov.uk')
    cy.confirmProblem('Please enter a valid domain name')
  })

  it('rejects bad domain names but accepts valid retry', () => {
    cy.goToDomain()
    cy.enterDomainName('DoSAC.gov.uk')
    cy.confirmProblem('Please enter a valid domain name')
    cy.enterDomainName('dosac.gov.uk')
    cy.checkPageTitleIncludes('Can you confirm if the dosac.gov.uk domain name is correct?')
  })
})
