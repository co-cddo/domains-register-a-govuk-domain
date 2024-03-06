describe('Happy passes', () => {
  it('performs a full transaction', () => {
    cy.visit('http://0.0.0.0:8000/')

    cy.get('h1').should('include.text', 'Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('select.govuk-select').should('exist')
    cy.get('select.govuk-select').select('34SP.com')
    cy.get('.govuk-button').click()


    cy.get('h1').should('include.text', 'What is your email address?')
    cy.get('.govuk-input').type('something@some.gov.uk')
    cy.get('.govuk-button').click()


    cy.get('h1').should('include.text', 'Which of the following best describes your registrant\'s organisation?')
    cy.get('#id_registrant_type_1').click()
    cy.get('.govuk-button').click()

    cy.get('h1').should('include.text', 'What is your registrant’s organisation name?')
    cy.get('.govuk-input').type('HMRC')
    cy.get('.govuk-button').click()

    cy.get('h1').should('include.text', 'Why do you want a .gov.uk domain name?')
    cy.get('#id_domain_purpose_1').click()
    cy.get('.govuk-button').click()

    cy.get('h1').should('include.text', 'Does your registrant have an exemption from using the GOV.UK website?')
    cy.get('#id_exe_radio_1').click()
    cy.get('.govuk-button').click()

    cy.get('h1').should('include.text', 'Upload evidence of the exemption')
    cy.get('input[type=file]').selectFile('request_a_govuk_domain/static/images/govuk-crest.png')
    cy.get('.govuk-button').click()

    cy.get('h1').should('include.text', 'Upload evidence of the exemption')
    cy.get('a').should('include.text', 'govuk-crest.png')
    cy.get('.govuk-button').click()

    cy.get('h1').should('include.text', 'Does your registrant have written permission to apply for a .gov.uk domain name?')

  })
})
