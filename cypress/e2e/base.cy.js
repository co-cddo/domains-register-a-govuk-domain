//============= Page title check ==================

Cypress.Commands.add('checkPageTitleIncludes', expectedTitle => {
  return cy.get('h1').should('include.text', expectedTitle)
})


Cypress.Commands.add('confirmProblem', (errorMessage) => {
  cy.get('#error-summary-title').should('exist')
  cy.get('h2').should('include.text', 'There is a problem')
  if (errorMessage) {
    cy.get('.govuk-error-summary__list').should('include.text', errorMessage)
  }
})

//============= Form user actions =================

Cypress.Commands.add('enterDomainName', name => {
  cy.get('#id_domain_name').clear().type(name)
  cy.get('.govuk-button#id_submit').click()
})

Cypress.Commands.add('fillOutRegistrarDetails', (org, name, phone, email) => {
  cy.get('#id_registrar_organisation').type('WeRegister')
  cy.get('#id_registrar_name').type(name)
  cy.get('#id_registrar_phone').type(phone)
  cy.get('#id_registrar_email').type(email)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('fillOutRegistrantDetails', (org, name, phone, email) => {
  cy.get('#id_registrant_organisation').type(name)
  cy.get('#id_registrant_full_name').type(name)
  cy.get('#id_registrant_phone').type(phone)
  cy.get('#id_registrant_email').type(email)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('fillOutRegistryDetails', (name, phone, email) => {
  cy.get('#id_registrant_role').type(name)
  cy.get('#id_registrant_contact_phone').type(phone)
  cy.get('#id_registrant_contact_email').type(email)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('chooseRegistrar', typedName => {
  cy.get('#id_organisations_choice').type('WeRegister')
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
  cy.get('#id_domain_purpose_1').click()
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
  cy.get('.govuk-tag').should('include.text', 'uploaded')
  cy.get('.govuk-button').should('not.include.text', 'Back to answers')
  cy.get('.govuk-button#button-continue').click()
})


//============= Routes ============================

Cypress.Commands.add('goToRegistrarDetails', () => {
  cy.visit('http://0.0.0.0:8000/')
  cy.checkPageTitleIncludes('Registrar details')
})


Cypress.Commands.add('goToRegistrarEmail', () => {
  cy.goToRegistrar()
  cy.chooseRegistrar('WeRegister')
  cy.checkPageTitleIncludes('What is your email address?')
})


Cypress.Commands.add('goToRegistrantType', () => {
  cy.goToRegistrarEmail()
  cy.typeInEmail('weregister@example.com')
  cy.checkPageTitleIncludes('Which of the following best describes your registrant\'s organisation?')
})


Cypress.Commands.add('goToRegistrant', () => {
  cy.goToRegistrantType()
  cy.chooseRegistrantType(1)
  cy.checkPageTitleIncludes('What is your registrant’s organisation name?')
})


Cypress.Commands.add('goToDomainPurpose', () => {
  cy.goToRegistrant()
  cy.typeInRegistrant('HMRC')
  cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
})


Cypress.Commands.add('goToExemption', () => {
  cy.goToDomainPurpose()
  cy.chooseDomainPurpose(1)
  cy.checkPageTitleIncludes('Does your registrant have an exemption from using the GOV.UK website?')
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
  cy.goToExemptionUploadConfirm('image.png')
  cy.confirmUpload('image.png')
  cy.checkPageTitleIncludes('Does your registrant have written permission to apply for a .gov.uk domain name?')
})


Cypress.Commands.add('goToWrittenPermissionUpload', filename => {
  cy.goToWrittenPermission()
  cy.selectYesOrNo('written_permission', 'yes')
  cy.checkPageTitleIncludes('Upload evidence of written permission')
})


Cypress.Commands.add('goToWrittenPermissionUploadConfirm', filename => {
  cy.goToWrittenPermissionUpload()
  cy.uploadDocument(filename)
  cy.checkPageTitleIncludes('Upload evidence of written permission')
})


Cypress.Commands.add('goToDomain', () => {
  cy.goToWrittenPermissionUploadConfirm('image.png')
  cy.confirmUpload('image.png')
  cy.checkPageTitleIncludes('What .gov.uk domain name do you want?')
})


Cypress.Commands.add('goToMinister', () => {
  cy.goToDomain()
  cy.enterDomainName('foobar')
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


Cypress.Commands.add('goToApplicantDetails', () => {
  cy.goToMinisterUploadConfirm('image.png')
  cy.confirmUpload('image.png')
  cy.checkPageTitleIncludes('Applicant details')
})


Cypress.Commands.add('goToRegistrantDetails', () => {
  cy.goToApplicantDetails()
  cy.fillOutApplicantDetails('Joe Bloggs', '01225672736', 'joe@example.com')
  cy.checkPageTitleIncludes('Registrant details')
})


Cypress.Commands.add('goToRegistryDetails', () => {
  cy.goToRegistrantDetails()
  cy.fillOutRegistrantDetails('Robert Smith', '01225672345', 'rob@example.com')
  cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
})


Cypress.Commands.add('goToConfirmation', () => {
  cy.goToRegistryDetails()
  cy.fillOutRegistryDetails('Clerk', '01225672345', 'rob@example.com')
  cy.checkPageTitleIncludes('Check your answers')
})
