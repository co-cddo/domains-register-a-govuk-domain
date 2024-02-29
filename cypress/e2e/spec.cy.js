describe('name spec', () => {
  it('passes', () => {
    cy.visit('http://0.0.0.0:8000/name/')

    //Get an input, type into it
    cy.get('.govuk-input').type('GOV UK')

    //Click Save
    cy.get('.govuk-button').click()

    // There should be an error
    cy.get('h2').should('exist')
    cy.get('h2').should('have.value', 'There is a problem')

    //Retrying with a correct email
    cy.get('.govuk-input').type('something@some.gov.uk')
    cy.get('.govuk-button').click()

    // No error message this time
    cy.get('h2').should('not.exist')

  })

  // it('fails', () => {
  //   cy.visit('http://0.0.0.0:8000/name/')

  //   //Get an input, type into it
  //   cy.get('.govuk-input').should('not.to.match', ':empty')

  // })
})
