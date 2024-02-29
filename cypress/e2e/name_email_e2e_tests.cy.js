/// <reference types="Cypress" />


describe('name_and_email_confirmation', () => {
  it('checks name and email', () => {
    cy.visit('name/')

    //Get an input, type into it
    cy.get('.govuk-input').type('GOV UK')

    //Click Save
    cy.get('.govuk-button').click()

    //Check email url
    cy.url().should('include', '/email')

    //Get an input, type into it
    cy.get('.govuk-input').type('something@some.gov.uk')

    //Check the entered email
    cy.get('.govuk-input').should('have.value', 'something@some.gov.uk')

    //Click Save
    cy.get('.govuk-button').click()

    //Confirm Screen
    cy.contains('Confirm')
    
    // last step
    cy.get('.govuk-button').click();

    cy.contains('Thanks for submitting!')
  })
})
