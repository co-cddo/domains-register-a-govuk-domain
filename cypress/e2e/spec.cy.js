describe('name spec', () => {
  it('passes', () => {
    cy.visit('http://0.0.0.0:8000/email/')

    // Don't type anything, just click on the button
    cy.get('.govuk-button').click()

    // There should be an error
    cy.get('#error-summary-title').should('exist')
    cy.get('#error-summary-title').should('include.text', 'There is a problem')
    cy.get('.govuk-error-summary__list').should('include.text', 'Please select an item from the list')

    // Retrying with a correct email
    cy.get('.govuk-input').type('something@some.gov.uk')
    cy.get('.govuk-button').click()

    // No error message this time
    cy.get('#error-summary-title').should('not.exist')
  })

  // it('fails', () => {
  //   cy.visit('http://0.0.0.0:8000/name/')

  //   //Get an input, type into it
  //   cy.get('.govuk-input').should('not.to.match', ':empty')

  // })
})
