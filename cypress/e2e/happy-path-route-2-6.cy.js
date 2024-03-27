import './base.cy'

describe('Happy path - route 2-6', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'joe@example.org')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(1) // Central government -> Route 2

    cy.checkPageTitleIncludes('Why do you want a .gov.uk domain name?')
    cy.chooseDomainPurpose(3) // API -> Route 6

    cy.checkPageTitleIncludes('Your registrant cannot get approval for a .gov.uk domain name')
  })
})
