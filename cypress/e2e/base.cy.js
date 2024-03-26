//============= Page title check ==================

Cypress.Commands.add('checkPageTitleIncludes', expectedTitle => {
  return cy.get('h1').should('include.text', expectedTitle)
})

//============= Form user actions =================

Cypress.Commands.add('fillOutApplicantDetails', (name, phone, email) => {
  cy.get('#id_applicant_name').type(name)
  cy.get('#id_applicant_phone').type(phone)
  cy.get('#id_applicant_email').type(email)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('fillOutRegistrantDetails', (name, phone, email) => {
  cy.get('#id_registrant_full_name').type(name)
  cy.get('#id_registrant_phone').type(phone)
  cy.get('#id_registrant_email_address').type(email)
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
  cy.get('.govuk-input').type(typedAddress)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('chooseRegistrantType', index => {
  cy.get(`#id_registrant_type_${index}`).click()
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('typeInRegistrant', index => {
  cy.get('.govuk-input').type('HMRC')
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


Cypress.Commands.add('uploadDocument', path => {
  cy.get('input[type=file]').selectFile(path)
  cy.get('.govuk-button#id_submit').click()
})


Cypress.Commands.add('confirmUpload', fileName => {
  cy.get('#uploaded-filename').should('include.text', 'image.png')
  cy.get('.govuk-button').should('not.include.text', 'Back to answers')
  cy.get('.govuk-button#button-continue').click()
})


//============= Routes ============================

Cypress.Commands.add('goToRegistrarEmail', () => {
  cy.visit('http://0.0.0.0:8000/')
  cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
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


Cypress.Commands.add('goToWrittenPermission', () => {
  cy.goToExemption()
  cy.selectYesOrNo('exemption', 'yes')
  cy.checkPageTitleIncludes('Upload evidence of the exemption')
  cy.uploadDocument('cypress/fixtures/image.png')
  cy.checkPageTitleIncludes('Upload evidence of the exemption')
  cy.confirmUpload('image.png')
  cy.checkPageTitleIncludes('Does your registrant have written permission to apply for a .gov.uk domain name?')
})


Cypress.Commands.add('goToDomain', () => {
  cy.goToWrittenPermission()
  cy.selectYesOrNo('written_permission', 'yes')
  cy.checkPageTitleIncludes('Upload evidence of written permission')
  cy.uploadDocument('cypress/fixtures/image.png')
  cy.checkPageTitleIncludes('Upload evidence of written permission')
  cy.confirmUpload('image.png')
  cy.checkPageTitleIncludes('What .gov.uk domain name do you want?')
})


Cypress.Commands.add('goToMinister', () => {
  cy.goToDomain()

  cy.get('#id_domain_name').type('foobar')
  cy.get('.govuk-button#id_submit').click()
  cy.checkPageTitleIncludes('Has a central government minister requested the foobar.gov.uk domain name?')
})

Cypress.Commands.add('goToApplicantDetails', () => {
  cy.goToMinister()
  cy.selectYesOrNo('minister', 'yes')
  cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
  cy.uploadDocument('cypress/fixtures/image.png')
  cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
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
