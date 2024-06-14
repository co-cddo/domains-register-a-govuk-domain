import './base.cy'

describe('Happy path - route 4', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(12) // None of the above -> route 4

    cy.checkPageTitleIncludes('Your registrant is not eligible for a .gov.uk domain name')
  })
})
