import './base.cy'

describe('Happy path - route 1-12', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(3) // Parish or community council -> route 1

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.selectYesOrNo('domain_confirmation', 'no')

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.enterDomainName('somethingelse-pc')

    cy.checkPageTitleIncludes('Is somethingelse-pc.gov.uk the correct domain name?')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Registrant details')
    cy.get('p').should('include.text', 'For example, for Parish Councils the registrant must be the Clerk.')
    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')

    cy.checkPageTitleIncludes('Check your answers')

    cy.summaryShouldHave(0, 'WeRegister')
    cy.summaryShouldHave(1, ['Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk'])
    cy.summaryShouldHave(2, 'Parish')
    cy.summaryShouldHave(3, 'somethingelse-pc.gov.uk')
    cy.summaryShouldHave(4, 'HMRC')
    cy.summaryShouldHave(5, ['Rob Roberts', '01225672344', 'rob@example.org'])
    cy.summaryShouldHave(6, ['Clerk', 'clerk@example.org'])
    cy.summaryShouldNotHave(['Reason for request', 'Minister', 'Permission', 'Exemption'])

    cy.get('#button-continue').click()

    cy.checkPageTitleIncludes('Application submitted')
  })
})
