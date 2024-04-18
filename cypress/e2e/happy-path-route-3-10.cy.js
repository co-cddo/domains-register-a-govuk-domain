import './base.cy'

describe('Happy path - route 3-9', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(5) // Fire service -> Route 3

    cy.checkPageTitleIncludes('Does your registrant have proof of permission to apply for a .gov.uk domain name?')
    cy.get('p').should('include.text', 'chief executive')
    cy.selectYesOrNo('written_permission', 'no')

    cy.checkPageTitleIncludes('Your registrant does not have the evidence required to get a .gov.uk domain name')
    cy.get('p').should('include.text', 'chief executive')
  })
})
