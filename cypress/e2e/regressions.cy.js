import './base.cy'

describe('Regression tests', () => {
  it('takes you to route 2 if you select ALB', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.checkBackLinkGoesTo('/registrar-details/')
    cy.chooseRegistrantType(2) // ALB -> Route 2

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
  })

  it('Resets the session if you click the start button again', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')
    cy.checkPageTitleIncludes('Who is this domain name for?')

    // Go back to the registrar details page
    cy.get('a.govuk-back-link').click()

    // check if the details are correctly remembered
    cy.get('#id_registrar_name').should('have.value', 'Joe Bloggs')

    // Now restart from the green button
    cy.start()
    cy.get('a.govuk-button--start').click()
    cy.checkPageTitleIncludes('Registrar details')

    // Values should not be remembered
    cy.get('#id_registrar_name').should('have.value', '')
  })

  it('displays the hint email as itsupport@ for central gov registrants', () => {
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

    cy.checkPageTitleIncludes('Confirm uploaded evidence of the exemption')
    cy.confirmUpload('exemption.png')

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief information officer')
    cy.selectYesOrNo('written_permission', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.uploadDocument("permission.png")

    cy.checkPageTitleIncludes('Confirm uploaded evidence of permission to apply')
    cy.confirmUpload('permission.png')

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Is something-pc.gov.uk the correct domain name?')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Has a central government minister requested the something-pc.gov.uk domain name?')
    cy.selectYesOrNo('minister', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
    cy.uploadDocument("minister.png")

    cy.checkPageTitleIncludes('Confirm uploaded evidence of the minister\'s request')
    cy.confirmUpload('minister.png')

    cy.checkPageTitleIncludes('Registrant details')
    cy.get('p').should('not.include.text', 'the registrant must be the Clerk.')
    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.get('#id_registrant_contact_email_hint').should('include.text', 'itsupport@[yourorganisation].gov.uk')
  })

  it('displays the hint email as clerk@ for parish council registrants', () => {
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
    cy.get('#id_registrant_contact_email_hint').should('include.text', 'clerk@[yourorganisation].gov.uk.')
  })
})
