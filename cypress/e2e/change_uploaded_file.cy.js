import './base.cy'

describe('change registrant details', () => {
  it('correctly changes the registrant details when the users goes back to change it', () => {
    cy.goToConfirmation('')


    cy.get("a[href='/change-written-permission']").click()
    cy.get('h1').should('include.text', 'Does your registrant have written permission')

    cy.get('#id_written_permission_1').click()
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Upload evidence of written permission')
    cy.get('input[type=file]').selectFile('cypress/fixtures/new-image.png')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Upload evidence of written permission')
    cy.get('#uploaded-filename').should('include.text', 'new-image.png')
    cy.get('#id_back_to_answers').click();


    // Back to Answers
    cy.get('h1').should('include.text', 'Check your answers')
    cy.get('.govuk-summary-list__value').should('include.text', 'new-image.png')

    // Again, but pressing Continue should take you to Registry details
    cy.get("a[href='/change-written-permission']").click()
    cy.get('h1').should('include.text', 'Does your registrant have written permission')

    cy.get('#id_written_permission_1').click()
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Upload evidence of written permission')
    cy.get('input[type=file]').selectFile('cypress/fixtures/new-image.png')
    cy.get('.govuk-button#id_submit').click()
    cy.get('h1').should('include.text', 'Upload evidence of written permission')
    cy.get('#button-continue').click()
    cy.get('h1').should('include.text', 'What .gov.uk domain name do you want?')
  })


})
