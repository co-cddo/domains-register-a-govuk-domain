import './base.cy'

describe('Error messages for registrar details', () => {
  it('tries a series of bad or missing data', () => {
    cy.goToRegistrarDetails()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Registrar details')

    // but display errors
    cy.confirmProblem('This field is required', 4)

    // enter just the registrant
    cy.get('#id_registrar_organisation').clear().type('WeRegister')
    cy.get('#id_submit').click()
    cy.confirmProblem('This field is required', 3)

    // enter a bad phone number
    cy.fillOutRegistrarDetails('WeRegister', 'Joe', '01 2', 'joe@example.com')
    cy.confirmProblem('Invalid phone number entered')

    // enter a bad email address
    cy.fillOutRegistrarDetails('WeRegister', 'Joe', '01225123334', 'a@b.c')
    cy.confirmProblem('Invalid email address entered')

    // enter valid details
    cy.fillOutRegistrarDetails('WeRegister', 'Joe', '01225123334', 'a@b.com')

    // No error, we've moved on to the next page
    cy.checkPageTitleIncludes('Who is this domain name for?')

  })
})
