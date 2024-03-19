import './base.cy'

describe('change registrant details', () => {
    it('correctly changes the registrant details when the users goes back to change it', () => {
      cy.goToConfirmPage('')
      // Change registrant details
      cy.visit("registrant-details/?change");
      cy.get('#id_registrant_full_name').clear('');
      cy.get('#id_registrant_full_name').type('Leto II Atreides');

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Leto II Atreides')
    })
  })
