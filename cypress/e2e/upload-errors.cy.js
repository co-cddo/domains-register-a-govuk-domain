const goToUploadExemption = function() {
    cy.visit('http://0.0.0.0:8000/')

    cy.checkPageTitleIncludes('Which .gov.uk Approved Registrar organisation are you from?')
    cy.get('select.govuk-select').should('exist')
    cy.get('#id_organisations_choice').type('WeRegister')
    cy.get('.govuk-button#id_submit').click()


    cy.checkPageTitleIncludes('What is your email address?')
    cy.get('.govuk-input').type('something@some.gov.uk')
    cy.get('.govuk-button#id_submit').click()


    cy.checkPageTitleIncludes('Which of the following best describes your registrant\'s organisation?')
    cy.get('#id_registrant_type_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('What is your registrant’s organisation name?')
    cy.get('.govuk-input').type('HMRC')
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.get('#id_domain_purpose_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Does your registrant have an exemption from using the GOV.UK website?')
    cy.get('#id_exemption_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
}


describe('Errors when uploading files', () => {
  it('Rejects files that are too big', () => {

    goToUploadExemption()

    cy.get('input[type=file]').selectFile('cypress/fixtures/large-image.png')
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.get('h2').should('include.text', 'There is a problem')
    cy.get('#id_file_1_error').should('include.text', 'Please keep filesize under 2.5\u00a0MB. Current filesize 2.9\u00a0MB')

    cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.get('.govuk-tag').should('include.text', 'uploaded')
  })

  it('Rejects files that are not images', () => {

    goToUploadExemption()

    cy.get('input[type=file]').selectFile('cypress/fixtures/example.json')
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.get('h2').should('include.text', 'There is a problem')
    cy.get('#id_file_1_error').should('include.text', 'Wrong file format. Please upload an image.')

    cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Upload evidence of the exemption')
    cy.get('.govuk-tag').should('include.text', 'uploaded')

  })
});
