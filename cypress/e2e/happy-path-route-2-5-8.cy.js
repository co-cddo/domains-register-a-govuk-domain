import './base.cy'

describe('Happy path - route 2-5-8', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'joe@example.org')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(1) // Central government -> Route 2

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.chooseDomainPurpose(2) // Email address only -> Route 5

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief information officer')
    cy.selectYesOrNo('written_permission', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.uploadDocument("permission.png")

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.confirmUpload('permission.png')

    cy.checkPageTitleIncludes('What .gov.uk domain name do you want?')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Has a central government minister requested the something-pc.gov.uk domain name?')
    cy.selectYesOrNo('minister', 'no')

    cy.checkPageTitleIncludes('Registrant details')
    cy.get('p').should('not.include.text', 'the registrant must be the Clerk.')
    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')

    cy.checkPageTitleIncludes('Check your answers')
    cy.summaryShouldHave(0, 'WeRegister')
    cy.summaryShouldHave(1, ['Joe Bloggs', '01225672345', 'joe@example.org'])
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

  })
})
