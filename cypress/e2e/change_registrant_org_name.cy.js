import './base.cy'

describe('change registrant organisation name', () => {
    it('correctly changes registrant when the users goes back to change it', () => {
      cy.goToConfirmation()
      // Change Organisation name
      cy.get('a[href="/change-registrant"]').click()
      cy.get('#id_registrant_organisation').clear().type('Caladan')

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Caladan')
    })
  })
