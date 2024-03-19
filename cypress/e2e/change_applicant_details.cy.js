import './base.cy'

describe('change applicant details', () => {
    it('correctly changes the applicant name when the users goes back to change it', () => {
      cy.goToConfirmPage('')
      // Change applicant name
      cy.visit("applicant-details/?change");
      cy.get('#id_applicant_name').clear('');
      cy.get('#id_applicant_name').type('Paul Atreides');

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Paul Atreides')
    })
  })
