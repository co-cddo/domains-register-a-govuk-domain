import './base.cy'

describe('Happy path - route 1', () => {
  it('performs a full transaction', () => {
    cy.deleteAllApplications()
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.checkBackLinkGoesTo('/registrar-details/')
    cy.chooseRegistrantType(3) // Parish, small town or community council -> route 1

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.checkBackLinkGoesTo('/registrant-type/')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.checkBackLinkGoesTo('/domain/')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Registrant details')
    cy.checkBackLinkGoesTo('/domain-confirmation/')
    cy.get('p').should('include.text', 'For example, for parish councils the registrant must be the Clerk.')

    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.checkBackLinkGoesTo('/registrant-details/')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')

    cy.checkPageTitleIncludes('Check your answers')
    cy.checkBackLinkGoesTo('/registry-details/')

    cy.summaryShouldHave(0, 'WeRegister')
    cy.summaryShouldHave(1, ['Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk'])
    cy.summaryShouldHave(2, 'Parish')
    cy.summaryShouldHave(3, 'something-pc.gov.uk')
    cy.summaryShouldHave(4, 'HMRC')
    cy.summaryShouldHave(5, ['Rob Roberts', '01225672344', 'rob@example.org'])
    cy.summaryShouldHave(6, ['Clerk', 'clerk@example.org'])
    cy.summaryShouldNotHave(['Reason for request', 'Minister', 'Permission', 'Exemption'])

    cy.get('#id_submit').click()
    cy.checkPageTitleIncludes('Application submitted')

    cy.checkPageTitleIncludes('Application submitted')
    cy.checkApplicationIsOnBackend({
      domain: 'something-pc.gov.uk',
      registrar_org: 'WeRegister',
      registrant_org: 'HMRC',
      minister: false,
      written_permission: false,
      exemption: false
    })
  })
})
