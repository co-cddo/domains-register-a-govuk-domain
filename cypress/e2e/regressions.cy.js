import './base.cy'

describe('Regression tests', () => {
  it('takes you to route 2 if you select ALB', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.checkBackLinkGoesTo('/registrar-details/')
    cy.chooseRegistrantType(2) // ALB -> Route 2

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
  })
})
