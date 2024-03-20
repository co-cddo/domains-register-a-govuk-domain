import './base.cy'

describe('Happy path with all uploads', () => {
  it('performs a full transaction with 3 uploads', () => {
    cy.goToConfirmation()
    cy.get('.govuk-button#button-continue').click()
    cy.get('h1').should('include.text', 'Application submitted')
    cy.get('body').should('include.text', 'We have sent you a confirmation email with a record of your answers')
  })
})
