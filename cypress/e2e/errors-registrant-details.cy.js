import './base.cy'

describe('Error messages for registrant details', () => {
  it('tries a series of bad or missing data', () => {
    cy.goToRegistrantDetails()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Registrant details')

    // but display errors
    cy.confirmProblem("Enter the registrant's full name", 4)

    // enter just the registrant
    cy.get('#id_registrant_organisation').clear().type('Littleton PC')
    cy.get('#id_submit').click()
    cy.confirmProblem("Enter the registrant's full name", 3)


    // enter a bad phone number
    cy.fillOutRegistrantDetails('Littleton PC', 'Joe', '01 3332', 'joe@example.com')
    cy.confirmProblem("Enter a telephone number, like 01632 960 001 or 07700 900 982")

    // enter a bad email address
    cy.fillOutRegistrantDetails('Littleton PC', 'Joe', '01225998877', 'joe@example')
    cy.confirmProblem("Enter an email address in the correct format, like name@example.co.uk")

    // enter valid details
    cy.fillOutRegistrantDetails('Littleton PC', 'Joe', '01225998877', 'joe@example.com')

    // // No error, we've moved on to the next page
    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
  })
})
