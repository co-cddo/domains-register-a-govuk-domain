import './base.cy'

describe('Bad domain names', () => {
  it('accepts valid domain names', () => {
    cy.goToDomainViaRoute(3)
    cy.enterDomainName('dosac')
    cy.checkPageTitleIncludes('Is dosac.gov.uk the correct domain name?')
  })

  it('accepts valid domain names with hyphens', () => {
    cy.goToDomainViaRoute(3)
    cy.enterDomainName('dos-ac')
    cy.checkPageTitleIncludes('Is dos-ac.gov.uk the correct domain name?')
  })

  it('accepts valid domain names with capitals', () => {
    cy.goToDomainViaRoute(3)
    cy.enterDomainName('DoSAC.gov.uk')
    cy.checkPageTitleIncludes('Is dosac.gov.uk the correct domain name?')
  })

  it('accepts valid domain names when user has entered .gov.uk', () => {
    cy.goToDomainViaRoute(3)
    cy.enterDomainName('dosac.gov.uk')
    cy.checkPageTitleIncludes('Is dosac.gov.uk the correct domain name?')
  })

  it('rejects invalid domain names', () => {
    cy.goToDomainViaRoute(3)
    cy.enterDomainName('blahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblah.gov.uk')
    cy.confirmProblem('The .gov.uk domain name must be between 3 and 63 characters')

    cy.enterDomainName('dos.ac')
    cy.confirmProblem('The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens.')

    cy.enterDomainName('dos.ac.gov.uk')
    cy.confirmProblem('The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens.')

    cy.enterDomainName('007.gov.uk')
    cy.confirmProblem('The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens.')

    cy.enterDomainName('-blah.gov.uk')
    cy.confirmProblem('The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens.')

    cy.enterDomainName('blah-.gov.uk')
    cy.confirmProblem('The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens.')

    cy.enterDomainName('b.gov.uk')
    cy.confirmProblem('The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens.')
  })

  it('rejects bad domain names but accepts valid retry', () => {
    cy.goToDomainViaRoute(3)
    cy.enterDomainName('dos.ac')
    cy.confirmProblem('The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens.')
    cy.enterDomainName('dosac.gov.uk')
    cy.checkPageTitleIncludes('Is dosac.gov.uk the correct domain name?')
  })
})
