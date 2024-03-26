import './base.cy'

describe('change registrant details', () => {
  it('correctly changes the registrant details when the users goes back to change it', () => {
    cy.goToConfirmation('')


    cy.get("a[href='/change-written-permission']").click()
    cy.checkPageTitleIncludes('Does your registrant have written permission')

    cy.get('#id_written_permission_1').click()
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Upload evidence of written permission')
    cy.get('input[type=file]').selectFile('cypress/fixtures/new-image.png')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Upload evidence of written permission')
    cy.get('#uploaded-filename').should('include.text', 'new-image.png')
    cy.get('#id_back_to_answers').click();


    // Back to Answers
    cy.checkPageTitleIncludes('Check your answers')
    cy.get('.govuk-summary-list__value').should('include.text', 'new-image.png')

    // Again, but pressing Continue should take you to Registry details
    cy.get("a[href='/change-written-permission']").click()
    cy.checkPageTitleIncludes('Does your registrant have written permission')

    cy.get('#id_written_permission_1').click()
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Upload evidence of written permission')
    cy.get('input[type=file]').selectFile('cypress/fixtures/new-image.png')
    cy.get('.govuk-button#id_submit').click()
    cy.checkPageTitleIncludes('Upload evidence of written permission')
    cy.get('#button-continue').click()
    cy.checkPageTitleIncludes('What .gov.uk domain name do you want?')
  })


})
