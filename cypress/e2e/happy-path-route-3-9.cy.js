import './base.cy'

describe('Happy path - route 2 - 5', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'joe@example.org')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(5) // Fire service -> Route 3

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    // TODO: will need to check it's the local gov version of the written-permission page
    cy.selectYesOrNo('written_permission', 'no')

    cy.checkPageTitleIncludes('Your registrant does not have the evidence required to get a .gov.uk domain name')
    cy.get('p').should('include.text', 'chief executive')
  })
})
