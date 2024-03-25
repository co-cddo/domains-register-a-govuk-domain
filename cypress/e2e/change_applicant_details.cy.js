import './base.cy'

describe('change applicant details', () => {
    it('correctly changes the applicant name when the users goes back to change it', () => {
      cy.goToConfirmation()
      // Change applicant name
      cy.get("a[href='/change-applicant-details']").click()
      cy.get('#id_applicant_name').clear('').type('Paul Atreides');

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Paul Atreides')
      // Again, but pressing Continue should take you to the next step, not the confirm page
      cy.get("a[href='/change-applicant-details']").click()
      cy.get('#id_applicant_name').clear().type('Paul Atreides');

      // Click continue
      cy.get('#id_submit').click();
      cy.get('h1').should('include.text', 'Registrant details')
    })
  })
