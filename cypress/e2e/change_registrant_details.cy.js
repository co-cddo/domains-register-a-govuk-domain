import './base.cy'

describe('change registrant details', () => {
    it('correctly changes the registrant details when the users goes back to change it', () => {
      cy.goToConfirmation('')
      // Change registrant details
      cy.get("a[href='/change-registrant-details']").click()
      cy.get('#id_registrant_full_name').clear().type('Leto II Atreides');

      // Back to Answers
      cy.get('#id_back_to_answers').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'Leto II Atreides')

      // Again, but pressing Continue should take you to Registry details
      cy.get("a[href='/change-registrant-details']").click()
      cy.get('#id_registrant_full_name').clear().type('Paul Atreides');

      // Click continue
      cy.get('#id_submit').click();
      cy.get('h1').should('include.text', 'Registrant details for publishing to the registry')
    })


  })
