import './base.cy'

describe('Error messages for registrar details', () => {
  it('tries a series of bad or missing data', () => {
    cy.goToRegistrarDetails()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Registrar details')

    // but display errors
    cy.confirmProblem("Select your organisation", 4)

    // enter just the registrant
    cy.get('#id_registrar_organisation').clear().type('WeRegister')
    cy.get('#id_submit').click()
    cy.confirmProblem("Enter your full name", 3)

    // enter a bad phone number
    cy.fillOutRegistrarDetails('WeRegister', 'Joe', '01 2', 'joe@example.com')
    cy.confirmProblem('Enter a telephone number, like 01632 960 001 or 07700 900 982')

    // enter a bad email address
    cy.fillOutRegistrarDetails('WeRegister', 'Joe', '01225123334', 'a@b.c')
    cy.confirmProblem('Enter an email address in the correct format, like name@example.co.uk')

    // enter valid details
    cy.fillOutRegistrarDetails('WeRegister', 'Joe', '01225123334', 'a@b.com')

    // No error, we've moved on to the next page
    cy.checkPageTitleIncludes('Who is this domain name for?')

  })
})
