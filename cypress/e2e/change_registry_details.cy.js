import './base.cy'

describe('change registry details', () => {
    it('registry details', () => {
      cy.base('')
      // Change registry details
      cy.visit("registry-details/?change");
      cy.get('#id_registrant_role').clear('');
      cy.get('#id_registrant_role').type('Ghanima Atreides');

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Ghanima Atreides')
    })
  })
