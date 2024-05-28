import './base.cy'

describe('Happy path - route 3', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(5) // Fire service -> Route 3

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief executive')
    cy.selectYesOrNo('written_permission', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.uploadDocument('permission.png')

    cy.checkPageTitleIncludes('Confirm uploaded evidence of permission to apply')
    cy.confirmUpload('permission.png')

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Registrant details')
    cy.get('p').should('include.text', 'For example, for parish councils the registrant must be the Clerk.')
    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')

    cy.checkPageTitleIncludes('Check your answers')

    cy.summaryShouldHave(0, 'WeRegister')
    cy.summaryShouldHave(1, ['Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk'])
    cy.summaryShouldHave(2, 'Fire service')
    cy.summaryShouldHave(3, ['Yes, evidence provided:', 'permission.png'])
    cy.summaryShouldHave(4, 'something-pc.gov.uk')
    cy.summaryShouldHave(5, 'HMRC')
    cy.summaryShouldHave(6, ['Rob Roberts', '01225672344', 'rob@example.org'])
    cy.summaryShouldHave(7, ['Clerk', 'clerk@example.org'])

    cy.get('#button-continue').click()

    cy.checkPageTitleIncludes('Application submitted')
  })
})
