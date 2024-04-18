//============= Page title check ==================

Cypress.Commands.add('checkPageTitleIncludes', expectedTitle => {
  return cy.get('h1').should('include.text', expectedTitle)
})


Cypress.Commands.add('confirmProblem', (errorMessage, nb_errors = 1) => {
  cy.get('#error-summary-title').should('exist')

  // count the number of errors
  cy.get('.govuk-error-summary__list li').should('have.length', nb_errors)

  // check the error box title
  cy.get('h2').should('include.text', 'There is a problem')

  // check the error is display
  if (errorMessage) {
    cy.get('.govuk-error-summary__list').should('include.text', errorMessage)
  }
})

Cypress.Commands.add('summaryShouldHave', (index, value)  => {
  if (typeof value === 'string') {
    // if a string is passed check that it's at the required index
    cy.get('.govuk-summary-list__value').eq(index).should('include.text', value)
  } else if (Array.isArray(value)) {
      // if an array strings is passed check that all are included at the required index
    for (const subvalue of value) {
      cy.get('.govuk-summary-list__value').eq(index).should('include.text', subvalue)
    }
  }
})

Cypress.Commands.add('summaryShouldNotHave', keys => {
  // Make sure the passed keys are not in the summary
  for (const key in keys) {
    cy.get('.govuk-summary-list__key').should('not.include.text', key)
  }
})


//============= Form user actions =================

Cypress.Commands.add('enterDomainName', name => {
  cy.get('#id_domain_name').clear().type(name)
  cy.get('.govuk-button#id_submit').click()
})

Cypress.Commands.add('fillOutRegistrarDetails', (org, name, phone, email) => {
  cy.get('#id_registrar_organisation').clear().type('WeRegister')
  cy.get('#id_registrar_name').clear().type(name)
  cy.get('#id_registrar_phone').clear().type(phone)
  cy.get('#id_registrar_email').clear().type(email)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('fillOutRegistrantDetails', (org, name, phone, email) => {
  cy.get('#id_registrant_organisation').clear().type(org)
  cy.get('#id_registrant_full_name').clear().type(name)
  cy.get('#id_registrant_phone').clear().type(phone)
  cy.get('#id_registrant_email').clear().type(email)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('fillOutRegistryDetails', (name, email) => {
  cy.get('#id_registrant_role').clear().type(name)
  cy.get('#id_registrant_contact_email').clear().type(email)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('chooseRegistrar', typedName => {
  cy.get('#id_organisations_choice').clear().type('WeRegister')
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('typeInEmail', typedAddress => {
  cy.get('.govuk-input').clear().type(typedAddress)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('chooseRegistrantType', index => {
  cy.get(`#id_registrant_type_${index}`).click()
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('typeInRegistrant', index => {
  cy.get('.govuk-input').clear().type('HMRC')
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('chooseDomainPurpose', index => {
  cy.get(`#id_domain_purpose_${index}`).click()
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('selectYesOrNo', (page, yesOrNo) => {
  if (yesOrNo === 'yes') {
    cy.get(`#id_${page}_1`).click()
  } else {
    cy.get(`#id_${page}_2`).click()
  }
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('uploadDocument', filename => {
  cy.get('input[type=file]').selectFile(`cypress/fixtures/${filename}`)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('confirmUpload', filename => {
  cy.get('#uploaded-filename').should('include.text', filename)
  cy.get('.govuk-tag').should('include.text', 'Uploaded')
  cy.get('.govuk-button').should('not.include.text', 'Back to answers')
  cy.get('.govuk-button#button-continue').click()
})


//============= Routes ============================

Cypress.Commands.add('start', () => {
  cy.visit('/')
  cy.checkPageTitleIncludes('Get approval to use a .gov.uk domain name')
})


Cypress.Commands.add('goToRegistrarDetails', () => {
  cy.start()
  cy.get('a.govuk-button--start').click()
  cy.checkPageTitleIncludes('Registrar details')
})


Cypress.Commands.add('goToRegistrantType', () => {
  cy.goToRegistrarDetails()
  cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'joe@example.org')
  cy.checkPageTitleIncludes('Who is this domain name for?')
})


Cypress.Commands.add('goToDomainPurpose', () => {
  cy.goToRegistrantType()
  cy.chooseRegistrantType(1) // Central-gov -> route 2
  cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
})


Cypress.Commands.add('goToExemption', () => {
  cy.goToDomainPurpose()
  cy.chooseDomainPurpose(1) // Website -> route 7
  cy.checkPageTitleIncludes('Does your registrant have an exemption from using the GOV.UK website?')
})

Cypress.Commands.add('goToWrittenPermission', () => {
  cy.goToRegistrantType()
  cy.chooseRegistrantType(3) // Fire service -> route 3
  cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
})


Cypress.Commands.add('goToExemptionUpload', () => {
  cy.goToExemption()
  cy.selectYesOrNo('exemption', 'yes')
  cy.checkPageTitleIncludes('Upload evidence of the exemption')
})


Cypress.Commands.add('goToExemptionUploadConfirm', filename => {
  cy.goToExemptionUpload()
  cy.uploadDocument(filename)
  cy.checkPageTitleIncludes('Upload evidence of the exemption')
})


Cypress.Commands.add('goToWrittenPermission', () => {
  cy.goToRegistrantType()
  cy.chooseRegistrantType(4) // Route 3
  cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
})


Cypress.Commands.add('goToWrittenPermissionUpload', filename => {
  cy.goToWrittenPermission()
  cy.selectYesOrNo('written_permission', 'yes')
  cy.checkPageTitleIncludes('Upload evidence of permission to apply')
})


Cypress.Commands.add('goToWrittenPermissionUploadConfirm', filename => {
  cy.goToWrittenPermissionUpload()
  cy.uploadDocument(filename)
  cy.checkPageTitleIncludes('Upload evidence of permission to apply')
})


Cypress.Commands.add('goToDomainConfirmation', (via_route = 1) => {
  cy.goToDomainViaRoute(via_route)
  cy.enterDomainName('something-pc')
})


Cypress.Commands.add('goToDomainViaRoute', route => {
  if (route === 3) {
    cy.goToWrittenPermissionUploadConfirm('permission.png')
    cy.confirmUpload('permission.png')
    cy.checkPageTitleIncludes('Choose a .gov.uk domain name?')
  } else if (route === 2) {
    cy.goToDomainPurpose()
    cy.chooseDomainPurpose(1) // Route 5
    cy.checkPageTitleIncludes('Does your registrant have an exemption from using the GOV.UK website?')
    cy.selectYesOrNo('exemption', 'yes')
    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.uploadDocument('exemption.png')
    cy.confirmUpload('exemption.png')
    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.selectYesOrNo('written_permission', 'yes')
    cy.checkPageTitleIncludes('Upload evidence of permission')
    cy.uploadDocument('permission.png')
    cy.checkPageTitleIncludes('Upload evidence of permission')
    cy.confirmUpload('permission.png')
    cy.checkPageTitleIncludes('Choose a .gov.uk domain name?')
  } else if (route === 1) {
    cy.goToRegistrantType()
    cy.chooseRegistrantType(3) // Parish -> route 1
    cy.checkPageTitleIncludes('Choose a .gov.uk domain name?')
  }
})

Cypress.Commands.add('goToMinister', () => {
  cy.goToDomainViaRoute(2)
  cy.enterDomainName('foobar')
  cy.checkPageTitleIncludes('Is foobar.gov.uk the correct domain name?')
  cy.selectYesOrNo('domain_confirmation', 'yes')
  cy.checkPageTitleIncludes('Has a central government minister requested the foobar.gov.uk domain name?')
})

Cypress.Commands.add('goToMinisterUpload', filename => {
  cy.goToMinister()
  cy.selectYesOrNo('minister', 'yes')
  cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
})

Cypress.Commands.add('goToMinisterUploadConfirm', filename => {
  cy.goToMinisterUpload()
  cy.uploadDocument(filename)
  cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
})


Cypress.Commands.add('goToRegistrantDetails', () => {
  cy.goToDomainConfirmation()
  cy.selectYesOrNo('domain_confirmation', 'yes')
  cy.checkPageTitleIncludes('Registrant details')
})


Cypress.Commands.add('goToRegistryDetails', () => {
  cy.goToRegistrantDetails()
  cy.fillOutRegistrantDetails('Littleton PC', 'Robert Smith', '01225672345', 'rob@example.com')
  cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
})


Cypress.Commands.add('goToConfirmation', (route=1) => {
  if (route === 1) {
    cy.goToRegistryDetails()
    cy.fillOutRegistryDetails('Clerk', 'rob@example.com')
    cy.checkPageTitleIncludes('Check your answers')
  } else if (route === 7) {
    cy.goToExemptionUploadConfirm('exemption.png')
    cy.confirmUpload('exemption.png')

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief information officer')
    cy.selectYesOrNo('written_permission', 'yes')

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.uploadDocument("permission.png")

    cy.checkPageTitleIncludes('Upload evidence of permission to apply')
    cy.confirmUpload('permission.png')

    cy.checkPageTitleIncludes('Choose a .gov.uk domain name?')
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
  }
})
