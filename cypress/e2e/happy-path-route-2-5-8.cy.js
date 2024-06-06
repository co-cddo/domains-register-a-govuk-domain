import './base.cy'

describe('Happy path - route 2-5-8', () => {
  beforeEach(() => {
    cy.deleteAllApplications()
  })

  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.checkBackLinkGoesTo('/registrar-details/')
    cy.chooseRegistrantType(1) // Central government -> Route 2

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.checkBackLinkGoesTo('/registrant-type/')
    cy.chooseDomainPurpose(2) // Email address only -> Route 5

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.checkBackLinkGoesTo('/domain-purpose/')
    cy.get('p').should('include.text', 'chief information officer')
    cy.selectYesOrNo('written_permission', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.checkBackLinkGoesTo('/written-permission/')
    cy.uploadDocument("permission.png")

    cy.checkPageTitleIncludes('Confirm uploaded evidence of permission to apply')
    cy.checkBackLinkGoesTo('/written-permission-upload/')
    cy.confirmUpload('permission.png')

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.checkBackLinkGoesTo('/written-permission-upload-confirm/')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.checkBackLinkGoesTo('/domain/')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Has a central government minister requested the something-pc.gov.uk domain name?')
    cy.checkBackLinkGoesTo('/domain-confirmation/')
    cy.selectYesOrNo('minister', 'no')

    cy.checkPageTitleIncludes('Registrant details')
    cy.checkBackLinkGoesTo('/minister/')
    cy.get('p').should('not.include.text', 'the registrant must be the Clerk.')
    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.checkBackLinkGoesTo('/registrant-details/')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')

    cy.checkPageTitleIncludes('Check your answers')
    cy.checkBackLinkGoesTo('/registry-details/')
    cy.summaryShouldHave(0, 'WeRegister')
    cy.summaryShouldHave(1, ['Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk'])
    cy.summaryShouldHave(2, 'Central government')
    cy.summaryShouldHave(3, 'Email only')
    cy.summaryShouldHave(4, ['Yes, evidence provided:', 'permission.png'])
    cy.summaryShouldHave(5, 'something-pc.gov.uk')
    cy.summaryShouldHave(6, 'No evidence provided') // Minister
    cy.summaryShouldHave(7, 'HMRC')
    cy.summaryShouldHave(8, ['Rob Roberts', '01225672344', 'rob@example.org'])
    cy.summaryShouldHave(9, ['Clerk', 'clerk@example.org'])

    cy.get('#button-continue').click()

    cy.checkPageTitleIncludes('Application submitted')
    cy.checkApplicationIsOnBackend({
      domain: 'something-pc.gov.uk',
      registrar_org: 'WeRegister',
      registrant_org: 'HMRC',
      minister: false,
      written_permission: true,
      exemption: false
    })
  })
})
