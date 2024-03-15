import './base.cy'

describe('change registrar organisation name', () => {
    it('goes back to the answers page after the user changed the registrar', () => {
      cy.base('')
      // Change registrar organisation name
      cy.visit("registrar/?change");
      cy.get('#id_organisations_choice').type('WeRegister')

      // Back to Answers
      cy.get('#id_cancel').click();
      cy.get('.govuk-summary-list__value').should('include.text', 'registrar-1')
    })
  })
