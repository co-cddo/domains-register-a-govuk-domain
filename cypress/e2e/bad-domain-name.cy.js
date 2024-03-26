import './base.cy'

describe('Bad domain names', () => {
  it('accepts valid domain names', () => {
    cy.goToDomain()
    cy.enterDomainName('dosac')
    cy.checkPageTitleIncludes('Has a central government minister requested the dosac.gov.uk domain name?')
  })

  it('accepts valid domain names with hyphens', () => {
    cy.goToDomain()
    cy.enterDomainName('dos-ac')
    cy.checkPageTitleIncludes('Has a central government minister requested the dos-ac.gov.uk domain name?')
  })

  it('accepts valid domain names when user has entered .gov.uk', () => {
    cy.goToDomain()
    cy.enterDomainName('dosac.gov.uk')
    cy.checkPageTitleIncludes('Has a central government minister requested the dosac.gov.uk domain name?')
  })

  it('rejects invalid domain names', () => {
    cy.goToDomain()
    cy.enterDomainName('dos.ac')
    cy.confirmProblem()

    cy.enterDomainName('dos.ac.gov.uk')
    cy.confirmProblem()

    cy.enterDomainName('DoSAC.gov.uk')
    cy.confirmProblem()

    cy.enterDomainName('007.gov.uk')
    cy.confirmProblem()

    cy.enterDomainName('-blah.gov.uk')
    cy.confirmProblem()

    cy.enterDomainName('blah-.gov.uk')
    cy.confirmProblem()

    cy.enterDomainName('b.gov.uk')
    cy.confirmProblem()
  })

  it('rejects bad domain names but accepts valid retry', () => {
    cy.goToDomain()
    cy.enterDomainName('DoSAC.gov.uk')
    cy.confirmProblem()
    cy.enterDomainName('dosac.gov.uk')
    cy.checkPageTitleIncludes('Has a central government minister requested the dosac.gov.uk domain name?')
  })

})
