describe('Happy passes', () => {
  it('performs a full transaction', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('select.govuk-select').should('exist')
    cy.get('select.govuk-select').select('34SP.com')
    cy.get('.govuk-button#id_submit').click()


    cy.get('h1').should('include.text', 'What is your email address?')
    cy.get('.govuk-input').type('something@some.gov.uk')
    cy.get('.govuk-button#id_submit').click()


    cy.get('h1').should('include.text', 'Which of the following best describes your registrant\'s organisation?')
    cy.get('#id_registrant_type_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'What is your registrant’s organisation name?')
    cy.get('.govuk-input').type('HMRC')
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'Why do you want a .gov.uk domain name?')
    cy.get('#id_domain_purpose_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'Does your registrant have an exemption from using the GOV.UK website?')
    cy.get('#id_exe_radio_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'Upload evidence of the exemption')
    cy.get('input[type=file]').selectFile('request_a_govuk_domain/static/images/govuk-crest.png')
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'Upload evidence of the exemption')
    cy.get('a').should('include.text', 'govuk-crest.png')
    cy.get('.govuk-button#button-continue').click()

    cy.get('h1').should('include.text', 'Does your registrant have written permission to apply for a .gov.uk domain name?')
    cy.get('#id_written_permission_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'Upload evidence of written permission')
    cy.get('input[type=file]').selectFile('request_a_govuk_domain/static/images/govuk-crest.png')
    cy.get('.govuk-button#id_submit').click()

    cy.get('h1').should('include.text', 'Upload evidence of written permission')
    cy.get('a').should('include.text', 'govuk-crest.png')
    cy.get('.govuk-button#button-continue').click()

    // Domain
    cy.get('h1').should('include.text', 'What .gov.uk domain name do you want?')
    cy.get('#id_domain_name').type('foobar')
    cy.get('.govuk-button#id_submit').click()

    // Minister
    cy.get('h1').should('include.text', 'Has a central government minister requested the domain name?')
    cy.get('#id_minister_radios_1').click()
    cy.get('.govuk-button#id_submit').click()

    // Minister upload
    cy.get('h1').should('include.text', 'Upload evidence of the minister\'s request')
    cy.get('input[type=file]').selectFile('request_a_govuk_domain/static/images/govuk-crest.png')
    cy.get('.govuk-button#id_submit').click()

    // Minister upload confirmation
    cy.get('h1').should('include.text', 'Upload evidence of the minister\'s request')
    cy.get('a').should('include.text', 'govuk-crest.png')
    cy.get('.govuk-button#button-continue').click()

    // Applicant details
    cy.get('h1').should('include.text', 'Applicant details')
    cy.get('#id_applicant_name').type('Joe Bloggs')
    cy.get('#id_applicant_phone').type('01225672736')
    cy.get('#id_applicant_email').type('joe@example.com')
    cy.get('.govuk-button#id_submit').click()

    // Registrant details
    cy.get('h1').should('include.text', 'Registrant details')
    cy.get('#id_registrant_full_name').type('Robert Smith')
    cy.get('#id_registrant_phone').type('01225672345')
    cy.get('#id_registrant_email_address').type('rob@example.com')
    cy.get('.govuk-button#id_submit').click()

    // Registry details
    cy.get('h1').should('include.text', 'Registrant details for publishing to the registry')
    cy.get('#id_registrant_role').type('Robert Smith')
    cy.get('#id_registrant_contact_phone').type('01225672345')
    cy.get('#id_registrant_contact_email').type('rob@example.com')
    cy.get('.govuk-button#id_submit').click()

    // Confirm
    cy.get('h1').should('include.text', 'Check your answers')
    cy.get('.govuk-button#button-continue').click()

    // Success
    cy.get('h1').should('include.text', 'Application submitted')
  })
})
