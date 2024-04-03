import './base.cy'

describe('Error messages for registrant details', () => {
  it('tries a series of bad or missing data', () => {
    cy.goToRegistrantDetails()

    // click without entering anything
    cy.get('#id_submit').click()

    // page shouldn't change
    cy.checkPageTitleIncludes('Registrant details')

    // but display errors
    cy.confirmProblem('This field is required', 4)

    // enter just the registrant
    cy.get('#id_registrant_organisation').clear().type('Littleton PC')
    cy.get('#id_submit').click()
    cy.confirmProblem('This field is required', 3)


    // enter a bad phone number
    cy.fillOutRegistrantDetails('Littleton PC', 'Joe', '01 3332', 'joe@example.com')
    cy.confirmProblem('Please enter a valid phone number')

    // enter a bad email address
    cy.fillOutRegistrantDetails('Littleton PC', 'Joe', '01225998877', 'joe@example')
    cy.confirmProblem('Please enter a valid email address')

    // enter valid details
    cy.fillOutRegistrantDetails('Littleton PC', 'Joe', '01225998877', 'joe@example.com')

    // // No error, we've moved on to the next page
    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
  })
})
