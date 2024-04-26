import './base.cy'

describe('Happy path - route 2-7', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(1) // Central government -> Route 2

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.chooseDomainPurpose(1) // Email+web -> Route 7

    cy.checkPageTitleIncludes('Does your registrant have an exemption from using the GOV.UK website?')
    cy.selectYesOrNo('exemption', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.uploadDocument("exemption.png")

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.confirmUpload('exemption.png')

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief information officer')
    cy.selectYesOrNo('written_permission', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.uploadDocument("permission.png")

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.confirmUpload('permission.png')

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Has a central government minister requested the something-pc.gov.uk domain name?')
    cy.selectYesOrNo('minister', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
    cy.uploadDocument("minister.png")

    cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
    cy.confirmUpload('minister.png')

    cy.checkPageTitleIncludes('Registrant details')
    cy.get('p').should('not.include.text', 'the registrant must be the Clerk.')
    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')

    cy.checkPageTitleIncludes('Check your answers')

    cy.summaryShouldHave(0, 'WeRegister')
    cy.summaryShouldHave(1, ['Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk'])
    cy.summaryShouldHave(2, 'Central government')
    cy.summaryShouldHave(3, 'Website (may include email)')
    cy.summaryShouldHave(4, ['Yes, evidence provided:', 'exemption.png'])
    cy.summaryShouldHave(5, ['Yes, evidence provided:', 'permission.png'])
    cy.summaryShouldHave(6, 'something-pc.gov.uk')
    cy.summaryShouldHave(7, ['Yes, evidence provided:', 'minister.png'])
    cy.summaryShouldHave(8, 'HMRC')
    cy.summaryShouldHave(9, ['Rob Roberts', '01225672344', 'rob@example.org'])
    cy.summaryShouldHave(10, ['Clerk', 'clerk@example.org'])


    cy.get('#button-continue').click()

    cy.checkPageTitleIncludes('Application submitted')

  })
})
