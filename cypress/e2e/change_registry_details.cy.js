import './base.cy'

describe('change registry details', () => {
    it('correctly changes registry details', () => {
      cy.goToConfirmation('')
      // Change registry details
      cy.get("a[href='/change-registry-details']").click()
      cy.get('#id_registrant_role').clear().type('Ghanima Atreides');

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.checkPageTitleIncludes('Check your answers')
      cy.get('.govuk-summary-list__value').should('include.text', 'Ghanima Atreides')

      // Pressing continue instead. Should also go back to confirm
      cy.get("a[href='/change-registry-details']").click()
      cy.get('#id_registrant_role').clear().type('Steve Atreides');
      cy.get('#id_submit').click();
      cy.checkPageTitleIncludes('Check your answers')
    })
  })
