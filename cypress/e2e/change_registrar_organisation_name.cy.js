import './base.cy'

describe('change Organisation name', () => {
    it('organisation name', () => {
      cy.base('')
      // Change Organisation name
      cy.get(':nth-child(5) > .govuk-summary-list__row > .govuk-summary-list__actions > .govuk-link').click();
      cy.get('#id_organisations_choice').select('20i Ltd');

      // Back to Answers
      cy.get('#id_cancel').click();
      cy.get('.govuk-summary-list__value').should('include.text', '20i Ltd')
    })
  })
  