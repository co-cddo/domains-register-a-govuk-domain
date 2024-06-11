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

  it('Resets the session if you click the start button again', () => {
    cy.goToRegistrarDetails()
    cy.fillOutRegistrarDetails('WeRegister', 'Joe Bloggs', '01225672345', 'simulate-delivered@notifications.service.gov.uk')
    cy.checkPageTitleIncludes('Who is this domain name for?')

    // Go back to the registrar details page
    cy.get('a.govuk-back-link').click()

    // check if the details are correctly remembered
    cy.get('#id_registrar_name').should('have.value', 'Joe Bloggs')

    // Now restart from the green button
    cy.start()
    cy.get('a.govuk-button--start').click()
    cy.checkPageTitleIncludes('Registrar details')

    // Values should not be remembered
    cy.get('#id_registrar_name').should('have.value', '')
  })
})
