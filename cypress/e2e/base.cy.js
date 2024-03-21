Cypress.Commands.add('goToRegistrarEmail', () => {
  cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('#id_organisations_choice').type('WeRegister')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'What is your email address?')
})


Cypress.Commands.add('goToRegistrantType', () => {
  cy.goToRegistrarEmail()

  cy.get('.govuk-input').type('something@some.gov.uk')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Which of the following best describes your registrant\'s organisation?')
})


Cypress.Commands.add('goToRegistrant', () => {
  cy.goToRegistrantType()

  cy.get('#id_registrant_type_1').click()
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'What is your registrant’s organisation name?')
})


Cypress.Commands.add('goToDomainPurpose', () => {
  cy.goToRegistrant()

  cy.get('.govuk-input').type('HMRC')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Why do you want a .gov.uk domain name?')
})


Cypress.Commands.add('goToExemption', () => {
  cy.goToDomainPurpose()

  cy.get('#id_domain_purpose_1').click()
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Does your registrant have an exemption from using the GOV.UK website?')
})


Cypress.Commands.add('goToWrittenPermission', () => {
  cy.goToExemption()

  cy.get('#id_exe_radio_1').click()
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Upload evidence of the exemption')
  cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Upload evidence of the exemption')
  cy.get('a').should('include.text', 'image.png')
  cy.get('.govuk-button#button-continue').click()
  cy.get('h1').should('include.text', 'Does your registrant have written permission to apply for a .gov.uk domain name?')
})


Cypress.Commands.add('goToDomain', () => {
  cy.goToWrittenPermission()

  cy.get('#id_written_permission_1').click()
  cy.get('.govuk-button#id_submit').click()

  cy.get('h1').should('include.text', 'Upload evidence of written permission')
  cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
  cy.get('.govuk-button#id_submit').click()

  cy.get('h1').should('include.text', 'Upload evidence of written permission')
  cy.get('a').should('include.text', 'image.png')
  cy.get('.govuk-button#button-continue').click()

  cy.get('h1').should('include.text', 'What .gov.uk domain name do you want?')
})


Cypress.Commands.add('goToMinister', () => {
  cy.goToDomain()
  cy.get('#id_domain_name').type('foobar')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Has a central government minister requested the foobar.gov.uk domain name?')
})

Cypress.Commands.add('goToApplicantDetails', () => {
  cy.goToMinister()
  cy.get('#id_minister_radios_1').click()
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Upload evidence of the minister\'s request')
  cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Upload evidence of the minister\'s request')
  cy.get('a').should('include.text', 'image.png')
  cy.get('.govuk-button#button-continue').click()
  cy.get('h1').should('include.text', 'Applicant details')
})


Cypress.Commands.add('goToRegistrantDetails', () => {
  cy.goToApplicantDetails()
  cy.get('#id_applicant_name').type('Joe Bloggs')
  cy.get('#id_applicant_phone').type('01225672736')
  cy.get('#id_applicant_email').type('joe@example.com')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Registrant details')
})


Cypress.Commands.add('goToRegistryDetails', () => {
  cy.goToRegistrantDetails()
  cy.get('#id_registrant_full_name').type('Robert Smith')
  cy.get('#id_registrant_phone').type('01225672345')
  cy.get('#id_registrant_email_address').type('rob@example.com')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Registrant details for publishing to the registry')
})


Cypress.Commands.add('goToConfirmation', () => {
  cy.goToRegistryDetails()
  cy.get('#id_registrant_role').type('Robert Smith')
  cy.get('#id_registrant_contact_phone').type('01225672345')
  cy.get('#id_registrant_contact_email').type('rob@example.com')
  cy.get('.govuk-button#id_submit').click()
  cy.get('h1').should('include.text', 'Check your answers')
})
