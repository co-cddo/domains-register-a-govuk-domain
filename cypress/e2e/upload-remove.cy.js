const goToUploadedExemption = function() {
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

  cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
  cy.get('.govuk-button#id_submit').click()
  cy.checkPageTitleIncludes('Upload evidence of the exemption')
  cy.get('.govuk-tag').should('include.text', 'uploaded')
}


describe('Errors when uploading files', () => {
  it('Removes the exemption uploaded data', () => {

    goToUploadedExemption()

    cy.get("#uploaded-filename").invoke('attr', 'href').then(uploadedFilename => {
      cy.get('#remove-link').click()
      cy.checkPageTitleIncludes('Upload evidence of the exemption')

      cy.get('input[type=file]').then(fileInputs => {
        expect(fileInputs.length).to.equal(1)
        expect(fileInputs[0].files.length).to.equal(0)
      })

      cy.request({
        url: 'http://0.0.0.0:8000' + uploadedFilename,
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404);
      });
    });
  });

  it('Removes the written permission uploaded data', () => {

    goToUploadedExemption()

    cy.get('.govuk-button#button-continue').click()

    cy.checkPageTitleIncludes('Does your registrant have written permission to apply for a .gov.uk domain name?')
    cy.get('#id_written_permission_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Upload evidence of written permission')
    cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
    cy.get('.govuk-button#id_submit').click()

    cy.get("#uploaded-filename").invoke('attr', 'href').then(uploadedFilename => {
      cy.get('#remove-link').click()
      cy.checkPageTitleIncludes('Upload evidence of written permission')

      cy.get('input[type=file]').then(fileInputs => {
        expect(fileInputs.length).to.equal(1)
        expect(fileInputs[0].files.length).to.equal(0)
      })

      cy.request({
        url: 'http://0.0.0.0:8000' + uploadedFilename,
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404);
      });
    });
  });

  it('Removes the minister uploaded data', () => {

    goToUploadedExemption()

    cy.get('.govuk-button#button-continue').click()

    cy.checkPageTitleIncludes('Does your registrant have written permission to apply for a .gov.uk domain name?')
    cy.get('#id_written_permission_1').click()
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Upload evidence of written permission')
    cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
    cy.get('.govuk-button#id_submit').click()

    cy.checkPageTitleIncludes('Upload evidence of written permission')
    cy.get('a').should('include.text', 'image.png')

    cy.get('.govuk-button#button-continue').click()

    // Domain
    cy.checkPageTitleIncludes('What .gov.uk domain name do you want?')
    cy.get('#id_domain_name').type('foobar')
    cy.get('.govuk-button#id_submit').click()

    // Minister
    cy.checkPageTitleIncludes('Has a central government minister requested the foobar.gov.uk domain name?')
    cy.get('#id_minister_1').click()
    cy.get('.govuk-button#id_submit').click()

    // Minister upload
    cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')
    cy.get('input[type=file]').selectFile('cypress/fixtures/image.png')
    cy.get('.govuk-button#id_submit').click()

    cy.get("#uploaded-filename").invoke('attr', 'href').then(uploadedFilename => {
      cy.get('#remove-link').click()
      cy.checkPageTitleIncludes('Upload evidence of the minister\'s request')

      cy.get('input[type=file]').then(fileInputs => {
        expect(fileInputs.length).to.equal(1)
        expect(fileInputs[0].files.length).to.equal(0)
      })

      cy.request({
        url: 'http://0.0.0.0:8000' + uploadedFilename,
        failOnStatusCode: false
      }).then(response => {
        expect(response.status).to.eq(404);
      });
    });
  });


});
