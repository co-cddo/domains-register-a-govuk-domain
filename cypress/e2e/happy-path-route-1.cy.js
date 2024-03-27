import './base.cy'

describe('Happy path - route 1', () => {
  it('performs a full transaction', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'joe@example.org')

    cy.checkPageTitleIncludes('Who is this domain name for?')
    cy.chooseRegistrantType(3) // Parish or community council -> route 1

    cy.checkPageTitleIncludes('What .gov.uk domain name do you want?')
    cy.enterDomainName('something-pc')

    cy.checkPageTitleIncludes('Can you confirm if the something-pc.gov.uk domain name is correct?')
    cy.selectYesOrNo('domain_confirmation', 'yes')

    cy.checkPageTitleIncludes('Registrant details')
    cy.get('p').should('include.text', 'For example, for Parish Councils the registrant must be the Clerk.')

    cy.fillOutRegistrantDetails('HMRC', 'Rob Roberts', '01225672344', 'rob@example.org')

    cy.checkPageTitleIncludes('Registrant details for publishing to the registry')
    cy.fillOutRegistryDetails('Clerk', 'clerk@example.org')

    cy.checkPageTitleIncludes('Check your answers')
    cy.get('#button-continue').click()

    cy.checkPageTitleIncludes('Application submitted')
  })
})
