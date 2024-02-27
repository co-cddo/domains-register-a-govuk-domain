describe('name spec', () => {
  it('passes', () => {
    cy.visit('http://0.0.0.0:8000/name/')
    
    //Get an input, type into it
    cy.get('.govuk-input').type('GOV UK')

    //Click Save
    cy.get('.govuk-button').click()

    //Get an input, type into it
    cy.get('.govuk-input').type('something@some.gov.uk')

    //Click Save
    cy.get('.govuk-button').click()

    //Confirm Screen
    cy.get('.govuk-heading-xl').should('have.value', '')
  })

  // it('fails', () => {
  //   cy.visit('http://0.0.0.0:8000/name/')
    
  //   //Get an input, type into it
  //   cy.get('.govuk-input').should('not.to.match', ':empty')

  // })
})
